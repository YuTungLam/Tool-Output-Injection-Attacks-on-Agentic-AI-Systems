"""Offline checks for the separately named smoke-plus-Case-A batch protocol."""

import hashlib
import json
from pathlib import Path

import case_a_batch
import pytest

HPC = Path(__file__).resolve().parent


def frozen_submission(tmp_path):
    frozen = tmp_path / "frozen-hpc"
    frozen.mkdir(exist_ok=True)
    for name in sorted(case_a_batch.MANIFEST_PAYLOAD_NAMES):
        path = frozen / name
        if not path.exists():
            path.write_text(f"# frozen {name}\n")
    executed = tmp_path / "slurm-spooled-case-a"
    executed.write_bytes((frozen / "scout-smoke-case-a.sbatch").read_bytes())
    manifest = frozen / "submission-sha256.txt"
    manifest.write_text(
        "".join(
            f"{case_a_batch.receipt(frozen / name)['sha256']}  {name}\n"
            for name in sorted(case_a_batch.MANIFEST_PAYLOAD_NAMES)
        )
    )
    site = tmp_path / "case-a-site.env"
    site.write_text("# private site fixture\n")
    helpers = [frozen / name for name in sorted(case_a_batch.EXPECTED_HELPER_NAMES)]
    return {
        "runner": frozen / "run_case_a_scout.py",
        "site": site,
        "manifest": manifest,
        "executed": executed,
        "canonical": frozen / "scout-smoke-case-a.sbatch",
        "helpers": helpers,
    }


def validate_submission_args(submission):
    return {
        "site_path": submission["site"],
        "site_sha256": case_a_batch.receipt(submission["site"])["sha256"],
        "manifest_path": submission["manifest"],
        "manifest_sha256": case_a_batch.receipt(submission["manifest"])["sha256"],
        "executed_wrapper_path": submission["executed"],
        "canonical_wrapper_path": submission["canonical"],
        "helper_paths": submission["helpers"],
    }


def write_wrapper_checksums(path, submission):
    inputs = {item.resolve() for item in [submission["executed"], submission["site"], *submission["helpers"]]}
    path.write_text("".join(f"{case_a_batch.receipt(item)['sha256']}  {item}\n" for item in sorted(inputs)))


def prepared_plan(**changes):
    plan = {
        "protocol": "scout-case-a-recipient-v1",
        "limits": {
            "primary_sdk_attempts_total": 16,
            "online_auditor_requests": 0,
            "sdk_max_retries": 0,
        },
        "config": {
            "provider": "openai_compatible",
            "base_url": "http://127.0.0.1:8000/v1",
        },
        "source_hashes": {},
    }
    plan.update(changes)
    return plan


def test_validate_requires_pristine_separate_paths_and_bound_plan(tmp_path):
    case = tmp_path / "case"
    case.mkdir()
    (case / "plan.json").write_text("{}")
    (case / "preparation.json").write_text("{}")
    smoke = tmp_path / "smoke"
    seen = []
    result = case_a_batch.validate_prepared_case(
        case, smoke, verifier=lambda path: seen.append(path) or prepared_plan()
    )
    assert result["limits"]["primary_sdk_attempts_total"] == 16
    assert seen == [case.resolve()]

    (case / "execution.json").write_text("prior output")
    with pytest.raises(ValueError, match="only plan"):
        case_a_batch.validate_prepared_case(case, smoke, verifier=lambda _path: prepared_plan())
    assert (case / "execution.json").read_text() == "prior output"


def test_validate_rejects_source_drift_existing_smoke_and_remote_plan(tmp_path):
    case = tmp_path / "case"
    case.mkdir()
    (case / "plan.json").write_text("{}")
    (case / "preparation.json").write_text("{}")
    smoke = tmp_path / "smoke"
    with pytest.raises(ValueError, match="source drift"):
        case_a_batch.validate_prepared_case(
            case,
            smoke,
            verifier=lambda _path: (_ for _ in ()).throw(ValueError("source drift")),
        )
    remote = prepared_plan(
        config={"provider": "openai_compatible", "base_url": "https://example.com/v1"}
    )
    with pytest.raises(ValueError, match="endpoint bounds"):
        case_a_batch.validate_prepared_case(case, smoke, verifier=lambda _path: remote)
    smoke.mkdir()
    with pytest.raises(FileExistsError, match="fresh"):
        case_a_batch.validate_prepared_case(case, smoke, verifier=lambda _path: prepared_plan())
    with pytest.raises(ValueError, match="absolute"):
        case_a_batch.validate_prepared_case(
            Path("relative-case"), Path("relative-smoke"), verifier=lambda _path: prepared_plan()
        )


