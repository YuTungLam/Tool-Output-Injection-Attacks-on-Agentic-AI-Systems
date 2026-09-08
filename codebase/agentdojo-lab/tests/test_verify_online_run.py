"""Saved sidecar verification against actual offline runs and inconsistent evidence."""

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from agentdojo_lab.runner import RunConfig, run_clean

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_online_run.py"
SPEC = importlib.util.spec_from_file_location("verify_online_run_under_test", SCRIPT)
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


@pytest.fixture(scope="module")
def source_run(tmp_path_factory):
    path = tmp_path_factory.mktemp("online-source") / "run"
    result = run_clean(RunConfig(online_provenance=True), offline=True, output=path)
    assert result["recording"]["complete"] is True
    assert result["online_provenance"]["complete"] is True
    return path


@pytest.fixture
def copied_run(source_run, tmp_path):
    path = tmp_path / "run"
    shutil.copytree(source_run, path)
    return path


def rows_at(run):
    return [json.loads(line) for line in (run / "provenance.jsonl").read_text().splitlines()]


def write_rows(run, rows, *, relink_hashes=False):
    """Optionally update hashes, so semantic/identity checks cannot hide behind a stale digest."""
    raw = [json.dumps(row, sort_keys=True) + "\n" for row in rows]
    if relink_hashes:
        by_sequence = {row["record_sequence"]: index for index, row in enumerate(rows)}
        for index, row in enumerate(rows):
            if row["record_type"] == "analysis_flush":
                analysis = by_sequence[row["analysis_record_sequence"]]
                row["analysis_line_sha256"] = hashlib.sha256(raw[analysis].encode()).hexdigest()
                raw[index] = json.dumps(row, sort_keys=True) + "\n"
    (run / "provenance.jsonl").write_text("".join(raw))


def select(rows, kind):
    return next(row for row in rows if row["record_type"] == kind)


def test_offline_run_verifies_without_changing_any_source_files(source_run, monkeypatch):
    hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_run.rglob("*") if p.is_file()
    }
    monkeypatch.setattr(verifier, "LocalMiniLMEncoder", lambda *a, **k: pytest.fail("No encoder configured"))
    result = verifier.verify(source_run)
    assert result["passed"] is True and all(result["checks"].values())
    assert result["real_llm"] is False
    assert result["proposal_count"] == result["runtime_count"] == 1
    assert result["semantic_comparison_count"] == 0
    assert hashes == {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_run.rglob("*") if p.is_file()
    }


@pytest.mark.parametrize("kind", ["call_analysis", "analysis_flush"])
def test_availability_must_be_the_exact_live_contract(copied_run, kind):
    rows = rows_at(copied_run)
    row = select(rows, kind)
    container = row["call"] if kind == "call_analysis" else row
    container["availability"] = "live_synchronous_sidecar; actually_offline; future_data_allowed"
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


def test_changed_call_content_fails_even_with_recomputed_receipt_hash(copied_run):
    rows = rows_at(copied_run)
    select(rows, "call_analysis")["call"]["fields"][0]["value"] = "not the observed argument"
    write_rows(copied_run, rows, relink_hashes=True)
    result = verifier.verify(copied_run)
    assert result["checks"]["flush_receipt_hashes_match"] is True
    assert result["checks"]["live_equals_replay_except_availability"] is False
    assert result["passed"] is False


def test_replay_comparison_preserves_json_number_types(copied_run):
    rows = rows_at(copied_run)
    call = select(rows, "call_analysis")["call"]
    call["request_sequence"] = float(call["request_sequence"])
    write_rows(copied_run, rows, relink_hashes=True)
    result = verifier.verify(copied_run)
    assert result["checks"]["live_equals_replay_except_availability"] is False
    assert result["passed"] is False


def test_receipt_hash_is_checked_against_exact_persisted_analysis_bytes(copied_run):
    rows = rows_at(copied_run)
    select(rows, "analysis_flush")["analysis_line_sha256"] = "0" * 64
    write_rows(copied_run, rows)
    result = verifier.verify(copied_run)
    assert result["checks"]["flush_receipt_hashes_match"] is False
    assert result["passed"] is False


