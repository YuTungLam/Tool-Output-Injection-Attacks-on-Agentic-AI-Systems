import hashlib
import json
import shutil
import subprocess
from html.parser import HTMLParser

import pytest

from agentdojo_lab import cli, html_report, runner
from agentdojo_lab.html_report import collect_run_record, export_run_html
from agentdojo_lab.runner import RunConfig, RunExecutionError, run_clean


class ReportParser(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.tags = []
        self.scripts = []
        self.active = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "script":
            self.active = {"attrs": attrs, "text": ""}
            self.scripts.append(self.active)

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = None

    def handle_data(self, data):
        if self.active is not None:
            self.active["text"] += data

    @property
    def record(self):
        return json.loads(next(s["text"] for s in self.scripts if s["attrs"].get("id") == "record"))


def minimal_run(path, *, marker="example"):
    path.mkdir()
    (path / "manifest.json").write_text(
        json.dumps({"config": {"user_tasks": ["user_task_0"]}, "notes": [marker]})
    )
    (path / "summary.json").write_text(json.dumps({"status": "failed", "error": marker}))
    return path


@pytest.fixture(scope="module")
def completed_run(tmp_path_factory):
    path = tmp_path_factory.mktemp("html-fixture") / "run"
    run_clean(RunConfig(), offline=True, output=path)
    return path


def test_runner_automatically_exports_full_offline_record(completed_run):
    parser = ReportParser((completed_run / "report.html").read_text())
    data = parser.record
    assert data["manifest"]["real_llm"] is False
    assert data["summary"]["tasks"][0]["utility"] is True
    assert len(data["events"]) == 15
    assert len(data["native"][0]["trace"]["messages"]) == 5
    assert data["audit"]["valid"] is True
    assert json.loads((completed_run / "html-report-status.json").read_text())["status"] == "generated"


def test_rebuilding_does_not_modify_experiment_sources(completed_run, tmp_path):
    sources = [
        p
        for p in completed_run.rglob("*")
        if p.is_file() and p.name not in {"report.html", "html-report-status.json"}
    ]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result = export_run_html(completed_run, output=tmp_path / "copy.html")
    assert result["event_count"] == 15
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    payload = ReportParser((tmp_path / "copy.html").read_text()).record
    for name, digest in payload["source_hashes"].items():
        assert digest == hashlib.sha256((completed_run / name).read_bytes()).hexdigest()


def test_embedded_data_is_inert_and_known_credentials_redacted(tmp_path):
    marker = '</script><b data-probe="literal">text</b>&\u2028\u2029@@NONCE@@'
    run = minimal_run(tmp_path / "run", marker=marker + " fixture-secret-value")
    export_run_html(run, redactions=("fixture-secret-value",))
    text = (run / "report.html").read_text()
    parsed = ReportParser(text)
    assert len(parsed.scripts) == 2
    assert not any("data-probe" in attrs for _, attrs in parsed.tags)
    assert "fixture-secret-value" not in text
    assert parsed.record["summary"]["error"] == marker + " [REDACTED]"
    assert r"\u003c/script\u003e" in text
    nonces = {script["attrs"]["nonce"] for script in parsed.scripts}
    assert len(nonces) == 1
    assert all("src" not in attrs for tag, attrs in parsed.tags if tag == "script")
    assert "connect-src 'none'" in text


def test_old_run_keeps_native_history_without_inventing_events(tmp_path):
    run = minimal_run(tmp_path / "old")
    (run / "native").mkdir()
    native = {"user_task_id": "user_task_0", "messages": [{"role": "assistant", "content": "saved"}]}
    (run / "native" / "trace.json").write_text(json.dumps(native))
    payload = collect_run_record(run)
    assert payload["events"] == []
    assert payload["audit"] is None
    assert payload["native"][0]["trace"] == native
    assert payload["warnings"]


def test_partial_events_preserve_saved_data_and_report_gaps(tmp_path):
    run = minimal_run(tmp_path / "partial")
    event = {"event_type": "MODEL_REQUEST", "episode_id": "attempt-1", "task_id": "task-1", "data": {}}
    (run / "events.jsonl").write_text(json.dumps(event) + '\n{"truncated":')
    payload = collect_run_record(run)
    assert payload["events"] == [event]
    assert payload["audit"]["valid"] is False
    assert any("第 2 行" in warning for warning in payload["warnings"])


def test_same_provider_id_across_episodes_remains_separate(tmp_path):
    run = minimal_run(tmp_path / "multi")
    events = [
        {
            "event_type": "TOOL_CALL_PROPOSED",
            "task_id": f"task-{i}",
            "episode_id": f"attempt-{i}",
            "tool_call_id": "provider-reused-id",
            "call_ref": f"call-{i}",
            "data": {},
        }
        for i in (1, 2)
    ]
    (run / "events.jsonl").write_text("\n".join(json.dumps(event) for event in events))
    assert collect_run_record(run)["events"] == events


@pytest.mark.parametrize("agent_fails", [False, True])
def test_export_failure_preserves_original_agent_outcome(monkeypatch, tmp_path, agent_fails):
    def fail_export(*args, **kwargs):
        raise OSError("export fixture failure")

    monkeypatch.setattr(runner, "export_run_html", fail_export)
    if agent_fails:

        def fail_client(*args):
            raise RuntimeError("original client failure")

        monkeypatch.setattr(runner, "make_offline_client", fail_client)
    run = tmp_path / "run"
    if agent_fails:
        with pytest.raises(RunExecutionError) as error:
            run_clean(RunConfig(), offline=True, output=run)
        assert str(error.value.__cause__) == "original client failure"
    else:
        assert run_clean(RunConfig(), offline=True, output=run)["task_success_count"] == 1
    saved = json.loads((run / "summary.json").read_text())
    assert saved["status"] == ("failed" if agent_fails else "completed")
    assert json.loads((run / "html-report-status.json").read_text()) == {
        "status": "failed",
        "error_type": "OSError",
    }


def test_atomic_export_keeps_previous_report_on_failure(monkeypatch, tmp_path):
    run = minimal_run(tmp_path / "run")
    (run / "report.html").write_text("previous report")
    monkeypatch.setattr(html_report.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("fixture")))
    with pytest.raises(OSError):
        export_run_html(run)
    assert (run / "report.html").read_text() == "previous report"
    assert not list(run.glob(".report-*.tmp"))