def test_pre_smoke_validation_binds_runner_to_plan_source_hash(tmp_path):
    case = tmp_path / "case"
    case.mkdir()
    (case / "plan.json").write_text("{}")
    (case / "preparation.json").write_text("{}")
    submission = frozen_submission(tmp_path)
    runner = submission["runner"]
    plan = prepared_plan(
        source_hashes={"scripts/run_case_a_scout.py": case_a_batch.receipt(runner)["sha256"]}
    )
    output = tmp_path / "pre-smoke.json"
    result = case_a_batch.validate_before_smoke(
        output,
        case,
        tmp_path / "smoke",
        runner,
        verifier=lambda _path: plan,
        **validate_submission_args(submission),
    )
    assert result["runner"] == case_a_batch.receipt(runner)
    runner.write_text("# drifted runner\n")
    with pytest.raises(ValueError, match="source hash"):
        case_a_batch.validate_before_smoke(
            tmp_path / "other.json",
            case,
            tmp_path / "smoke",
            runner,
            verifier=lambda _path: plan,
            **validate_submission_args(submission),
        )


@pytest.mark.parametrize(
    "mutation",
    ["site_hash", "manifest_hash", "spooled_wrapper", "manifest_entry", "missing_helper"],
)
def test_pre_smoke_rejects_unbound_submission_inputs(tmp_path, mutation):
    case = tmp_path / "case"
    case.mkdir()
    submission = frozen_submission(tmp_path)
    runner = submission["runner"]
    plan = prepared_plan(
        source_hashes={"scripts/run_case_a_scout.py": case_a_batch.receipt(runner)["sha256"]}
    )
    (case / "plan.json").write_text(json.dumps(plan))
    (case / "preparation.json").write_text("{}")
    arguments = validate_submission_args(submission)
    if mutation == "site_hash":
        arguments["site_sha256"] = "0" * 64
    elif mutation == "manifest_hash":
        arguments["manifest_sha256"] = "0" * 64
    elif mutation == "spooled_wrapper":
        submission["executed"].write_text("# changed in spool\n")
    elif mutation == "manifest_entry":
        lines = submission["manifest"].read_text().splitlines()
        submission["manifest"].write_text("\n".join(lines[:-1]) + "\n")
        arguments["manifest_sha256"] = case_a_batch.receipt(submission["manifest"])["sha256"]
    else:
        arguments["helper_paths"] = arguments["helper_paths"][:-1]
    with pytest.raises(ValueError):
        case_a_batch.validate_before_smoke(
            tmp_path / "pre-smoke.json",
            case,
            tmp_path / "smoke",
            runner,
            verifier=lambda _path: plan,
            **arguments,
        )


@pytest.mark.parametrize(
    ("raw", "seconds"),
    [("01:05:00", 3900), ("59:00", 3540), ("0-02:00:00", 7200), ("1-00:00:00", 86400)],
)
def test_parse_slurm_duration(raw, seconds):
    assert case_a_batch.parse_slurm_duration(raw) == seconds


@pytest.mark.parametrize("raw", ["", " 01:00", "01:60", "x", "1-24:00:00"])
def test_parse_slurm_duration_rejects_malformed_values(raw):
    with pytest.raises(ValueError):
        case_a_batch.parse_slurm_duration(raw)


