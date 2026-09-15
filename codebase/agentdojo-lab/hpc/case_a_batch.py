"""Offline gates and immutable receipts for the bounded Scout smoke-plus-Case-A job."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

PROTOCOL = "nesi-scout-smoke-case-a-v1"
WALLTIME_SECONDS = 7200
MINIMUM_REMAINING_SECONDS = 3900
CASE_COMMAND_TIMEOUT_SECONDS = 3600
SYNTHETIC_REQUEST_LIMIT = 4
NATIVE_REQUEST_LIMIT = 4
CASE_REQUEST_LIMIT = 16
TOTAL_REQUEST_LIMIT = 24
CASE_PROTOCOL = "scout-case-a-recipient-v1"
SMOKE_PROTOCOL = "nesi-scout-smoke-v1"
NATIVE_PROTOCOL = "nesi-scout-native-clean-smoke-v1"
UNSTARTED_STATUSES = {
    "unstarted_walltime_limit_exceeded",
    "unstarted_insufficient_remaining_time",
    "unstarted_invalid_current_job_time_evidence",
}
MANIFEST_PAYLOAD_NAMES = frozenset(
    {
        "case_a_batch.py",
        "native_smoke.py",
        "preflight.py",
        "run_case_a_scout.py",
        "scout-smoke-case-a.sbatch",
        "scout-smoke.sbatch",
        "smoke.py",
        "tool_chat_template_llama4_pythonic_typed_v1.jinja",
    }
)
EXPECTED_HELPER_NAMES = MANIFEST_PAYLOAD_NAMES | {"submission-sha256.txt"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def receipt(path: Path) -> dict:
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def fixed_limits() -> dict:
    return {
        "walltime_seconds": WALLTIME_SECONDS,
        "minimum_remaining_seconds": MINIMUM_REMAINING_SECONDS,
        "case_command_timeout_seconds": CASE_COMMAND_TIMEOUT_SECONDS,
        "synthetic_requests": SYNTHETIC_REQUEST_LIMIT,
        "native_requests": NATIVE_REQUEST_LIMIT,
        "case_requests": CASE_REQUEST_LIMIT,
        "total_generation_requests": TOTAL_REQUEST_LIMIT,
        "online_auditor_requests": 0,
        "sdk_retries": 0,
    }


def fixed_preflight_limits() -> tuple[dict, dict]:
    smoke = {
        "scope": "smoke_phase_only",
        "gpus": 4,
        "intended_walltime_minutes": 60,
        "ready_seconds": 1500,
        "generative_requests": 8,
        "synthetic_requests": 4,
        "synthetic_request_timeout_seconds": 120,
        "synthetic_max_completion_tokens_per_request": 512,
        "native_requests": 4,
        "native_request_timeout_seconds": 180,
        "native_max_completion_tokens_per_request": 2048,
    }
    enclosing = {
        "scope": "smoke_plus_case_a_job",
        "walltime_seconds": WALLTIME_SECONDS,
        "total_generation_requests": TOTAL_REQUEST_LIMIT,
        "case_requests": CASE_REQUEST_LIMIT,
        "online_auditor_requests": 0,
    }
    return smoke, enclosing


def validate_preflight_limit_records(preflight: dict) -> None:
    smoke, enclosing = fixed_preflight_limits()
    if (
        preflight.get("limits") != smoke
        or preflight.get("enclosing_case_a_limits") != enclosing
    ):
        raise ValueError("Preflight does not record the fixed smoke and Case A limits")


def require_absolute_regular(path: Path, label: str) -> Path:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be an absolute, existing, non-symlink file")
    return path.resolve()


def helper_receipts(helper_paths: list[Path]) -> dict:
    helpers: dict[str, dict] = {}
    for path in helper_paths:
        resolved = require_absolute_regular(path, "Submission helper")
        if resolved.name in helpers:
            raise ValueError("Submission helper names must be unique")
        helpers[resolved.name] = receipt(resolved)
    if set(helpers) != EXPECTED_HELPER_NAMES:
        raise ValueError("Submission helper set differs from the fixed Case A set")
    parents = {str(Path(item["path"]).parent) for item in helpers.values()}
    if len(parents) != 1:
        raise ValueError("All frozen Case A helpers must share one directory")
    return helpers


def manifest_entries(path: Path, helpers: dict) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\x00]+)", line)
        if match is None or match.group(2) in entries:
            raise ValueError("Malformed or duplicate Case A checksum manifest entry")
        entries[match.group(2)] = match.group(1)
    expected = {
        name: item["sha256"]
        for name, item in helpers.items()
        if name != "submission-sha256.txt"
    }
    if set(entries) != MANIFEST_PAYLOAD_NAMES or entries != expected:
        raise ValueError("Case A checksum manifest does not exactly bind every payload")
    return entries


def submission_binding(
    *,
    site_path: Path,
    site_sha256: str,
    manifest_path: Path,
    manifest_sha256: str,
    executed_wrapper_path: Path,
    canonical_wrapper_path: Path,
    helper_paths: list[Path],
) -> tuple[dict, dict]:
    if not SHA256_RE.fullmatch(site_sha256) or not SHA256_RE.fullmatch(manifest_sha256):
        raise ValueError("Submission hashes must be lowercase SHA-256 values")
    site = require_absolute_regular(site_path, "Case A site file")
    manifest = require_absolute_regular(manifest_path, "Case A manifest")
    executed = require_absolute_regular(executed_wrapper_path, "Executed Case A wrapper")
    canonical = require_absolute_regular(canonical_wrapper_path, "Canonical Case A wrapper")
    helpers = helper_receipts(helper_paths)
    helper_dir = Path(next(iter(helpers.values()))["path"]).parent
    if (
        manifest != helper_dir / "submission-sha256.txt"
        or canonical != helper_dir / "scout-smoke-case-a.sbatch"
    ):
        raise ValueError("Submission binding paths differ from the frozen helper directory")
    site_receipt = receipt(site)
    manifest_receipt = receipt(manifest)
    executed_receipt = receipt(executed)
    canonical_receipt = receipt(canonical)
    if site_receipt["sha256"] != site_sha256:
        raise ValueError("Case A site file differs from its submission hash")
    if manifest_receipt["sha256"] != manifest_sha256:
        raise ValueError("Case A manifest differs from its submission hash")
    if executed_receipt["sha256"] != canonical_receipt["sha256"]:
        raise ValueError("Slurm-spooled Case A wrapper differs from the canonical wrapper")
    if helpers["submission-sha256.txt"] != manifest_receipt:
        raise ValueError("Helper receipts do not bind the submitted manifest")
    if helpers["scout-smoke-case-a.sbatch"] != canonical_receipt:
        raise ValueError("Helper receipts do not bind the canonical wrapper")
    manifest_entries(manifest, helpers)
    return (
        {
            "site": site_receipt,
            "site_sha256_at_submission": site_sha256,
            "manifest": manifest_receipt,
            "manifest_sha256_at_submission": manifest_sha256,
            "executed_wrapper": executed_receipt,
            "canonical_wrapper": canonical_receipt,
            "executed_wrapper_matches_canonical": True,
        },
        helpers,
    )


def validate_recorded_submission(binding: dict, helpers: dict) -> None:
    if set(helpers) != EXPECTED_HELPER_NAMES:
        raise ValueError("Recorded helper set differs from the fixed Case A set")
    for item in helpers.values():
        if receipt(Path(item["path"])) != item:
            raise ValueError("A frozen Case A helper changed")
    manifest = helpers["submission-sha256.txt"]
    canonical = helpers["scout-smoke-case-a.sbatch"]
    required = {
        "site",
        "site_sha256_at_submission",
        "manifest",
        "manifest_sha256_at_submission",
        "executed_wrapper",
        "canonical_wrapper",
        "executed_wrapper_matches_canonical",
    }
    if set(binding) != required:
        raise ValueError("Recorded Case A submission binding has unexpected fields")
    for name in ("site", "manifest", "executed_wrapper", "canonical_wrapper"):
        if receipt(Path(binding[name]["path"])) != binding[name]:
            raise ValueError("A submission-bound Case A file changed")
    if (
        binding["site"]["sha256"] != binding["site_sha256_at_submission"]
        or binding["manifest"]["sha256"] != binding["manifest_sha256_at_submission"]
        or binding["manifest"] != manifest
        or binding["canonical_wrapper"] != canonical
        or binding["executed_wrapper"]["sha256"] != canonical["sha256"]
        or binding["executed_wrapper_matches_canonical"] is not True
    ):
        raise ValueError("Recorded Case A submission hashes are inconsistent")
    manifest_entries(Path(manifest["path"]), helpers)


def validate_wrapper_checksums(path: Path, binding: dict, helpers: dict) -> None:
    recorded: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (/.+)", line)
        if match is None:
            raise ValueError("Malformed Case A wrapper checksum entry")
        resolved = str(Path(match.group(2)).resolve())
        if resolved in recorded:
            raise ValueError("Duplicate Case A wrapper checksum path")
        recorded[resolved] = match.group(1)
    expected = {
        item["path"]: item["sha256"]
        for item in (
            binding["executed_wrapper"],
            binding["site"],
            *helpers.values(),
        )
    }
    if recorded != expected:
        raise ValueError("Case A wrapper checksum record differs from bound inputs")


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object receipt")
    return value


def write_exclusive(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def validate_prepared_case(case_dir: Path, smoke_dir: Path, *, verifier=None) -> dict:
    """Require a pristine prepared directory and revalidate all plan-bound sources."""
    if not case_dir.is_absolute() or not smoke_dir.is_absolute():
        raise ValueError("Case and smoke evidence paths must be absolute")
    case_dir = case_dir.resolve()
    smoke_dir = smoke_dir.resolve()
    if not case_dir.is_dir():
        raise ValueError("The prepared Case A directory must exist")
    if case_dir == smoke_dir or case_dir.is_relative_to(smoke_dir) or smoke_dir.is_relative_to(case_dir):
        raise ValueError("Case and smoke evidence directories must be separate")
    actual = {path.name for path in case_dir.iterdir()}
    if actual != {"plan.json", "preparation.json"}:
        raise ValueError("Prepared Case A directory must contain only plan.json and preparation.json")
    if smoke_dir.exists():
        raise FileExistsError("Smoke evidence directory must be fresh")
    if verifier is None:
        from agentdojo_lab.case_a_scout import verify_plan

        verifier = verify_plan
    plan = verifier(case_dir)
    if plan.get("protocol") != CASE_PROTOCOL:
        raise ValueError("Prepared plan is not Case A v1")
    limits = plan.get("limits", {})
    config = plan.get("config", {})
    if (
        limits.get("primary_sdk_attempts_total") != CASE_REQUEST_LIMIT
        or limits.get("online_auditor_requests") != 0
        or limits.get("sdk_max_retries") != 0
        or config.get("provider") != "openai_compatible"
        or config.get("base_url") != "http://127.0.0.1:8000/v1"
        or config.get("online_causal_audit", False) is not False
    ):
        raise ValueError("Prepared plan violates the fixed local Case A request/endpoint bounds")
    return plan


def validate_before_smoke(
    output: Path,
    case_dir: Path,
    smoke_dir: Path,
    runner_path: Path,
    site_path: Path,
    site_sha256: str,
    manifest_path: Path,
    manifest_sha256: str,
    executed_wrapper_path: Path,
    canonical_wrapper_path: Path,
    helper_paths: list[Path],
    *,
    verifier=None,
) -> dict:
    """Bind the prepared plan and exact active runner before smoke starts."""
    if not output.is_absolute() or not runner_path.is_absolute():
        raise ValueError("Pre-smoke receipt and Case A runner paths must be absolute")
    plan = validate_prepared_case(case_dir, smoke_dir, verifier=verifier)
    if not runner_path.is_file():
        raise ValueError("Case A runner must be an existing file")
    expected = plan.get("source_hashes", {}).get("scripts/run_case_a_scout.py")
    if not isinstance(expected, str) or receipt(runner_path)["sha256"] != expected:
        raise ValueError("Case A runner differs from its prepared source hash")
    binding, helpers = submission_binding(
        site_path=site_path,
        site_sha256=site_sha256,
        manifest_path=manifest_path,
        manifest_sha256=manifest_sha256,
        executed_wrapper_path=executed_wrapper_path,
        canonical_wrapper_path=canonical_wrapper_path,
        helper_paths=helper_paths,
    )
    if helpers["run_case_a_scout.py"] != receipt(runner_path):
        raise ValueError("Case A runner is not the frozen submitted runner")
    value = {
        "protocol": PROTOCOL,
        "status": "prepared_inputs_validated_before_smoke",
        "case_dir": str(case_dir.resolve()),
        "smoke_dir": str(smoke_dir.resolve()),
        "plan": receipt(case_dir / "plan.json"),
        "runner": receipt(runner_path),
        "submission_binding": binding,
        "helpers": helpers,
    }
    write_exclusive(output, value)
    return value


def parse_slurm_duration(value: str) -> int:
    """Parse Slurm's [days-]hours:minutes:seconds or minutes:seconds form."""
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("Missing Slurm duration")
    day_text, clock = (value.split("-", 1) if "-" in value else ("0", value))
    parts = clock.split(":")
    if len(parts) == 2:
        parts.insert(0, "0")
    if (
        len(parts) != 3
        or not day_text.isdigit()
        or any(not part.isdigit() for part in parts)
    ):
        raise ValueError("Invalid Slurm duration")
    days, hours, minutes, seconds = (int(day_text), *(int(part) for part in parts))
    if (days and hours > 23) or minutes > 59 or seconds > 59:
        raise ValueError("Invalid Slurm duration fields")
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def scheduler_decision(
    *, job_id: str, reported_job_id: str, remaining: str, time_limit: str
) -> dict:
    """Purely derive the only permitted Case start decision from Slurm fields."""
    status = "reserved_before_case_calls"
    error_type = None
    try:
        if not job_id or reported_job_id != job_id:
            raise ValueError("Slurm time record belongs to another job")
        remaining_seconds = parse_slurm_duration(remaining)
        time_limit_seconds = parse_slurm_duration(time_limit)
        if time_limit_seconds <= 0 or remaining_seconds > time_limit_seconds:
            raise ValueError("Slurm remaining time is inconsistent with its time limit")
        if time_limit_seconds > WALLTIME_SECONDS:
            status = "unstarted_walltime_limit_exceeded"
        elif remaining_seconds < MINIMUM_REMAINING_SECONDS:
            status = "unstarted_insufficient_remaining_time"
    except ValueError as error:
        status = "unstarted_invalid_current_job_time_evidence"
        error_type = type(error).__name__
        remaining_seconds = None
        time_limit_seconds = None
    value = {
        "status": status,
        "time_decision": {
            "source": "squeue_current_job_%i_%L_%l",
            "reported_job_id": reported_job_id,
            "remaining_raw": remaining,
            "time_limit_raw": time_limit,
            "remaining_seconds": remaining_seconds,
            "time_limit_seconds": time_limit_seconds,
        },
    }
    if error_type:
        value["error_type"] = error_type
    return value