def test_sources_outside_run_are_not_embedded(tmp_path):
    run = minimal_run(tmp_path / "run")
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"unrelated": "external-fixture-value"}))
    (run / "native").mkdir()
    (run / "native" / "trace.json").symlink_to(outside)
    data = collect_run_record(run)
    assert data["native"] == []
    assert data["warnings"]
    assert "external-fixture-value" not in json.dumps(data)


def test_html_cli_exports_from_existing_run_without_llm(monkeypatch, completed_run, tmp_path, capsys):
    monkeypatch.setattr(runner, "configured_key", lambda: pytest.fail("HTML must not load credentials"))
    assert cli.main(["html", "--run", str(completed_run), "--output", str(tmp_path / "cli.html")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "generated"


def test_viewer_script_syntax(completed_run):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is optional; needed only to check viewer JavaScript syntax")
    parser = ReportParser((completed_run / "report.html").read_text())
    script = next(s["text"] for s in parser.scripts if s["attrs"].get("type") != "application/json")
    checked = subprocess.run([node, "--check"], input=script, text=True, capture_output=True)
    assert checked.returncode == 0, checked.stderr


def test_bad_report_status_does_not_turn_cli_success_into_failure(monkeypatch, tmp_path, capsys):
    (tmp_path / "html-report-status.json").write_text('{"unfinished":')
    monkeypatch.setattr(
        cli,
        "run_clean",
        lambda *args, **kwargs: {
            "status": "completed",
            "run_dir": str(tmp_path),
            "task_count": 1,
            "task_success_count": 1,
        },
    )
    assert cli.main(["smoke", "--offline"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["task_success_count"] == 1
    assert printed["html_report"]["status"] == "unavailable"


def test_viewer_pure_helpers_accept_damaged_event_fields(completed_run):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is optional for the JavaScript helper checks")
    parsed = ReportParser((completed_run / "report.html").read_text())
    script = next(s["text"] for s in parsed.scripts if s["attrs"].get("type") != "application/json")
    helpers = script.split("const taskIds=")[0]
    checks = """
const assert = require('node:assert/strict');
assert.deepEqual(asArray({}), []);
assert.equal(category({event_type: 7}), 'run');
assert.equal(eventLabel({event_type: 7}), '未知事件');
assert.equal(eventLabel({event_type: '__proto__'}), '__proto__');
assert.equal(eventLabel({event_type: 'MODEL_ERROR'}), '模型调用异常');
"""
    # Only pure helper expressions execute; no browser or DOM traversal is used.
    prelude = 'const document={getElementById:()=>({textContent:"{}"})};\n'
    result = subprocess.run([node], input=prelude + helpers + checks, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