def reserve(tmp_path, **changes):
    submission = frozen_submission(tmp_path)
    case = tmp_path / "case"
    case.mkdir(exist_ok=True)
    smoke_dir = tmp_path / "smoke"
    runner = submission["runner"]
    plan = prepared_plan(
        source_hashes={"scripts/run_case_a_scout.py": case_a_batch.receipt(runner)["sha256"]}
    )
    if not (case / "plan.json").exists():
        (case / "plan.json").write_text(json.dumps(plan))
        (case / "preparation.json").write_text("{}")
    pre_smoke = Path(str(smoke_dir) + ".case-a-pre-smoke.json")
    if not pre_smoke.exists():
        case_a_batch.validate_before_smoke(
            pre_smoke,
            case,
            smoke_dir,
            runner,
            verifier=lambda _path: plan,
            **validate_submission_args(submission),
        )
    smoke_dir.mkdir(exist_ok=True)
    wrapper_checksums = smoke_dir / "case-a-wrapper-sha256.txt"
    if not wrapper_checksums.exists():
        write_wrapper_checksums(wrapper_checksums, submission)
    values = {
        "job_id": "42",
        "reported_job_id": "42",
        "remaining": "01:05:00",
        "time_limit": "02:00:00",
        "case_dir": case,
        "server_pid": 123,
        "wrapper_sha256_path": wrapper_checksums,
        "pre_smoke_path": pre_smoke,
        "runner_path": runner,
        "helper_paths": submission["helpers"],
    }
    values.update(changes)
    return case_a_batch.reserve_phase(smoke_dir / "case-a-phase.json", **values)


def test_phase_gate_reserves_at_boundary_hashes_helpers_and_is_exclusive(tmp_path):
    result = reserve(tmp_path)
    assert result["status"] == "reserved_before_case_calls"
    assert result["time_decision"]["remaining_seconds"] == 3900
    assert result["limits"]["total_generation_requests"] == 24
    assert set(result["helpers"]) == case_a_batch.EXPECTED_HELPER_NAMES
    assert result["wrapper_checksums"]["sha256"]
    before = (tmp_path / "smoke" / "case-a-phase.json").read_bytes()
    with pytest.raises(FileExistsError):
        reserve(tmp_path)
    assert (tmp_path / "smoke" / "case-a-phase.json").read_bytes() == before


@pytest.mark.parametrize(
    ("changes", "status"),
    [
        ({"remaining": "01:04:59"}, "unstarted_insufficient_remaining_time"),
        ({"time_limit": "02:00:01"}, "unstarted_walltime_limit_exceeded"),
        ({"reported_job_id": "43"}, "unstarted_invalid_current_job_time_evidence"),
        ({"remaining": "INVALID"}, "unstarted_invalid_current_job_time_evidence"),
        ({"remaining": "02:00:01"}, "unstarted_invalid_current_job_time_evidence"),
        ({"time_limit": "00:00:00"}, "unstarted_invalid_current_job_time_evidence"),
    ],
)
def test_phase_gate_fails_closed_with_terminal_reason(tmp_path, changes, status):
    result = reserve(tmp_path, **changes)
    assert result["status"] == status
    assert result["slurm_job_id"] == "42"
    assert result["limits"]["case_command_timeout_seconds"] == 3600


class Response:
    def __init__(self, url, status, body):
        self.url = url
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _limit):
        return self.body

    def geturl(self):
        return self.url


class Opener:
    def __init__(self):
        self.authorizations = []

    def open(self, request, timeout):
        assert timeout == 10
        authorization = request.get_header("Authorization")
        self.authorizations.append(authorization)
        if authorization == "Bearer local-key":
            body = json.dumps({"data": [{"id": "llama-4-scout-local"}]}).encode()
            return Response(request.full_url, 200, body)
        return Response(request.full_url, 401, b'{"error":"unauthorized"}')