def validate_scheduler_decision(phase: dict) -> None:
    recorded = phase.get("time_decision", {})
    expected = scheduler_decision(
        job_id=phase.get("slurm_job_id", ""),
        reported_job_id=recorded.get("reported_job_id", ""),
        remaining=recorded.get("remaining_raw", ""),
        time_limit=recorded.get("time_limit_raw", ""),
    )
    if (
        phase.get("status") != expected["status"]
        or recorded != expected["time_decision"]
        or phase.get("error_type") != expected.get("error_type")
        or ("error_type" in phase) != ("error_type" in expected)
    ):
        raise ValueError("Recorded Case A scheduler decision is inconsistent")


def reserve_phase(
    output: Path,
    *,
    job_id: str,
    reported_job_id: str,
    remaining: str,
    time_limit: str,
    case_dir: Path,
    server_pid: int,
    wrapper_sha256_path: Path,
    pre_smoke_path: Path | None = None,
    runner_path: Path | None = None,
    helper_paths: list[Path] = (),
) -> dict:
    if not job_id:
        raise ValueError("A Slurm job ID is required")
    if type(server_pid) is not int or server_pid <= 1:
        raise ValueError("A live server PID is required before Case A reservation")
    decision = scheduler_decision(
        job_id=job_id,
        reported_job_id=reported_job_id,
        remaining=remaining,
        time_limit=time_limit,
    )
    case_dir = case_dir.resolve()
    pre_smoke = read(pre_smoke_path) if pre_smoke_path is not None else None
    current_plan = receipt(case_dir / "plan.json")
    current_runner = receipt(runner_path) if runner_path is not None else None
    if pre_smoke is not None and (
        pre_smoke.get("protocol") != PROTOCOL
        or pre_smoke.get("status") != "prepared_inputs_validated_before_smoke"
        or pre_smoke.get("case_dir") != str(case_dir)
        or pre_smoke.get("plan") != current_plan
        or pre_smoke.get("runner") != current_runner
    ):
        raise ValueError("Pre-smoke Case A binding changed before phase reservation")
    current_helpers = helper_receipts(helper_paths)
    if pre_smoke is None or pre_smoke.get("helpers") != current_helpers:
        raise ValueError("Frozen Case A helpers changed before phase reservation")
    binding = pre_smoke.get("submission_binding")
    if not isinstance(binding, dict):
        raise ValueError("Missing Case A submission binding")
    validate_recorded_submission(binding, current_helpers)
    wrapper_sha256_path = require_absolute_regular(
        wrapper_sha256_path, "Case A wrapper checksum record"
    )
    validate_wrapper_checksums(wrapper_sha256_path, binding, current_helpers)
    value = {
        "protocol": PROTOCOL,
        "status": decision["status"],
        "slurm_job_id": job_id,
        "server_pid": server_pid,
        "time_decision": decision["time_decision"],
        "case_dir": str(case_dir),
        "plan": current_plan,
        "runner": current_runner,
        "pre_smoke": receipt(pre_smoke_path) if pre_smoke_path is not None else None,
        "submission_binding": binding,
        "helpers": current_helpers,
        "wrapper_checksums": receipt(wrapper_sha256_path),
        "limits": fixed_limits(),
    }
    if "error_type" in decision:
        value["error_type"] = decision["error_type"]
    write_exclusive(output, value)
    return value


