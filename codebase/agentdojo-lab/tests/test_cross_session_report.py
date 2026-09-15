"""Offline Case C comparison controls; these are not research trajectories."""

import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import pytest

import agentdojo_lab.cross_session_report as cross_session_report
from agentdojo_lab.cross_session_report import export_cross_session_pair

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "cross_session_memory_fixture", ROOT / "scripts/run_memory_pair.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)
sys.path.pop(0)


@pytest.fixture(scope="module")
def memory_pair(tmp_path_factory):
    output = tmp_path_factory.mktemp("cross-session-source") / "pair"
    result = pilot.run_pair(output)
    assert result["completed_sessions"] == 4
    return output


def _export(source, output, *, labels=("clean", "attacked")):
    return export_cross_session_pair(
        source / "neutralized/A",
        source / "neutralized/B",
        source / "original/A",
        source / "original/B",
        output,
        labels=labels,
    )


def _hashes(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def _state_digest(state):
    canonical = json.dumps(
        state, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(canonical).hexdigest()


def _rebase_specs(source):
    for branch in ("neutralized", "original"):
        path = source / branch / "B-spec.json"
        spec = json.loads(path.read_text())
        spec["native_input"] = str(source / branch / "A/native-memory.json")
        spec["lineage_input"] = str(source / branch / "A/lineage-state.json")
        path.write_text(json.dumps(spec))


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.ids = [], [], set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values["href"])


def test_memory_pair_boundary_evidence_and_escaped_links_are_preserved(memory_pair, tmp_path):
    before = _hashes(memory_pair)
    label = 'attacked</pre><script>alert("fixture")</script>'
    output = tmp_path / "report"
    result = _export(memory_pair, output, labels=("clean", label))
    assert result["causal_influence"] == "not_assessed"
    assert result["attack_success"].startswith("unknown")
    for stage in ("A", "B"):
        comparison = result["session_comparisons"][stage]
        assert comparison["alignment"]["status"] == "unique_under_rule"
        assert comparison["arms"][0]["actions"][0]["event_id"] == "event:00000009"
        assert comparison["arms"][1]["actions"][0]["event_id"] == "event:00000009"
    for condition in ("clean", label):
        boundary = result["session_boundaries"][condition]
        assert boundary["identities"]["run"]["status"] == "observed_distinct"
        assert boundary["identities"]["session"]["status"] == "unknown"
        assert boundary["identities"]["process"]["status"] == "observed_distinct"
        assert boundary["identities"]["recorded_episode"]["global_session_identity"] == "unknown"
        assert boundary["identities"]["fresh_b_history"]["status"] == "observed_empty"
        assert boundary["identities"]["fresh_b_history"]["first_model_request_roles"] == [
            "system",
            "user",
        ]
        assert boundary["checkpoint_inputs"]["native_state"]["status"] == "observed_hash_bound"
        assert boundary["checkpoint_inputs"]["lineage_checkpoint"]["status"] == "observed_hash_bound"
        assert boundary["b_spec"]["status"] == "observed_content_bound"
        assert len(boundary["b_spec"]["sha256"]) == 64
        assert len(boundary["b_spec"]["source_content_sha256"]) == 64
        assert set(boundary["consumed_boundary_hashes"]) == {
            "session_a/native-memory.json",
            "session_a/lineage-state.json",
            "session_b/lineage-initial-state.json",
            "session_b_spec/B-spec.json",
        }
        assert boundary["created_file_id_to_b_read_id"]["status"] == "observed_match"
        assert (
            boundary["created_file_id_to_b_read_id"]["proposal_argument_correspondence"]
            == "proposal_argument_match"
        )
        assert boundary["b_actual_source_exposure"]["status"] == "observed"
        memory = boundary["a_memory_write_and_version"]
        assert memory["status"] == "canonical_digest_valid_bound_row_graph_unknown"
        assert memory["checkpoint_integrity"] == "canonical_state_digest_valid"
        assert memory["graph_connectivity"] == "unknown_not_validated"
        assert memory["bound_rows"][0]["version"] == 1
        assert boundary["b_restored_read"]["status"] == "observed"
        assert boundary["b_restored_read"]["recovered_lineage_candidates"]
    assert _hashes(memory_pair) == before
    assert json.loads((output / "cross-session.json").read_text()) == result
    page = Page()
    page.feed((output / "index.html").read_text())
    assert "script" not in page.tags
    assert all(
        unquote(link[1:]) in page.ids
        if link.startswith("#")
        else (output / unquote(link)).resolve().is_file()
        for link in page.links
    )
    assert sum(not link.startswith("#") for link in page.links) == 4


def test_mismatched_and_missing_boundary_evidence_stays_typed(memory_pair, tmp_path):
    source = tmp_path / "mismatch"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    attacked_a = json.loads((source / "original/A/summary.json").read_text())
    attacked_a["created_file_id"] = "different-file"
    (source / "original/A/summary.json").write_text(json.dumps(attacked_a))
    attacked_b = json.loads((source / "original/B/summary.json").read_text())
    attacked_b["input_hashes"]["native_input"] = "0" * 64
    (source / "original/B/summary.json").write_text(json.dumps(attacked_b))
    (source / "neutralized/A/native-memory.json").unlink()
    result = _export(source, tmp_path / "mismatch-report")
    attacked = result["session_boundaries"]["attacked"]
    assert attacked["checkpoint_inputs"]["native_state"]["status"] == "mismatched"
    assert attacked["created_file_id_to_b_read_id"]["status"] == "observed_mismatch"
    clean = result["session_boundaries"]["clean"]
    assert clean["checkpoint_inputs"]["native_state"]["status"] == "unknown"


def test_repeated_calls_report_ambiguous_alignment_and_omission(memory_pair, tmp_path):
    source = tmp_path / "ambiguous"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    events_path = source / "neutralized/B/events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()]
    position = next(
        index for index, event in enumerate(events) if event["event_type"] == "TOOL_CALL_PROPOSED"
    )
    duplicate = copy.deepcopy(events[position])
    duplicate["event_id"] = "event:ambiguous-read"
    duplicate["call_ref"] = "call:ambiguous-read"
    duplicate["event_sequence"] = duplicate["event_sequence"] + 0.5
    events.insert(position + 1, duplicate)
    events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
    result = _export(source, tmp_path / "ambiguous-report")
    alignment = result["session_comparisons"]["B"]["alignment"]
    assert alignment["status"] == "ambiguous"
    assert any(row["status"] == "omitted_in_attacked" for row in alignment["rows"])
    assert {row["clean_event_id"] for row in alignment["rows"]} >= {
        "event:00000009",
        "event:ambiguous-read",
    }


def test_existing_inside_or_reused_sources_are_rejected(memory_pair, tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        _export(memory_pair, output)
    with pytest.raises(ValueError, match="inside"):
        _export(memory_pair, memory_pair / "original/A/derived")
    with pytest.raises(ValueError, match="distinct"):
        export_cross_session_pair(
            memory_pair / "neutralized/A",
            memory_pair / "neutralized/A",
            memory_pair / "original/A",
            memory_pair / "original/B",
            tmp_path / "reused",
        )


def test_input_budget_is_enforced_before_loading(memory_pair, tmp_path, monkeypatch):
    monkeypatch.setattr(cross_session_report, "MAX_ARTIFACT_BYTES", 1)
    with pytest.raises(ValueError, match="exceeds"):
        _export(memory_pair, tmp_path / "bounded")


def test_restored_read_requires_exact_successful_read_call(memory_pair, tmp_path):
    source = tmp_path / "restored-call"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    provenance = source / "original/B/provenance.jsonl"
    rows = [json.loads(line) for line in provenance.read_text().splitlines()]
    restored = next(
        event
        for row in rows
        for event in (row.get("call") or {}).get("lineage", {}).get("memory_events", [])
        if event.get("status") == "lineage_restored"
    )
    restored["call_ref"] = "call:unrelated"
    provenance.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = _export(source, tmp_path / "restored-call-report")
    assert (
        result["session_boundaries"]["attacked"]["b_restored_read"]["status"]
        == "mismatched_call_or_record_key"
    )


def test_no_b_read_never_upgrades_restored_event(memory_pair, tmp_path):
    source = tmp_path / "no-read"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    events = source / "original/B/events.jsonl"
    rows = [json.loads(line) for line in events.read_text().splitlines()]
    rows = [row for row in rows if row.get("event_type") != "TOOL_CALL_PROPOSED" or row.get("data", {}).get("function") != "get_file_by_id"]
    events.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = _export(source, tmp_path / "no-read-report")
    boundary = result["session_boundaries"]["attacked"]
    assert boundary["created_file_id_to_b_read_id"]["status"] == "unknown"
    assert boundary["b_restored_read"]["status"] == "unknown"


@pytest.mark.parametrize("mutation", ["inactive", "wrong_event", "missing_created_id"])
def test_memory_write_requires_valid_binding_and_successful_create(
    memory_pair, tmp_path, mutation
):
    source = tmp_path / f"write-{mutation}"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    if mutation == "missing_created_id":
        summary = source / "original/A/summary.json"
        value = json.loads(summary.read_text())
        value["created_file_id"] = ""
        summary.write_text(json.dumps(value))
    else:
        lineage = source / "original/A/lineage-state.json"
        value = json.loads(lineage.read_text())
        binding = value["state"]["memory_bindings"][0]
        if mutation == "inactive":
            binding["active"] = False
        else:
            binding["confirmed_write_event_id"] = "event:00000012"
        lineage.write_text(json.dumps(value))
        (source / "original/B/lineage-initial-state.json").write_text(json.dumps(value))
        b_summary = source / "original/B/summary.json"
        digest = hashlib.sha256(lineage.read_bytes()).hexdigest()
        summary_value = json.loads(b_summary.read_text())
        summary_value["input_hashes"]["lineage_input"] = digest
        b_summary.write_text(json.dumps(summary_value))
    result = _export(source, tmp_path / f"write-{mutation}-report")
    status = result["session_boundaries"]["attacked"]["a_memory_write_and_version"]["status"]
    assert status == ("unknown" if mutation == "missing_created_id" else "mismatched_or_malformed")


def test_self_consistent_foreign_memory_row_cannot_match_create(memory_pair, tmp_path):
    source = tmp_path / "foreign-row"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    lineage = source / "original/A/lineage-state.json"
    envelope = json.loads(lineage.read_text())
    binding = envelope["state"]["memory_bindings"][0]
    binding["content"] = "self-consistent foreign content"
    binding["content_sha256"] = hashlib.sha256(binding["content"].encode()).hexdigest()
    envelope["state_sha256"] = _state_digest(envelope["state"])
    lineage.write_text(json.dumps(envelope))
    (source / "original/B/lineage-initial-state.json").write_text(json.dumps(envelope))
    b_summary = source / "original/B/summary.json"
    summary = json.loads(b_summary.read_text())
    summary["input_hashes"]["lineage_input"] = hashlib.sha256(lineage.read_bytes()).hexdigest()
    b_summary.write_text(json.dumps(summary))
    result = _export(source, tmp_path / "foreign-row-report")
    boundary = result["session_boundaries"]["attacked"]
    assert boundary["checkpoint_inputs"]["lineage_checkpoint"]["status"] == "observed_hash_bound"
    memory = boundary["a_memory_write_and_version"]
    assert memory["checkpoint_integrity"] == "canonical_state_digest_valid"
    assert memory["status"] == "mismatched_or_malformed"
    assert memory["bound_rows"] == []


def test_missing_memory_node_stays_graph_unknown_after_recomputed_digest(
    memory_pair, tmp_path
):
    source = tmp_path / "missing-node"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    lineage = source / "original/A/lineage-state.json"
    envelope = json.loads(lineage.read_text())
    node_id = envelope["state"]["memory_bindings"][0]["node_id"]
    envelope["state"]["nodes"] = [
        node for node in envelope["state"]["nodes"] if node.get("node_id") != node_id
    ]
    envelope["state_sha256"] = _state_digest(envelope["state"])
    lineage.write_text(json.dumps(envelope))
    (source / "original/B/lineage-initial-state.json").write_text(json.dumps(envelope))
    b_summary = source / "original/B/summary.json"
    summary = json.loads(b_summary.read_text())
    summary["input_hashes"]["lineage_input"] = hashlib.sha256(lineage.read_bytes()).hexdigest()
    b_summary.write_text(json.dumps(summary))
    result = _export(source, tmp_path / "missing-node-report")
    memory = result["session_boundaries"]["attacked"]["a_memory_write_and_version"]
    assert memory["status"] == "canonical_digest_valid_bound_row_graph_unknown"
    assert memory["checkpoint_integrity"] == "canonical_state_digest_valid"
    assert memory["graph_connectivity"] == "unknown_not_validated"
    assert "observed_versioned_lineage_binding" not in json.dumps(result)


def test_mutated_visible_tool_result_record_downgrades_memory_row(memory_pair, tmp_path):
    source = tmp_path / "mutated-visible-result"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    events = source / "original/A/events.jsonl"
    rows = [json.loads(line) for line in events.read_text().splitlines()]
    result_event = next(
        row
        for row in rows
        if row.get("event_type") == "TOOL_RESULT" and row.get("call_ref") == "call:00000018"
    )
    result_event["data"]["message"]["content"][0]["content"] = (
        "content: 'foreign visible content'\nfilename: session-memory.txt\nid_: '2'"
    )
    events.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = _export(source, tmp_path / "mutated-visible-result-report")
    memory = result["session_boundaries"]["attacked"]["a_memory_write_and_version"]
    assert memory["checkpoint_integrity"] == "canonical_state_digest_valid"
    assert memory["status"] == "mismatched_or_malformed"
    assert memory["bound_rows"] == []


@pytest.mark.parametrize("contradiction", ["summary", "request"])
def test_fresh_history_requires_summary_and_first_request_agreement(
    memory_pair, tmp_path, contradiction
):
    source = tmp_path / f"history-{contradiction}"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    if contradiction == "summary":
        summary = source / "original/B/summary.json"
        value = json.loads(summary.read_text())
        value["initial_history_empty"] = False
        summary.write_text(json.dumps(value))
    else:
        events = source / "original/B/events.jsonl"
        rows = [json.loads(line) for line in events.read_text().splitlines()]
        request = next(row for row in rows if row.get("event_type") == "MODEL_REQUEST")
        request["data"]["body"]["messages"].insert(
            1, {"role": "assistant", "content": "prior session text"}
        )
        events.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = _export(source, tmp_path / f"history-{contradiction}-report")
    history = result["session_boundaries"]["attacked"]["identities"]["fresh_b_history"]
    assert history["status"] == "mismatched_summary_and_first_request"


def test_created_read_match_requires_successful_runtime_return(memory_pair, tmp_path):
    source = tmp_path / "failed-read"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    events = source / "original/B/events.jsonl"
    rows = [json.loads(line) for line in events.read_text().splitlines()]
    returned = next(
        row
        for row in rows
        if row.get("event_type") == "TOOL_RUNTIME_RETURNED"
        and row.get("call_ref") == "call:00000008"
    )
    returned["data"]["error"] = "fixture failure"
    events.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = _export(source, tmp_path / "failed-read-report")
    evidence = result["session_boundaries"]["attacked"]["created_file_id_to_b_read_id"]
    assert evidence["proposal_argument_correspondence"] == "proposal_argument_match"
    assert evidence["successful_execution_correspondence"] == "none_observed"
    assert evidence["status"] != "observed_match"
    assert result["session_boundaries"]["attacked"]["b_restored_read"]["status"] == "none_observed"


@pytest.mark.parametrize("failure", ["incomplete", "invalid_audit"])
def test_invalid_or_incomplete_recording_cannot_upgrade_exposure(
    memory_pair, tmp_path, failure
):
    source = tmp_path / failure
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    if failure == "incomplete":
        summary = source / "original/B/summary.json"
        value = json.loads(summary.read_text())
        value["recording"]["complete"] = False
        summary.write_text(json.dumps(value))
    else:
        events = source / "original/B/events.jsonl"
        rows = [json.loads(line) for line in events.read_text().splitlines()]
        rows[0]["event_sequence"] = 999
        events.write_text("".join(json.dumps(row) + "\n" for row in rows))
    output = tmp_path / f"{failure}-report"
    result = _export(source, output)
    exposure = result["session_boundaries"]["attacked"]["b_actual_source_exposure"]
    assert exposure["events"]
    assert exposure["status"] == "unknown"
    history = result["session_boundaries"]["attacked"]["identities"]["fresh_b_history"]
    assert history["status"] == "unknown"
    page = (output / "index.html").read_text()
    assert "Candidate B exposure [unknown]" in page
    assert "Candidate B restored read [unknown]" in page


def test_per_run_report_symlink_is_rejected(memory_pair, tmp_path):
    source = tmp_path / "symlink"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    report = source / "original/B/report.html"
    report.unlink()
    report.symlink_to(source / "original/A/report.html")
    with pytest.raises(ValueError, match="symlink"):
        _export(source, tmp_path / "symlink-report")


def test_native_tree_entry_cap_short_circuits(memory_pair, tmp_path, monkeypatch):
    source = tmp_path / "native-cap"
    shutil.copytree(memory_pair, source)
    _rebase_specs(source)
    (source / "neutralized/A/native/extra.txt").write_text("extra")
    monkeypatch.setattr(cross_session_report, "MAX_NATIVE_ENTRIES", 1)
    with pytest.raises(ValueError, match="native tree"):
        _export(source, tmp_path / "native-cap-report")