def test_server_check_requires_live_literal_loopback_and_preserves_receipt(tmp_path, monkeypatch):
    monkeypatch.setenv("SLURM_JOB_ID", "42")
    monkeypatch.setenv("SCOUT_SERVER_PID", "123")
    identity = {
        "server_process": {"pid": 123, "start_ticks": 456},
        "allocation_process_scope": {"cgroup_sha256": "fixture"},
        "scheduler": {"reported_job_id": "42", "state": "RUNNING"},
    }
    opener = Opener()
    output = tmp_path / "server.json"
    result = case_a_batch.check_server(
        output,
        base_url="http://127.0.0.1:8000/v1",
        key="local-key",
        server_pid=123,
        job_id="42",
        opener=opener,
        identity_probe=lambda _pid, _job: identity,
    )
    assert result["status"] == "passed"
    assert result["models_auth"]["generation_requests_started"] == 0
    assert result["models_auth"]["checks"]["missing_key"]["rejected"] is True
    assert result["models_auth"]["checks"]["wrong_key"]["rejected"] is True
    assert opener.authorizations == [
        "Bearer local-key",
        None,
        "Bearer case-a-intentionally-wrong-key",
    ]
    assert "local-key" not in output.read_text()
    before = output.read_bytes()
    with pytest.raises(ValueError, match="literal loopback"):
        case_a_batch.check_server(
            tmp_path / "remote.json",
            base_url="http://localhost:8000/v1",
            key="local-key",
            server_pid=123,
            job_id="42",
        )
    with pytest.raises(FileExistsError):
        case_a_batch.check_server(
            output,
            base_url="http://127.0.0.1:8000/v1",
            key="local-key",
            server_pid=123,
            job_id="42",
            opener=opener,
            identity_probe=lambda _pid, _job: identity,
        )
    assert output.read_bytes() == before


@pytest.mark.parametrize(
    ("job", "pid"),
    [("forged-job", "123"), ("42", "999"), ("42", None)],
)
def test_server_check_rejects_forged_allocation_or_pid(tmp_path, monkeypatch, job, pid):
    monkeypatch.setenv("SLURM_JOB_ID", job)
    if pid is None:
        monkeypatch.delenv("SCOUT_SERVER_PID", raising=False)
    else:
        monkeypatch.setenv("SCOUT_SERVER_PID", pid)
    output = tmp_path / f"server-{job}-{pid}.json"
    result = case_a_batch.check_server(
        output,
        base_url="http://127.0.0.1:8000/v1",
        key="local-key",
        server_pid=123,
        job_id="42",
        auth_probe=lambda *_args: (_ for _ in ()).throw(
            AssertionError("authentication probe must not run")
        ),
        identity_probe=lambda *_args: (_ for _ in ()).throw(
            AssertionError("identity probe must not run")
        ),
    )
    assert result["status"] == "failed"
    assert result["error_type"] == "ValueError"