def check_server(
    output: Path,
    *,
    base_url: str,
    key: str,
    server_pid: int,
    job_id: str,
    opener=None,
    auth_probe=None,
    identity_probe=None,
) -> dict:
    from agentdojo_lab.case_a_scout import (
        live_serving_identity,
        local_url,
        models_auth_check,
    )

    try:
        local_url(base_url)
    except ValueError as error:
        raise ValueError("Server check requires literal loopback /v1") from error
    value = {
        "protocol": PROTOCOL,
        "status": "failed",
        "slurm_job_id": job_id,
        "endpoint": base_url,
        "server_pid": server_pid,
    }
    try:
        if os.environ.get("SLURM_JOB_ID") != job_id:
            raise ValueError("Server check job differs from the current allocation")
        if os.environ.get("SCOUT_SERVER_PID") != str(server_pid):
            raise ValueError("Server check PID differs from SCOUT_SERVER_PID")
        auth_probe = auth_probe or (
            lambda url, secret: models_auth_check(url, secret, opener=opener)
        )
        identity_probe = identity_probe or live_serving_identity
        identity = identity_probe(server_pid, job_id)
        auth = auth_probe(base_url, key)
        if identity_probe(server_pid, job_id) != identity:
            raise ValueError("Server process identity changed during authentication checks")
        value.update(
            status="passed",
            model="llama-4-scout-local",
            created_unix_ns=time.time_ns(),
            live_binding=identity,
            models_auth=auth,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        value["error_type"] = type(error).__name__
    write_exclusive(output, value)
    return value


def record_cleanup(
    output: Path,
    *,
    server_pid: int,
    term_sent: bool,
    kill_sent: bool,
    stopped: bool,
    case_pid: int = 0,
    case_term_sent: bool = False,
    case_kill_sent: bool = False,
    case_stopped: bool = True,
    job_id: str = "",
) -> dict:
    value = {
        "protocol": PROTOCOL,
        "slurm_job_id": job_id,
        "status": "server_stopped" if stopped else "server_cleanup_unconfirmed",
        "server_pid": server_pid,
        "term_sent": term_sent,
        "kill_sent": kill_sent,
        "case_process": {
            "pid": case_pid,
            "term_sent": case_term_sent,
            "kill_sent": case_kill_sent,
            "stopped": case_stopped,
        },
    }
    write_exclusive(output, value)
    return value


def require_path(path: Path, parent: Path, name: str) -> None:
    if path.resolve() != parent.resolve() / name:
        raise ValueError(f"Expected {name} in the bound evidence directory")


def count_slot_attempts(path: Path) -> int:
    if not path.is_file():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > 8:
        raise ValueError("Case A slot exceeded eight SDK attempts")
    for expected, line in enumerate(lines, 1):
        row = json.loads(line)
        if (
            not isinstance(row, dict)
            or type(row.get("sdk_attempt")) is not int
            or row["sdk_attempt"] != expected
        ):
            raise ValueError("Case A SDK attempts must be sequential JSON objects")
    return len(lines)


def validate_phase_sources(
    *,
    phase: dict,
    pre_smoke: dict,
    smoke_root: Path,
    wrapper_sha256_path: Path,
) -> None:
    """Recompute every helper and submission binding used by both terminal paths."""
    require_path(wrapper_sha256_path, smoke_root, "case-a-wrapper-sha256.txt")
    helpers = phase.get("helpers")
    binding = phase.get("submission_binding")
    if (
        type(phase.get("server_pid")) is not int
        or phase["server_pid"] <= 1
        or phase.get("limits") != fixed_limits()
        or not isinstance(helpers, dict)
        or not isinstance(binding, dict)
        or helpers != pre_smoke.get("helpers")
        or binding != pre_smoke.get("submission_binding")
        or phase.get("wrapper_checksums") != receipt(wrapper_sha256_path)
    ):
        raise ValueError("Case A phase source, PID, checksum, or limit binding differs")
    validate_recorded_submission(binding, helpers)
    validate_wrapper_checksums(wrapper_sha256_path, binding, helpers)


def validate_unstarted_chain(
    *,
    phase: dict,
    pre_smoke_path: Path,
    runner_path: Path,
    preflight_path: Path,
    smoke_path: Path,
    native_path: Path,
    cleanup_path: Path,
    wrapper_sha256_path: Path,
    case_plan_path: Path,
    binding_validator=None,
) -> dict:
    """Validate all pre-Case evidence while omitting artifacts Case never created."""
    if phase.get("status") not in UNSTARTED_STATUSES:
        raise ValueError("Unrecognized Case A unstarted gate status")
    smoke_root = smoke_path.parent.resolve()
    for path, name in (
        (preflight_path, "preflight.json"),
        (smoke_path, "smoke.json"),
        (native_path, "native-smoke.json"),
        (cleanup_path, "case-a-cleanup.json"),
    ):
        require_path(path, smoke_root, name)
    if pre_smoke_path.resolve() != Path(str(smoke_root) + ".case-a-pre-smoke.json"):
        raise ValueError("Pre-smoke receipt path differs from the bound smoke directory")
    case_root = case_plan_path.parent.resolve()
    require_path(case_plan_path, case_root, "plan.json")
    plan_receipt = receipt(case_plan_path)
    runner_receipt = receipt(runner_path)
    if (
        phase.get("protocol") != PROTOCOL
        or phase.get("case_dir") != str(case_root)
        or phase.get("plan") != plan_receipt
        or phase.get("runner") != runner_receipt
        or phase.get("pre_smoke") != receipt(pre_smoke_path)
    ):
        raise ValueError("Unstarted phase source or path binding differs")
    pre_smoke = read(pre_smoke_path)
    if (
        pre_smoke.get("protocol") != PROTOCOL
        or pre_smoke.get("status") != "prepared_inputs_validated_before_smoke"
        or pre_smoke.get("case_dir") != str(case_root)
        or pre_smoke.get("smoke_dir") != str(smoke_root)
        or pre_smoke.get("plan") != plan_receipt
        or pre_smoke.get("runner") != runner_receipt
    ):
        raise ValueError("Unstarted pre-smoke binding differs")
    validate_phase_sources(
        phase=phase,
        pre_smoke=pre_smoke,
        smoke_root=smoke_root,
        wrapper_sha256_path=wrapper_sha256_path,
    )
    plan = read(case_plan_path)
    if (
        plan.get("protocol") != CASE_PROTOCOL
        or plan.get("source_hashes", {}).get("scripts/run_case_a_scout.py")
        != runner_receipt["sha256"]
    ):
        raise ValueError("Unstarted Case A plan does not bind the current runner")
    job_id = phase.get("slurm_job_id")
    preflight = read(preflight_path)
    smoke = read(smoke_path)
    native = read(native_path)
    cleanup = read(cleanup_path)
    validate_preflight_limit_records(preflight)
    if (
        preflight.get("protocol") != SMOKE_PROTOCOL
        or preflight.get("slurm_job_id") != job_id
        or smoke.get("protocol") != SMOKE_PROTOCOL
        or native.get("protocol") != NATIVE_PROTOCOL
        or native.get("slurm_job_id") != job_id
        or cleanup.get("protocol") != PROTOCOL
        or cleanup.get("slurm_job_id") != job_id
        or cleanup.get("server_pid") != phase.get("server_pid")
        or cleanup.get("case_process", {}).get("pid") != 0
    ):
        raise ValueError("Unstarted smoke or cleanup allocation binding differs")
    if binding_validator is None:
        from agentdojo_lab.case_a_scout import recorded_smoke_binding

        binding_validator = recorded_smoke_binding
    binding = binding_validator(preflight_path, plan["config"]["base_url"])
    if (
        binding.get("status") != "bound_before_case_calls"
        or binding.get("slurm_job_id") != job_id
    ):
        raise ValueError("Unstarted recomputed serving binding differs")
    return binding


def validate_case_chain(
    *,
    phase: dict,
    pre_smoke_path: Path,
    runner_path: Path,
    preflight_path: Path,
    smoke_path: Path,
    native_path: Path,
    server_check_path: Path,
    cleanup_path: Path,
    wrapper_sha256_path: Path,
    case_plan_path: Path,
    execution_path: Path,
    case_summary_path: Path,
    binding_validator=None,
) -> tuple[dict, dict, list[int]]:
    """Recompute the serving and Case artifact chain used for terminal success."""
    smoke_root = smoke_path.parent.resolve()
    expected_pre_smoke = Path(str(smoke_root) + ".case-a-pre-smoke.json")
    if pre_smoke_path.resolve() != expected_pre_smoke:
        raise ValueError("Pre-smoke receipt path differs from the bound smoke directory")
    for path, name in (
        (preflight_path, "preflight.json"),
        (smoke_path, "smoke.json"),
        (native_path, "native-smoke.json"),
        (server_check_path, "case-a-server-check.json"),
        (cleanup_path, "case-a-cleanup.json"),
    ):
        require_path(path, smoke_root, name)
    case_root = case_plan_path.parent.resolve()
    require_path(case_plan_path, case_root, "plan.json")
    require_path(execution_path, case_root, "execution.json")
    require_path(case_summary_path, case_root, "case-summary.json")
    if phase.get("protocol") != PROTOCOL or phase.get("case_dir") != str(case_root):
        raise ValueError("Phase protocol or Case A path differs")
    plan_receipt = receipt(case_plan_path)
    runner_receipt = receipt(runner_path)
    pre_smoke_receipt = receipt(pre_smoke_path)
    if (
        phase.get("plan") != plan_receipt
        or phase.get("runner") != runner_receipt
        or phase.get("pre_smoke") != pre_smoke_receipt
    ):
        raise ValueError("Phase plan, runner, or pre-smoke receipt changed")
    pre_smoke = read(pre_smoke_path)
    if (
        pre_smoke.get("protocol") != PROTOCOL
        or pre_smoke.get("status") != "prepared_inputs_validated_before_smoke"
        or pre_smoke.get("case_dir") != str(case_root)
        or pre_smoke.get("smoke_dir") != str(smoke_root)
        or pre_smoke.get("plan") != plan_receipt
        or pre_smoke.get("runner") != runner_receipt
    ):
        raise ValueError("Pre-smoke source binding differs")
    validate_phase_sources(
        phase=phase,
        pre_smoke=pre_smoke,
        smoke_root=smoke_root,
        wrapper_sha256_path=wrapper_sha256_path,
    )
    plan = read(case_plan_path)
    if (
        plan.get("protocol") != CASE_PROTOCOL
        or plan.get("source_hashes", {}).get("scripts/run_case_a_scout.py")
        != runner_receipt["sha256"]
    ):
        raise ValueError("Current Case A plan does not bind the current runner")
    job_id = phase.get("slurm_job_id")
    preflight = read(preflight_path)
    smoke = read(smoke_path)
    native = read(native_path)
    server_check = read(server_check_path)
    cleanup = read(cleanup_path)
    validate_preflight_limit_records(preflight)
    if (
        preflight.get("protocol") != SMOKE_PROTOCOL
        or preflight.get("slurm_job_id") != job_id
        or smoke.get("protocol") != SMOKE_PROTOCOL
        or native.get("protocol") != NATIVE_PROTOCOL
        or native.get("slurm_job_id") != job_id
        or server_check.get("protocol") != PROTOCOL
        or server_check.get("slurm_job_id") != job_id
        or server_check.get("server_pid") != phase.get("server_pid")
        or server_check.get("endpoint") != plan.get("config", {}).get("base_url")
        or cleanup.get("protocol") != PROTOCOL
        or cleanup.get("slurm_job_id") != job_id
        or cleanup.get("server_pid") != phase.get("server_pid")
        or type(cleanup.get("case_process", {}).get("pid")) is not int
        or cleanup["case_process"]["pid"] <= 1
    ):
        raise ValueError("Smoke, server, cleanup, or allocation binding differs")
    if binding_validator is None:
        from agentdojo_lab.case_a_scout import recorded_serving_binding

        binding_validator = recorded_serving_binding
    binding = binding_validator(preflight_path, plan["config"]["base_url"])
    if (
        binding.get("status") != "bound_before_case_calls"
        or binding.get("slurm_job_id") != job_id
    ):
        raise ValueError("Recomputed serving binding differs")
    execution = read(execution_path)
    if (
        execution.get("protocol") != CASE_PROTOCOL
        or execution.get("status") != "execution_reserved_before_workers"
        or execution.get("plan") != plan_receipt
        or execution.get("serving") != binding
    ):
        raise ValueError("Case A execution receipt differs from recomputed serving binding")
    case = read(case_summary_path)
    if (
        case.get("protocol") != CASE_PROTOCOL
        or case.get("status") != "all_slots_terminal"
        or case.get("plan") != plan_receipt
        or [slot.get("slot_id") for slot in case.get("slots", [])] != ["clean", "attacked"]
    ):
        raise ValueError("Case A summary protocol, plan, status, or slots differ")
    counts = []
    for condition, slot in zip(("clean", "attacked"), case["slots"], strict=True):
        terminal_path = case_root / f"{condition}-terminal.json"
        terminal = read(terminal_path)
        if (
            slot.get("status") != "terminal"
            or slot.get("terminal") != terminal
            or terminal.get("protocol") != CASE_PROTOCOL
            or terminal.get("condition") != condition
            or terminal.get("plan") != plan_receipt
        ):
            raise ValueError("Case A embedded and on-disk terminal evidence differs")
        count = count_slot_attempts(case_root / condition / "sdk-attempts.jsonl")
        if slot.get("reserved_sdk_attempts") != count:
            raise ValueError("Case A reserved SDK count differs from its attempt ledger")
        counts.append(count)
    if case.get("reserved_sdk_attempts") != sum(counts):
        raise ValueError("Case A total SDK count differs from its slot ledgers")
    return plan, case, counts


def finalize(
    output: Path,
    *,
    phase_path: Path,
    pre_smoke_path: Path,
    runner_path: Path,
    preflight_path: Path,
    smoke_path: Path,
    native_path: Path,
    case_summary_path: Path,
    case_plan_path: Path,
    execution_path: Path,
    wrapper_exit_path: Path,
    wrapper_sha256_path: Path,
    server_check_path: Path,
    cleanup_path: Path,
    binding_validator=None,
) -> dict:
    """Account for every bounded request source without turning failures into success."""
    value: dict = {
        "protocol": PROTOCOL,
        "status": "incomplete",
        "input_paths": {
            "phase": str(phase_path.resolve()),
            "pre_smoke": str(pre_smoke_path.resolve()),
            "runner": str(runner_path.resolve()),
            "preflight": str(preflight_path.resolve()),
            "smoke": str(smoke_path.resolve()),
            "native_smoke": str(native_path.resolve()),
            "case_summary": str(case_summary_path.resolve()),
            "case_plan": str(case_plan_path.resolve()),
            "execution": str(execution_path.resolve()),
            "wrapper_exit": str(wrapper_exit_path.resolve()),
            "wrapper_checksums": str(wrapper_sha256_path.resolve()),
            "server_check": str(server_check_path.resolve()),
            "cleanup": str(cleanup_path.resolve()),
        },
    }
    try:
        smoke_root = smoke_path.parent.resolve()
        require_path(output, smoke_root, "case-a-batch-summary.json")
        require_path(phase_path, smoke_root, "case-a-phase.json")
        require_path(wrapper_exit_path, smoke_root, "case-a-wrapper-exit-code.txt")
        require_path(wrapper_sha256_path, smoke_root, "case-a-wrapper-sha256.txt")
        case_root = case_plan_path.parent.resolve()
        if (
            case_root == smoke_root
            or case_root.is_relative_to(smoke_root)
            or smoke_root.is_relative_to(case_root)
        ):
            raise ValueError("Case and smoke terminal evidence paths must be separate")
        phase = read(phase_path)
        validate_scheduler_decision(phase)
        smoke = read(smoke_path)
        native = read(native_path)
        cleanup = read(cleanup_path)
        wrapper_exit = int(wrapper_exit_path.read_text(encoding="utf-8").strip())
        synthetic_count = smoke.get("requests_started")
        native_count = native.get("native_requests_started")
        value.update(
            phase=receipt(phase_path),
            wrapper_exit=receipt(wrapper_exit_path),
            cleanup=receipt(cleanup_path),
        )
        common_valid = (
            phase.get("protocol") == PROTOCOL
            and cleanup.get("status") == "server_stopped"
            and cleanup.get("protocol") == PROTOCOL
            and cleanup.get("slurm_job_id") == phase.get("slurm_job_id")
            and cleanup.get("server_pid") == phase.get("server_pid")
            and type(phase.get("server_pid")) is int
            and phase["server_pid"] > 1
            and cleanup.get("case_process", {}).get("stopped") is True
            and smoke.get("protocol") == SMOKE_PROTOCOL
            and smoke.get("status") == "passed"
            and synthetic_count == SYNTHETIC_REQUEST_LIMIT
            and native.get("status") == "passed"
            and native.get("protocol") == NATIVE_PROTOCOL
            and native.get("slurm_job_id") == phase.get("slurm_job_id")
            and type(native_count) is int
            and 0 <= native_count <= NATIVE_REQUEST_LIMIT
            and native.get("checks", {}).get("no_online_auditors") is True
        )
        if str(phase.get("status", "")).startswith("unstarted_"):
            validate_unstarted_chain(
                phase=phase,
                pre_smoke_path=pre_smoke_path,
                runner_path=runner_path,
                preflight_path=preflight_path,
                smoke_path=smoke_path,
                native_path=native_path,
                cleanup_path=cleanup_path,
                wrapper_sha256_path=wrapper_sha256_path,
                case_plan_path=case_plan_path,
                binding_validator=binding_validator,
            )
            if not common_valid or wrapper_exit != 3:
                raise ValueError("Unstarted terminal evidence is inconsistent")
            value.update(
                status="terminal_case_unstarted",
                framework_status="case_not_started_after_smoke",
                wrapper_exit_code=wrapper_exit,
                requests={
                    "synthetic": synthetic_count,
                    "native": native_count,
                    "case": 0,
                    "total": synthetic_count + native_count,
                    "limit": TOTAL_REQUEST_LIMIT,
                },
                scientific_outcome={
                    "case_started": False,
                    "reason": phase["status"],
                },
                artifacts={
                    "pre_smoke": receipt(pre_smoke_path),
                    "runner": receipt(runner_path),
                    "preflight": receipt(preflight_path),
                    "plan": receipt(case_plan_path),
                    "smoke": receipt(smoke_path),
                    "native_smoke": receipt(native_path),
                    "wrapper_checksums": receipt(wrapper_sha256_path),
                },
            )
            write_exclusive(output, value)
            return value

        server_check = read(server_check_path)
        value["server_check"] = receipt(server_check_path)
        plan, case, slot_counts = validate_case_chain(
            phase=phase,
            pre_smoke_path=pre_smoke_path,
            runner_path=runner_path,
            preflight_path=preflight_path,
            smoke_path=smoke_path,
            native_path=native_path,
            server_check_path=server_check_path,
            cleanup_path=cleanup_path,
            wrapper_sha256_path=wrapper_sha256_path,
            case_plan_path=case_plan_path,
            execution_path=execution_path,
            case_summary_path=case_summary_path,
            binding_validator=binding_validator,
        )
        case_count = case.get("reserved_sdk_attempts")
        counts = (synthetic_count, native_count, case_count)
        if any(type(count) is not int or count < 0 for count in counts):
            raise ValueError("Request counts must be nonnegative integers")
        total = sum(counts)
        if (
            phase.get("status") != "reserved_before_case_calls"
            or server_check.get("status") != "passed"
            or server_check.get("slurm_job_id") != phase.get("slurm_job_id")
            or server_check.get("endpoint") != plan["config"]["base_url"]
            or not common_valid
            or wrapper_exit != 0
            or any(type(count) is not int or not 0 <= count <= 8 for count in slot_counts)
            or sum(slot_counts) != case_count
            or case_count > CASE_REQUEST_LIMIT
            or total > TOTAL_REQUEST_LIMIT
            or plan.get("limits", {}).get("online_auditor_requests") != 0
            or plan.get("limits", {}).get("sdk_max_retries") != 0
            or plan.get("config", {}).get("online_causal_audit", False) is not False
        ):
            raise ValueError("Smoke-plus-Case-A completion violates its fixed evidence or request bounds")
        value.update(
            status="complete_all_slots_terminal",
            framework_status="case_runner_all_slots_terminal",
            wrapper_exit_code=wrapper_exit,
            requests={
                "synthetic": synthetic_count,
                "native": native_count,
                "case": case_count,
                "total": total,
                "limit": TOTAL_REQUEST_LIMIT,
            },
            artifacts={
                "pre_smoke": receipt(pre_smoke_path),
                "runner": receipt(runner_path),
                "preflight": receipt(preflight_path),
                "smoke": receipt(smoke_path),
                "native_smoke": receipt(native_path),
                "wrapper_checksums": receipt(wrapper_sha256_path),
                "execution": receipt(execution_path),
                "case_summary": receipt(case_summary_path),
                "case_plan": receipt(case_plan_path),
                "slot_terminals": {
                    condition: receipt(case_plan_path.parent / f"{condition}-terminal.json")
                    for condition in ("clean", "attacked")
                },
                "slot_attempts": {
                    condition: receipt(case_plan_path.parent / condition / "sdk-attempts.jsonl")
                    for condition in ("clean", "attacked")
                    if (case_plan_path.parent / condition / "sdk-attempts.jsonl").is_file()
                },
            },
            scientific_outcome={
                "case_started": True,
                "case_summary": receipt(case_summary_path),
                "interpretation": "Use the Case A paired report for scientific outcomes",
            },
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        value["error_type"] = type(error).__name__
    write_exclusive(output, value)
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--output", type=Path, required=True)
    validate.add_argument("--case-dir", type=Path, required=True)
    validate.add_argument("--smoke-dir", type=Path, required=True)
    validate.add_argument("--runner-path", type=Path, required=True)
    validate.add_argument("--site-path", type=Path, required=True)
    validate.add_argument("--site-sha256", required=True)
    validate.add_argument("--manifest-path", type=Path, required=True)
    validate.add_argument("--manifest-sha256", required=True)
    validate.add_argument("--executed-wrapper-path", type=Path, required=True)
    validate.add_argument("--canonical-wrapper-path", type=Path, required=True)
    validate.add_argument("--helper-path", type=Path, action="append", default=[])
    reserve = commands.add_parser("reserve")
    reserve.add_argument("--output", type=Path, required=True)
    reserve.add_argument("--job-id", required=True)
    reserve.add_argument("--reported-job-id", required=True)
    reserve.add_argument("--remaining", required=True)
    reserve.add_argument("--time-limit", required=True)
    reserve.add_argument("--case-dir", type=Path, required=True)
    reserve.add_argument("--server-pid", type=int, required=True)
    reserve.add_argument("--wrapper-sha256-path", type=Path, required=True)
    reserve.add_argument("--pre-smoke-path", type=Path, required=True)
    reserve.add_argument("--runner-path", type=Path, required=True)
    reserve.add_argument("--helper-path", type=Path, action="append", default=[])
    server = commands.add_parser("server-check")
    server.add_argument("--output", type=Path, required=True)
    server.add_argument("--base-url", required=True)
    server.add_argument("--server-pid", type=int, required=True)
    server.add_argument("--job-id", required=True)
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--output", type=Path, required=True)
    cleanup.add_argument("--server-pid", type=int, required=True)
    cleanup.add_argument("--term-sent", choices=("true", "false"), required=True)
    cleanup.add_argument("--kill-sent", choices=("true", "false"), required=True)
    cleanup.add_argument("--stopped", choices=("true", "false"), required=True)
    cleanup.add_argument("--case-pid", type=int, default=0)
    cleanup.add_argument("--case-term-sent", choices=("true", "false"), default="false")
    cleanup.add_argument("--case-kill-sent", choices=("true", "false"), default="false")
    cleanup.add_argument("--case-stopped", choices=("true", "false"), default="true")
    cleanup.add_argument("--job-id", required=True)
    finish = commands.add_parser("finalize")
    for name in (
        "output",
        "phase-path",
        "pre-smoke-path",
        "runner-path",
        "preflight-path",
        "smoke-path",
        "native-path",
        "case-summary-path",
        "case-plan-path",
        "execution-path",
        "wrapper-exit-path",
        "wrapper-sha256-path",
        "server-check-path",
        "cleanup-path",
    ):
        finish.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "validate":
        validate_before_smoke(
            args.output,
            args.case_dir,
            args.smoke_dir,
            args.runner_path,
            args.site_path,
            args.site_sha256,
            args.manifest_path,
            args.manifest_sha256,
            args.executed_wrapper_path,
            args.canonical_wrapper_path,
            args.helper_path,
        )
        return 0
    if args.command == "reserve":
        result = reserve_phase(
            args.output,
            job_id=args.job_id,
            reported_job_id=args.reported_job_id,
            remaining=args.remaining,
            time_limit=args.time_limit,
            case_dir=args.case_dir,
            server_pid=args.server_pid,
            wrapper_sha256_path=args.wrapper_sha256_path,
            pre_smoke_path=args.pre_smoke_path,
            runner_path=args.runner_path,
            helper_paths=args.helper_path,
        )
        return 0 if result["status"] == "reserved_before_case_calls" else 3
    if args.command == "server-check":
        result = check_server(
            args.output,
            base_url=args.base_url,
            key=os.environ.get("LOCAL_LLM_API_KEY", ""),
            server_pid=args.server_pid,
            job_id=args.job_id,
        )
        return 0 if result["status"] == "passed" else 1
    if args.command == "cleanup":
        result = record_cleanup(
            args.output,
            server_pid=args.server_pid,
            term_sent=args.term_sent == "true",
            kill_sent=args.kill_sent == "true",
            stopped=args.stopped == "true",
            case_pid=args.case_pid,
            case_term_sent=args.case_term_sent == "true",
            case_kill_sent=args.case_kill_sent == "true",
            case_stopped=args.case_stopped == "true",
            job_id=args.job_id,
        )
        return 0 if result["status"] == "server_stopped" else 1
    result = finalize(
        args.output,
        phase_path=args.phase_path,
        pre_smoke_path=args.pre_smoke_path,
        runner_path=args.runner_path,
        preflight_path=args.preflight_path,
        smoke_path=args.smoke_path,
        native_path=args.native_path,
        case_summary_path=args.case_summary_path,
        case_plan_path=args.case_plan_path,
        execution_path=args.execution_path,
        wrapper_exit_path=args.wrapper_exit_path,
        wrapper_sha256_path=args.wrapper_sha256_path,
        server_check_path=args.server_check_path,
        cleanup_path=args.cleanup_path,
    )
    return 0 if result["status"] == "complete_all_slots_terminal" else 1


if __name__ == "__main__":
    raise SystemExit(main())