@pytest.mark.parametrize("kind", ["call_analysis", "analysis_flush", "runtime_timing"])
def test_top_level_identity_cannot_disagree_with_the_linked_event(copied_run, kind):
    rows = rows_at(copied_run)
    select(rows, kind)["episode_id"] = "episode:another"
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


@pytest.mark.parametrize("field", ["analysis_record_sequence", "receipt_record_sequence"])
def test_runtime_record_must_link_the_same_analysis_and_receipt(copied_run, field):
    rows = rows_at(copied_run)
    select(rows, "runtime_timing")[field] = 987654
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


def test_boolean_is_not_an_analysis_sequence_number(copied_run):
    rows = rows_at(copied_run)
    assert select(rows, "call_analysis")["record_sequence"] == 1
    select(rows, "runtime_timing")["analysis_record_sequence"] = True
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


@pytest.mark.parametrize(
    "mutation", ["negative", "reversed", "different_copy", "bool_clock", "wrong_elapsed"]
)
def test_proposal_and_receipt_compute_timestamps_are_consistent(copied_run, mutation):
    rows = rows_at(copied_run)
    analysis = select(rows, "call_analysis")["timing"]
    receipt = select(rows, "analysis_flush")["timing"]
    if mutation == "negative":
        analysis["consume_started_monotonic_ns"] = -20
        analysis["compute_completed_monotonic_ns"] = -10
        analysis["compute_elapsed_ns"] = 10
        receipt["consume_started_monotonic_ns"] = -20
        receipt["compute_completed_monotonic_ns"] = -10
    elif mutation == "reversed":
        analysis["compute_completed_monotonic_ns"] = analysis["consume_started_monotonic_ns"] - 1
        receipt["compute_completed_monotonic_ns"] = analysis["compute_completed_monotonic_ns"]
    elif mutation == "different_copy":
        receipt["compute_completed_monotonic_ns"] += 1
    elif mutation == "bool_clock":
        analysis["consume_started_monotonic_ns"] = True
        receipt["consume_started_monotonic_ns"] = True
    else:
        receipt["compute_and_analysis_flush_elapsed_ns"] += 1
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


@pytest.mark.parametrize("mutation", ["late", "different_event_clock", "receipt_before_analysis", "bad_lead"])
def test_runtime_timestamps_establish_recorded_boundary_availability(copied_run, mutation):
    rows = rows_at(copied_run)
    runtime = select(rows, "runtime_timing")
    timing = runtime["timing"]
    if mutation == "late":
        timing["receipt_flushed_monotonic_ns"] = runtime["runtime_event_monotonic_ns"] + 1
    elif mutation == "different_event_clock":
        runtime["runtime_event_monotonic_ns"] += 1
    elif mutation == "receipt_before_analysis":
        timing["receipt_flushed_monotonic_ns"] = timing["analysis_flushed_monotonic_ns"] - 1
    else:
        timing["analysis_lead_ns"] += 1
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


@pytest.mark.parametrize("kind", ["call_analysis", "analysis_flush", "runtime_timing"])
@pytest.mark.parametrize("mutation", ["missing", "duplicate"])
def test_missing_or_duplicate_required_rows_fail(copied_run, kind, mutation):
    rows = rows_at(copied_run)
    row = select(rows, kind)
    if mutation == "missing":
        rows.remove(row)
    else:
        rows.append({**row, "record_sequence": len(rows) + 1})
    write_rows(copied_run, rows)
    assert verifier.verify(copied_run)["passed"] is False


def test_unsupported_extra_row_is_not_ignored(copied_run):
    rows = rows_at(copied_run)
    rows.append({"schema_version": 1, "record_sequence": len(rows) + 1, "record_type": "unsupported"})
    write_rows(copied_run, rows, relink_hashes=True)
    assert verifier.verify(copied_run)["passed"] is False


def test_summary_cannot_claim_different_sidecar_counts(copied_run):
    path = copied_run / "summary.json"
    summary = json.loads(path.read_text())
    summary["online_provenance"]["analysis_count"] += 1
    path.write_text(json.dumps(summary))
    assert verifier.verify(copied_run)["passed"] is False