def completion_fixture(
    tmp_path,
    *,
    native_count=2,
    case_counts=(2, 3),
    wrapper_exit=0,
    native_job_id="42",
    phase_remaining="01:05:00",
):
    reserve(tmp_path, remaining=phase_remaining)
    smoke_dir = tmp_path / "smoke"
    case_dir = tmp_path / "case"
    phase = smoke_dir / "case-a-phase.json"
    runner = tmp_path / "frozen-hpc" / "run_case_a_scout.py"
    pre_smoke = Path(str(smoke_dir) + ".case-a-pre-smoke.json")
    plan_path = case_dir / "plan.json"
    plan = json.loads(plan_path.read_text())
    plan_receipt = case_a_batch.receipt(plan_path)
    binding = {
        "status": "bound_before_case_calls",
        "slurm_job_id": "42",
        "evidence": {"fixture": True},
    }

    def validate_binding(path, base_url):
        assert path == smoke_dir / "preflight.json"
        assert base_url == "http://127.0.0.1:8000/v1"
        return binding

    paths = {
        "phase_path": phase,
        "pre_smoke_path": pre_smoke,
        "runner_path": runner,
        "preflight_path": smoke_dir / "preflight.json",
        "smoke_path": smoke_dir / "smoke.json",
        "native_path": smoke_dir / "native-smoke.json",
        "case_summary_path": case_dir / "case-summary.json",
        "case_plan_path": plan_path,
        "execution_path": case_dir / "execution.json",
        "wrapper_exit_path": smoke_dir / "case-a-wrapper-exit-code.txt",
        "wrapper_sha256_path": smoke_dir / "case-a-wrapper-sha256.txt",
        "server_check_path": smoke_dir / "case-a-server-check.json",
        "cleanup_path": smoke_dir / "case-a-cleanup.json",
        "binding_validator": validate_binding,
    }
    paths["preflight_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.SMOKE_PROTOCOL,
                "slurm_job_id": "42",
                "limits": case_a_batch.fixed_preflight_limits()[0],
                "enclosing_case_a_limits": case_a_batch.fixed_preflight_limits()[1],
            }
        )
    )
    paths["smoke_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.SMOKE_PROTOCOL,
                "status": "passed",
                "requests_started": 4,
            }
        )
    )
    paths["native_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.NATIVE_PROTOCOL,
                "status": "passed",
                "slurm_job_id": native_job_id,
                "native_requests_started": native_count,
                "checks": {"no_online_auditors": True},
            }
        )
    )
    paths["execution_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.CASE_PROTOCOL,
                "status": "execution_reserved_before_workers",
                "plan": plan_receipt,
                "serving": binding,
            }
        )
    )
    slots = []
    for condition, count in zip(("clean", "attacked"), case_counts, strict=True):
        terminal = {
            "protocol": case_a_batch.CASE_PROTOCOL,
            "condition": condition,
            "status": "completed",
            "plan": plan_receipt,
        }
        (case_dir / f"{condition}-terminal.json").write_text(json.dumps(terminal))
        slot_dir = case_dir / condition
        slot_dir.mkdir()
        (slot_dir / "sdk-attempts.jsonl").write_text(
            "".join(json.dumps({"sdk_attempt": index}) + "\n" for index in range(1, count + 1))
        )
        slots.append(
            {
                "slot_id": condition,
                "status": "terminal",
                "returncode": 0,
                "terminal": terminal,
                "reserved_sdk_attempts": count,
            }
        )
    paths["case_summary_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.CASE_PROTOCOL,
                "status": "all_slots_terminal",
                "plan": plan_receipt,
                "reserved_sdk_attempts": sum(case_counts),
                "slots": slots,
            }
        )
    )
    paths["wrapper_exit_path"].write_text(str(wrapper_exit) + "\n")
    paths["server_check_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.PROTOCOL,
                "status": "passed",
                "slurm_job_id": "42",
                "endpoint": plan["config"]["base_url"],
                "server_pid": 123,
            }
        )
    )
    paths["cleanup_path"].write_text(
        json.dumps(
            {
                "protocol": case_a_batch.PROTOCOL,
                "status": "server_stopped",
                "slurm_job_id": "42",
                "server_pid": 123,
                "case_process": {
                    "pid": 456 if phase_remaining == "01:05:00" else 0,
                    "stopped": True,
                },
            }
        )
    )
    return paths


def test_final_receipt_accounts_for_requests_cleanup_and_separate_outcome(tmp_path):
    paths = completion_fixture(tmp_path)
    output = paths["smoke_path"].parent / "case-a-batch-summary.json"
    result = case_a_batch.finalize(output, **paths)
    assert result["status"] == "complete_all_slots_terminal"
    assert result["framework_status"] == "case_runner_all_slots_terminal"
    assert result["wrapper_exit_code"] == 0
    assert result["requests"] == {
        "synthetic": 4,
        "native": 2,
        "case": 5,
        "total": 11,
        "limit": 24,
    }
    assert result["scientific_outcome"]["case_summary"]["sha256"]
    before = output.read_bytes()
    with pytest.raises(FileExistsError):
        case_a_batch.finalize(output, **paths)
    assert output.read_bytes() == before


@pytest.mark.parametrize(
    "values",
    [
        {"native_count": 5},
        {"case_counts": (8, 9)},
        {"wrapper_exit": 124},
        {"native_job_id": "different-job"},
    ],
)
def test_final_receipt_refuses_request_or_exit_bound_violations(tmp_path, values):
    paths = completion_fixture(tmp_path, **values)
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "incomplete"
    assert result["error_type"] == "ValueError"


