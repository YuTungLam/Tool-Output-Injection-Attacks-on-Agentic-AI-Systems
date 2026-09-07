import json

import httpx
import openai
import pytest

from agentdojo_lab import cli, runner
from agentdojo_lab.runner import ROOT, RunConfig, RunExecutionError, run_clean


def test_offline_run_persists_reproducible_native_results(tmp_path):
    output = tmp_path / "run"
    result = run_clean(RunConfig(), offline=True, output=output)
    assert result["status"] == "completed"
    assert result["real_llm"] is False
    assert result["task_success_count"] == 1
    assert result["usage"]["request_count"] == 2
    assert result["tasks"][0]["tool_results"] == 1
    assert result["tasks"][0]["tool_errors"] == 0
    recording = result["recording"]
    assert recording["complete"] is True
    assert recording["audit"]["valid"] is True
    assert recording["audit"]["model_requests"] == result["usage"]["request_count"]
    assert recording["audit"]["tool_proposals"] == recording["audit"]["tool_results"] == 1
    assert recording["audit"]["tool_output_exposures"] == 1
    assert json.loads((output / "events.audit.json").read_text()) == recording["audit"]
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["upstream"]["pin_matches"]
    assert len(manifest["uv_lock_sha256"]) == 64
    assert manifest["attack"] is None
    assert manifest["defense"] is None
    assert json.loads((output / "summary.json").read_text()) == result
    trace = json.loads((output / result["tasks"][0]["trace"]).read_text())
    assert [m["role"] for m in trace["messages"]] == ["system", "user", "assistant", "tool", "assistant"]
    with pytest.raises(FileExistsError):
        run_clean(RunConfig(), offline=True, output=output)


def test_recording_control_preserves_native_result(tmp_path):
    enabled = run_clean(RunConfig(), offline=True, output=tmp_path / "enabled")
    disabled = run_clean(RunConfig(record_events=False), offline=True, output=tmp_path / "disabled")
    assert disabled["recording"] == {"enabled": False}
    assert not (tmp_path / "disabled" / "events.jsonl").exists()
    assert enabled["tasks"] == disabled["tasks"]
    assert enabled["usage"] == disabled["usage"]
    for result in (enabled, disabled):
        result["native_messages"] = json.loads(
            (
                tmp_path / ("enabled" if result is enabled else "disabled") / result["tasks"][0]["trace"]
            ).read_text()
        )["messages"]
    assert enabled["native_messages"] == disabled["native_messages"]


def test_missing_key_stops_before_output_or_network(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "configured_key", lambda: "")
    output = tmp_path / "run"
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        run_clean(RunConfig(), output=output)
    assert not output.exists()


def test_failure_is_recorded_and_not_retried(monkeypatch, tmp_path):
    calls = []

    def fail_client(*args):
        calls.append(True)
        raise RuntimeError("fixture unavailable")

    monkeypatch.setattr(runner, "make_offline_client", fail_client)
    output = tmp_path / "run"
    with pytest.raises(RunExecutionError, match="summary.json") as failure:
        run_clean(RunConfig(), offline=True, output=output)
    assert failure.value.summary_path == output / "summary.json"
    result = json.loads((output / "summary.json").read_text())
    assert result["status"] == "failed"
    assert result["error_type"] == "RuntimeError"
    assert "task_success_rate" not in result
    assert len(calls) == 1


def test_invalid_task_is_rejected_before_client_creation(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "configured_key", lambda: pytest.fail("should validate task first"))
    with pytest.raises(ValueError, match="Unknown task"):
        run_clean(RunConfig(user_tasks=["missing_task"]), output=tmp_path / "run")


def test_upstream_caught_api_error_is_not_an_evaluated_task(monkeypatch, tmp_path):
    def failing_client(*args):
        transport = httpx.MockTransport(
            lambda request: httpx.Response(
                400,
                json={"error": {"message": "Context too long", "code": "context_length_exceeded"}},
            )
        )
        return openai.OpenAI(
            api_key="offline-fixture",
            base_url="https://fixture.invalid/v1",
            max_retries=0,
            http_client=httpx.Client(transport=transport),
        )

    monkeypatch.setattr(runner, "make_offline_client", failing_client)
    result = run_clean(RunConfig(), offline=True, output=tmp_path / "run")
    assert result["status"] == "completed_with_issues"
    assert result["error_task_count"] == 1
    assert result["evaluable_task_count"] == 0
    assert result["evaluable_success_rate"] is None
    assert result["tasks"][0]["status"] == "error"
    assert result["usage"]["request_count"] == 1
    assert result["recording"]["complete"] is True
    assert result["recording"]["audit"]["valid"] is True


def test_cli_model_and_tasks_override_config(monkeypatch, capsys):
    configs = []

    def capture(config, **kwargs):
        configs.append(config)
        return {"task_count": 1, "task_success_count": 1}

    monkeypatch.setattr(cli, "run_clean", capture)
    result = cli.main(
        [
            "run",
            "--config",
            str(ROOT / "configs/groq.toml"),
            "--model",
            "example-other-model",
            "--task",
            "user_task_1",
        ]
    )
    assert result == 0
    assert configs[0].model == "example-other-model"
    assert configs[0].user_tasks == ["user_task_1"]
    assert configs[0].reasoning_effort is None
    assert "task_success_count" in capsys.readouterr().out


@pytest.mark.parametrize(
    "data",
    [
        {"user_tasks": []},
        {"user_tasks": ["user_task_0", "user_task_0"]},
        {"attack": "unsupported"},
        {"max_completion_tokens": 0},
    ],
)
def test_config_rejects_invalid_or_unknown_options(data):
    with pytest.raises(ValueError):
        RunConfig.model_validate(data)
