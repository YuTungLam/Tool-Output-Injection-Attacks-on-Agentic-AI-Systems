"""Self-contained, offline HTML records of individual experiments.

Data stays inert: JSON is escaped for the HTML parser and the viewer uses text
nodes rather than interpreting recorded model/tool content as markup or code.
"""

import hashlib
import json
import os
import secrets
import tempfile
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

from agentdojo_lab.inspection import inspect_events


def collect_run_record(run_dir: Path, *, summary: dict | None = None) -> dict:
    run_dir = run_dir.expanduser().resolve()
    if not run_dir.is_dir():
        raise ValueError(f"Run directory does not exist: {run_dir}")
    warnings = []
    hashes = {}

    def read_json(path, *, required=False):
        relative = str(path.relative_to(run_dir))
        try:
            if not path.resolve().is_relative_to(run_dir):
                raise ValueError("source outside run directory")
            raw = path.read_bytes()
            hashes[relative] = hashlib.sha256(raw).hexdigest()
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("expected JSON object")
            return value
        except (OSError, ValueError, UnicodeError) as exc:
            if required:
                raise ValueError(f"Cannot read {relative} ({type(exc).__name__}).") from exc
            warnings.append(f"无法读取 {relative}（{type(exc).__name__}）")
            return None

    manifest = read_json(run_dir / "manifest.json", required=True)
    stored_summary = read_json(run_dir / "summary.json", required=summary is None)
    selected_summary = dict(summary if summary is not None else stored_summary)
    # HTML export status is stored outside the immutable experimental outcome.
    events = []
    event_path = run_dir / "events.jsonl"
    audit = None
    if event_path.exists():
        if not event_path.resolve().is_relative_to(run_dir):
            warnings.append("events.jsonl 指向实验目录以外，未纳入报告")
        else:
            raw = event_path.read_bytes()
            hashes["events.jsonl"] = hashlib.sha256(raw).hexdigest()
            for index, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError("expected event object")
                    events.append(event)
                except ValueError:
                    warnings.append(f"events.jsonl 第 {index} 行无法解析，原始文件仍保留")
            audit = inspect_events(event_path)
    native = []
    for path in sorted((run_dir / "native").rglob("*.json")):
        trace = read_json(path)
        if trace is not None:
            native.append({"source": str(path.relative_to(run_dir)), "trace": trace})
    if not events:
        warnings.append("本次实验没有可用的在线事件；原生对话历史单独显示，不推断事件时间或来源关系。")
    return {
        "schema_version": 1,
        "run_id": run_dir.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest,
        "summary": selected_summary,
        "events": events,
        "audit": audit,
        "native": native,
        "warnings": warnings,
        "source_hashes": hashes,
    }


def _escaped_json(value):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False)
    for char, escaped in (
        ("&", r"\u0026"),
        ("<", r"\u003c"),
        (">", r"\u003e"),
        ("\u2028", r"\u2028"),
        ("\u2029", r"\u2029"),
    ):
        text = text.replace(char, escaped)
    return text


def _redact(value, known):
    if isinstance(value, str):
        for secret in known:
            value = value.replace(secret, "[REDACTED]")
        return value
    if isinstance(value, dict):
        return {_redact(key, known): _redact(item, known) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, known) for item in value]
    return value


def export_run_html(
    run_dir: Path,
    *,
    output: Path | None = None,
    summary: dict | None = None,
    redactions: tuple[str, ...] = (),
) -> dict:
    record = collect_run_record(run_dir, summary=summary)
    record = _redact(record, sorted({s for s in redactions if s}, key=len, reverse=True))
    template = files("agentdojo_lab").joinpath("templates/run_report.html").read_text(encoding="utf-8")
    nonce = secrets.token_urlsafe(24)
    html = template.replace("@@NONCE@@", nonce).replace("@@RECORD@@", _escaped_json(record))
    destination = (output or (run_dir / "report.html")).expanduser().resolve()
    if destination.suffix.lower() != ".html":
        raise ValueError("HTML report output must end in .html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Rebuilding the derived report is intentional; raw logs are never rewritten.
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=destination.parent, prefix=".report-", suffix=".tmp", delete=False
    ) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(html)
            stream.flush()
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
    return {
        "status": "generated",
        "path": str(destination),
        "event_count": len(record["events"]),
        "native_trace_count": len(record["native"]),
        "warning_count": len(record["warnings"]),
    }