def test_unstarted_terminal_preserves_smoke_counts_and_cleanup(tmp_path):
    paths = completion_fixture(tmp_path, phase_remaining="01:04:59", wrapper_exit=3)
    paths["case_summary_path"].unlink()
    paths["server_check_path"].unlink()
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "terminal_case_unstarted"
    assert result["requests"]["case"] == 0
    assert result["scientific_outcome"] == {
        "case_started": False,
        "reason": "unstarted_insufficient_remaining_time",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_status",
        "runner_drift",
        "plan_drift",
        "pre_smoke_drift",
        "native_job",
        "preflight_limits",
        "cleanup_path",
        "status_time_mismatch",
        "parsed_time_mismatch",
        "phase_helpers",
        "phase_limits",
        "wrapper_checksums",
        "cleanup_server_pid",
        "cleanup_case_pid",
    ],
)
def test_unstarted_terminal_rejects_mutated_pre_case_chain(tmp_path, mutation):
    paths = completion_fixture(tmp_path, phase_remaining="01:04:59", wrapper_exit=3)

    def change(path, update):
        value = json.loads(path.read_text())
        update(value)
        path.write_text(json.dumps(value))

    paths["case_summary_path"].unlink()
    paths["server_check_path"].unlink()
    if mutation == "unknown_status":
        change(paths["phase_path"], lambda value: value.update(status="unstarted_unknown"))
    elif mutation == "runner_drift":
        paths["runner_path"].write_text("# drift after smoke\n")
    elif mutation == "plan_drift":
        change(paths["case_plan_path"], lambda value: value.update(status="forged"))
    elif mutation == "pre_smoke_drift":
        change(paths["pre_smoke_path"], lambda value: value.update(status="forged"))
    elif mutation == "native_job":
        change(paths["native_path"], lambda value: value.update(slurm_job_id="other"))
    elif mutation == "preflight_limits":
        change(
            paths["preflight_path"],
            lambda value: value["enclosing_case_a_limits"].update(case_requests=17),
        )
    elif mutation == "cleanup_path":
        wrong = paths["cleanup_path"].parent / "wrong-cleanup.json"
        wrong.write_bytes(paths["cleanup_path"].read_bytes())
        paths["cleanup_path"] = wrong
    elif mutation == "status_time_mismatch":
        change(
            paths["phase_path"],
            lambda value: value.update(status="unstarted_walltime_limit_exceeded"),
        )
    elif mutation == "parsed_time_mismatch":
        change(
            paths["phase_path"],
            lambda value: value["time_decision"].update(remaining_seconds=3900),
        )
    elif mutation == "phase_helpers":
        change(paths["phase_path"], lambda value: value["helpers"].pop("smoke.py"))
    elif mutation == "phase_limits":
        change(
            paths["phase_path"],
            lambda value: value["limits"].update(total_generation_requests=25),
        )
    elif mutation == "wrapper_checksums":
        paths["wrapper_sha256_path"].write_text("0" * 64 + "  /forged\n")
    elif mutation == "cleanup_server_pid":
        change(paths["cleanup_path"], lambda value: value.update(server_pid=999))
    else:
        change(paths["cleanup_path"], lambda value: value["case_process"].update(pid=456))
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "incomplete"
    assert result["error_type"] == "ValueError"


def test_unstarted_terminal_rejects_reserved_time_relabelled_insufficient(tmp_path):
    paths = completion_fixture(tmp_path, wrapper_exit=3)
    phase = json.loads(paths["phase_path"].read_text())
    phase["status"] = "unstarted_insufficient_remaining_time"
    paths["phase_path"].write_text(json.dumps(phase))
    paths["case_summary_path"].unlink()
    paths["server_check_path"].unlink()
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "incomplete"
    assert result["error_type"] == "ValueError"


def test_started_failure_still_writes_terminal_infrastructure_receipts(tmp_path):
    paths = completion_fixture(tmp_path)
    paths["case_summary_path"].unlink()
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "incomplete"
    assert result["error_type"] == "FileNotFoundError"
    assert result["phase"]["sha256"]
    assert result["server_check"]["sha256"]
    assert result["cleanup"]["sha256"]


