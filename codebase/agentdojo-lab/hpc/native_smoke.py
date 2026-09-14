"""At most four native clean-agent requests against an already checked local Scout server.

Run with the lab's Python 3.12 inside the serving allocation. This wrapper does
not start a server, download a model, change a frozen experiment, or run an attack.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import signal
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import httpx
import smoke

from agentdojo_lab import runner
from agentdojo_lab.groq_adapter import GroqLLM
from agentdojo_lab.inspection import inspect_events
from agentdojo_lab.providers import EndpointSettings
from agentdojo_lab.runner import ROOT, RunConfig, load_config, run_clean

PROTOCOL = "nesi-scout-native-clean-smoke-v1"
REQUEST_LIMIT = 4


class NativeSmokeBudgetExceeded(RuntimeError):
    """The next native completion would exceed the four-attempt smoke budget."""


class BudgetedSmokeLLM(GroqLLM):
    """One shared counter across native retries; denied requests never enter the SDK."""

    def query(self, *args, **kwargs):
        if self.stats["request_count"] >= REQUEST_LIMIT:
            raise NativeSmokeBudgetExceeded("Native smoke primary request budget exhausted")
        return super().query(*args, **kwargs)


def file_receipt(path: Path) -> dict:
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_serving_inputs(path: Path, base_url: str) -> dict:
    """Bind this client to the passed synthetic smoke and recorded server command."""
    preflight = json.loads(path.read_text())
    if preflight.get("slurm_job_id") != os.environ.get("SLURM_JOB_ID"):
        raise ValueError("Serving receipt belongs to a different Slurm allocation")
    if preflight.get("model", {}).get("model_id") != "meta-llama/Llama-4-Scout-17B-16E-Instruct":
        raise ValueError("Serving receipt does not select Scout")
    synthetic_path = path.parent / "smoke.json"
    synthetic = json.loads(synthetic_path.read_text())
    if synthetic.get("status") != "passed" or synthetic.get("requests_started") != 4:
        raise ValueError("Four successful synthetic requests are required before the native phase")
    requests = synthetic.get("requests", [])
    if len(requests) != 4 or any(
        row.get("status") != "passed" or row.get("request", {}).get("model") != smoke.MODEL
        or row.get("response", {}).get("model") != smoke.MODEL for row in requests
    ):
        raise ValueError("Synthetic smoke model or request status differs from native smoke")
    command_path = path.parent / "server-command.txt"
    command = shlex.split(command_path.read_text())

    def value(flag):
        try:
            return command[command.index(flag) + 1]
        except (ValueError, IndexError):
            raise ValueError("Serving command lacks a required smoke flag") from None

    if (value("--served-model-name") != smoke.MODEL or value("--host") != "127.0.0.1"
            or int(value("--port")) != urlsplit(base_url).port or value("--max-model-len") != "8192"):
        raise ValueError("Recorded serving model/endpoint/context differs from native smoke")
    receipts = {
        "preflight": file_receipt(path),
        "synthetic_smoke": file_receipt(synthetic_path),
        "server_command": file_receipt(command_path),
        "model": preflight["model"],
        "template": preflight.get("template"),
        "container": preflight.get("container"),
    }
    runtime_path = path.parent / "container-runtime.json"
    if runtime_path.is_file():
        receipts["container_runtime"] = file_receipt(runtime_path)
    return receipts


def config_for(base_url: str) -> RunConfig:
    data = load_config(ROOT / "configs/local_scout.toml").model_dump()
    data.update(
        provider="openai_compatible", model=smoke.MODEL, base_url=smoke.local_url(base_url),
        api_key_env="LOCAL_LLM_API_KEY", user_tasks=["user_task_0"], temperature=0.0,
        max_completion_tokens=2048, max_tool_rounds=4, request_timeout_seconds=180.0,
        online_provenance=False, online_causal_audit=False, causal_endpoint=None, record_events=True,
        provenance_policy=None, lineage_namespace=None, canary_enabled=False,
        semantic_model=None, semantic_revision=None, reasoning_effort=None, pacing_tokens_per_minute=None,
    )
    return RunConfig.model_validate(data)


def successful_round_trips(events_path: Path) -> list[dict]:
    """Require a successful runtime return, native result, and its later model exposure."""
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    returned = {
        event["event_id"]: event for event in events
        if event["event_type"] == "TOOL_RUNTIME_RETURNED"
        and event["data"].get("error") is None
        and event["data"].get("raised_exception_type") is None
    }
    results = {}
    for event in events:
        if event["event_type"] != "TOOL_RESULT" or event["data"].get("runtime_entered") is not True:
            continue
        if event["data"].get("message", {}).get("error") is not None:
            continue
        for parent in event.get("parent_event_ids", []):
            if parent in returned and returned[parent].get("call_ref") == event.get("call_ref"):
                results[event["event_id"]] = parent
    return [
        {"runtime_return_event_id": results[event["data"]["source_result_event_id"]],
         "result_event_id": event["data"]["source_result_event_id"], "exposure_event_id": event["event_id"]}
        for event in events if event["event_type"] == "TOOL_OUTPUT_EXPOSED"
        and event["data"].get("source_result_event_id") in results
    ]


def run_native(*, base_url: str, serving_receipt: Path, output: Path, run_dir: Path) -> dict:
    receipt = {
        "protocol": PROTOCOL, "status": "failed", "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "run_dir": str(run_dir.resolve()), "wrapper": file_receipt(Path(__file__)),
        "native_requests_started": 0,
        "limits": {"primary_sdk_attempts": REQUEST_LIMIT, "completion_tokens_per_request": 2048,
                   "request_timeout_seconds": 180, "context_tokens": 8192, "causal_requests": 0,
                   "combined_synthetic_and_native_generation_cap": 8},
        "scope": "one native clean task; integration/utility smoke, not an attack or attribution result",
        "budget_enforcement": "process-local scoped LLM subclass; blocks before SDK call; spans native retries",
    }
    native_started = False
    # Reserve a new receipt before validation or inference. Failed starts remain visible.
    with output.open("x", encoding="utf-8") as stream:
        try:
            if not os.environ.get("SLURM_JOB_ID"):
                raise ValueError("Native smoke requires the serving Slurm allocation")
            base_url = smoke.local_url(base_url)
            receipt["serving"] = verify_serving_inputs(serving_receipt, base_url)
            if run_dir.exists():
                raise FileExistsError("Native smoke requires a fresh run directory")
            config = config_for(base_url)
            receipt["config"] = config.model_dump()
            config.primary_endpoint().require_key()
            # The native SDK must not inherit a proxy or follow a redirect away
            # from the literal loopback endpoint chosen for this allocation.
            def local_client(endpoint, *, key: str, timeout: float):
                if endpoint != config.primary_endpoint():
                    raise ValueError("Native smoke attempted an unexpected endpoint")
                return runner.openai.OpenAI(
                    api_key=key, base_url=base_url, max_retries=0, timeout=timeout,
                    http_client=httpx.Client(trust_env=False, follow_redirects=False),
                )

            with patch.object(runner, "GroqLLM", BudgetedSmokeLLM), patch.object(
                EndpointSettings, "client", local_client
            ):
                native_started = True
                result = run_clean(config, output=run_dir)
            audit = inspect_events(run_dir / "events.jsonl")
            round_trips = successful_round_trips(run_dir / "events.jsonl")
            html = json.loads((run_dir / "html-report-status.json").read_text())
            observed = result.get("usage", {}).get("request_count")
            checks = {
                "completed": result.get("status") == "completed",
                "native_utility_passed": result.get("task_count") == result.get("task_success_count") == 1,
                "one_evaluable_task": result.get("evaluable_task_count") == 1,
                "request_cap_respected": type(observed) is int and 1 <= observed <= REQUEST_LIMIT,
                "recording_complete": result.get("recording", {}).get("complete") is True,
                "event_links_valid": audit.get("valid") is True,
                "native_tool_round_trip": bool(round_trips),
                "html_exported": html.get("status") == "generated" and (run_dir / "report.html").is_file(),
                "no_online_auditors": result.get("online_causal_audit", {}).get("enabled") is False,
            }
            receipt.update(checks=checks, event_audit=audit, native_summary=result,
                           native_tool_round_trips=round_trips,
                           native_requests_started=observed)
            if all(checks.values()):
                receipt["status"] = "passed"
        except BaseException as error:
            # Error type plus retained native artifacts are sufficient; avoid
            # printing API errors or environment values into scheduler output.
            receipt["error_type"] = type(error).__name__
            summary_path = run_dir / "summary.json"
            if native_started and summary_path.is_file():
                result = json.loads(summary_path.read_text())
                receipt["native_summary"] = result
                receipt["native_requests_started"] = result.get("usage", {}).get("request_count", 0)
        finally:
            receipt["artifacts"] = {
                name: file_receipt(run_dir / name)
                for name in ("manifest.json", "summary.json", "events.jsonl", "events.audit.json", "report.html")
                if native_started and (run_dir / name).is_file()
            }
            encoded = json.dumps(receipt, ensure_ascii=False, indent=2)
            secret = os.environ.get("LOCAL_LLM_API_KEY", "")
            stream.write((encoded.replace(secret, "[REDACTED]") if secret else encoded) + "\n")
    return receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--serving-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    def interrupted(_signum, _frame):
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, interrupted)
    try:
        result = run_native(base_url=args.base_url, serving_receipt=args.serving_receipt,
                            output=args.output, run_dir=args.run_dir)
    except (OSError, ValueError):
        print("Native Scout smoke could not reserve its receipt; existing outputs are unchanged.")
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous)
    print("Native Scout smoke " + result["status"] + "; inspect its retained receipt.")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