@pytest.mark.parametrize(
    "mutation",
    [
        "phase_case_path",
        "phase_plan",
        "preflight_job",
        "preflight_limits",
        "execution_binding",
        "summary_plan",
        "terminal_file",
        "terminal_plan",
        "attempt_sequence",
        "runner_drift",
        "server_endpoint",
        "cleanup_job",
        "wrong_smoke_path",
        "phase_helpers",
        "phase_limits",
        "wrapper_checksums",
        "server_pid",
        "cleanup_server_pid",
        "cleanup_case_pid",
    ],
)
def test_complete_receipt_rejects_mutated_chain_edges(tmp_path, mutation):
    paths = completion_fixture(tmp_path)

    def change(path, update):
        value = json.loads(path.read_text())
        update(value)
        path.write_text(json.dumps(value))

    if mutation == "phase_case_path":
        change(paths["phase_path"], lambda value: value.update(case_dir=str(tmp_path / "other")))
    elif mutation == "phase_plan":
        change(paths["phase_path"], lambda value: value.update(plan={"sha256": "forged"}))
    elif mutation == "preflight_job":
        change(paths["preflight_path"], lambda value: value.update(slurm_job_id="other"))
    elif mutation == "preflight_limits":
        change(
            paths["preflight_path"],
            lambda value: value["enclosing_case_a_limits"].update(case_requests=17),
        )
    elif mutation == "execution_binding":
        change(paths["execution_path"], lambda value: value.update(serving={"status": "forged"}))
    elif mutation == "summary_plan":
        change(paths["case_summary_path"], lambda value: value.update(plan={"sha256": "forged"}))
    elif mutation == "terminal_file":
        change(
            paths["case_plan_path"].parent / "clean-terminal.json",
            lambda value: value.update(status="forged"),
        )
    elif mutation == "terminal_plan":
        change(
            paths["case_plan_path"].parent / "attacked-terminal.json",
            lambda value: value.update(plan={"sha256": "forged"}),
        )
    elif mutation == "attempt_sequence":
        attempt = paths["case_plan_path"].parent / "clean" / "sdk-attempts.jsonl"
        attempt.write_text('{"sdk_attempt": 2}\n')
    elif mutation == "runner_drift":
        paths["runner_path"].write_text("# changed after smoke\n")
    elif mutation == "server_endpoint":
        change(
            paths["server_check_path"],
            lambda value: value.update(endpoint="http://127.0.0.1:9000/v1"),
        )
    elif mutation == "cleanup_job":
        change(paths["cleanup_path"], lambda value: value.update(slurm_job_id="other"))
    elif mutation == "wrong_smoke_path":
        wrong = paths["smoke_path"].parent / "wrong-smoke.json"
        wrong.write_bytes(paths["smoke_path"].read_bytes())
        paths["smoke_path"] = wrong
    elif mutation == "phase_helpers":
        change(paths["phase_path"], lambda value: value["helpers"].pop("smoke.py"))
    elif mutation == "phase_limits":
        change(
            paths["phase_path"],
            lambda value: value["limits"].update(total_generation_requests=25),
        )
    elif mutation == "wrapper_checksums":
        paths["wrapper_sha256_path"].write_text("0" * 64 + "  /forged\n")
    elif mutation == "server_pid":
        change(paths["server_check_path"], lambda value: value.update(server_pid=999))
    elif mutation == "cleanup_server_pid":
        change(paths["cleanup_path"], lambda value: value.update(server_pid=999))
    else:
        change(paths["cleanup_path"], lambda value: value["case_process"].update(pid=0))
    result = case_a_batch.finalize(
        paths["smoke_path"].parent / "case-a-batch-summary.json", **paths
    )
    assert result["status"] == "incomplete"
    assert result["error_type"] == "ValueError"


def test_wrapper_is_separate_bounded_and_hardens_shared_smoke_cleanup():
    original = (HPC / "scout-smoke.sbatch").read_bytes()
    wrapper = (HPC / "scout-smoke-case-a.sbatch").read_text()
    assert hashlib.sha256(original).hexdigest() == (
        "1e2caa7bd21310f7ce04af46607ad0e077abb56f2ba117691f5ee466a584ee1a"
    )
    for fragment in (
        "#SBATCH --time=02:00:00",
        "export SCOUT_NATIVE_SMOKE=1",
        "export SCOUT_CASE_A_MODE=1",
        "squeue -h -j \"$SLURM_JOB_ID\" -o '%i|%L|%l'",
        '--remaining "$REMAINING_TIME" --time-limit "$TIME_LIMIT"',
        "sleep 3600",
        'kill -TERM -- "-$CASE_A_PROCESS_PID"',
        'kill -KILL -- "-$CASE_A_PROCESS_PID"',
        "case-a-server-check.json",
        "case-a-cleanup.json",
        "case-a-batch-summary.json",
        "export SCOUT_SERVER_PID",
        "SCOUT_SITE_SHA256:?Export the reviewed site-file SHA-256 at submission",
        "SCOUT_HPC_MANIFEST_SHA256:?Set its reviewed SHA-256 in the site file",
        "sha256sum --check --strict --status submission-sha256.txt",
        'cmp --silent -- "$CASE_A_EXECUTED_WRAPPER" "$CASE_A_CANONICAL_WRAPPER"',
        '[[ "$SCOUT_LAB_PYTHON" == /* ]]',
        "readonly CASE_A_HPC_DIR",
        "unset SCOUT_SITE_FILE",
        '--pre-smoke-path "$SCOUT_CASE_A_PRE_SMOKE"',
        '--runner-path "$SCOUT_CASE_A_RUNNER"',
        '--wrapper-sha256-path "$CASE_A_WRAPPER_SHA256"',
        '--server-pid "$SCOUT_SERVER_PID"',
        '&& kill -TERM -- "-$CASE_A_PROCESS_PID"',
        'if kill -KILL -- "-$CASE_A_PROCESS_PID"',
        "(( SCOUT_SERVER_PID <= 1 ))",
        "(( CASE_A_PROCESS_PID > 1 ))",
        "valid_server_pid=true",
    ):
        assert fragment in wrapper
    assert 'dirname -- "${BASH_SOURCE[0]}"' not in wrapper
    assert wrapper.index('source "$CASE_A_SITE_FILE"') < wrapper.index(
        'CASE_A_HPC_DIR=$(realpath -e -- "$SCOUT_HPC_DIR")'
    )
    assert wrapper.index("unset SCOUT_SITE_FILE SCOUT_SITE_SHA256") < wrapper.index(
        'source "$CASE_A_HPC_DIR/scout-smoke.sbatch"'
    )
    assert wrapper.count('source "$CASE_A_SITE_FILE"') == 1
    assert 'kill -TERM -- "-$CASE_A_PROCESS_PID" 2>/dev/null || true' not in wrapper
    assert 'kill -KILL -- "-$CASE_A_PROCESS_PID" 2>/dev/null || true' not in wrapper
    assert "[[ ${SCOUT_SERVER_PID:-} =~ ^[1-9][0-9]*$ ]] || exit 2" not in wrapper
    pid_guard = "if [[ ! ${SCOUT_SERVER_PID:-} =~ ^[0-9]+$ ]] || (( SCOUT_SERVER_PID <= 1 )); then"
    smoke_source = 'source "$CASE_A_HPC_DIR/scout-smoke.sbatch"'
    post_smoke_guard = '[[ "$SCOUT_HPC_DIR" == "$CASE_A_HPC_DIR"'
    assert wrapper.index(smoke_source) < wrapper.index(pid_guard) < wrapper.index(post_smoke_guard)
    assert wrapper.index("SCOUT_SERVER_PID=''") < wrapper.index("exit 2", wrapper.index(pid_guard))
    assert wrapper.index('source "$CASE_A_HPC_DIR/scout-smoke.sbatch"') < wrapper.index(
        '"$SCOUT_CASE_A_RUNNER" run'
    )
    assert (
        wrapper.index('source "$CASE_A_HPC_DIR/scout-smoke.sbatch"')
        < wrapper.index("export SCOUT_SERVER_PID")
        < wrapper.index("case-a-server-check.json")
    )
    assert "http://127.0.0.1:$SCOUT_PORT/v1" in original.decode()
    assert 'if [[ "$SCOUT_SERVER_PID" =~ ^[0-9]+$ ]] && (( SCOUT_SERVER_PID > 1 )); then' in original.decode()
    assert case_a_batch.TOTAL_REQUEST_LIMIT == 24
    assert case_a_batch.WALLTIME_SECONDS == 7200
    assert case_a_batch.CASE_REQUEST_LIMIT == 16
