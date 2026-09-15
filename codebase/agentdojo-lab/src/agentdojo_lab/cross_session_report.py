"""Bounded, offline comparison of caller-labelled two-session run pairs.

The exporter describes recorded actions and session-boundary evidence. It never
infers causal influence, hidden reasoning, maliciousness, or attack success.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

import yaml

from agentdojo_lab.html_report import collect_run_record
from agentdojo_lab.paired_report import compare_records

MAX_ARTIFACT_BYTES = 32 * 1024 * 1024
MAX_RUN_INPUT_BYTES = 64 * 1024 * 1024
MAX_NATIVE_JSON_FILES = 128
MAX_NATIVE_ENTRIES = 512
SCOPE = (
    "Offline descriptive comparison of two ordered sessions per caller-labelled condition. "
    "Actions are aligned independently within session A and session B using the displayed "
    "edit rule. Event IDs, call IDs, episode IDs, and action indices remain local to their "
    "recorded run. Session-boundary fields report only direct identity, content-hash, native "
    "file, event, and lineage evidence. Missing evidence is unknown. Correspondence, lineage "
    "candidates, and clean/attacked differences do not establish causal influence, hidden "
    "reasoning, maliciousness, or attack success. Condition labels are supplied by the caller."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode()


def _validate_run_budget(path: Path):
    if not path.is_dir():
        raise ValueError(f"Run directory does not exist: {path}")
    candidates = [
        path / name
        for name in (
            "manifest.json",
            "summary.json",
            "events.jsonl",
            "provenance.jsonl",
            "causal-online.jsonl",
            "causal-online-graph.json",
            "lineage-state.json",
        )
    ]
    native = []
    native_root = path / "native"
    if native_root.is_symlink():
        raise ValueError(f"Run native input must not be a symlink: {native_root}")
    if native_root.is_dir():
        stack = [native_root]
        entry_count = 0
        while stack:
            directory = stack.pop()
            with os.scandir(directory) as entries:
                for entry in entries:
                    entry_count += 1
                    if entry_count > MAX_NATIVE_ENTRIES:
                        raise ValueError(f"Run native tree has more than {MAX_NATIVE_ENTRIES} entries")
                    candidate = Path(entry.path)
                    if entry.is_symlink():
                        raise ValueError(f"Run native input contains a symlink: {candidate}")
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(candidate)
                    elif entry.is_file(follow_symlinks=False) and candidate.suffix == ".json":
                        native.append(candidate)
                        if len(native) > MAX_NATIVE_JSON_FILES:
                            raise ValueError(
                                f"Run has more than {MAX_NATIVE_JSON_FILES} native JSON artifacts"
                            )
    total = 0
    for candidate in [*candidates, *native]:
        if not candidate.exists():
            continue
        if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(path):
            raise ValueError(f"Run input is not a regular in-source file: {candidate}")
        size = candidate.stat().st_size
        if size > MAX_ARTIFACT_BYTES:
            raise ValueError(f"Run input exceeds {MAX_ARTIFACT_BYTES} bytes: {candidate}")
        total += size
    if total > MAX_RUN_INPUT_BYTES:
        raise ValueError(f"Run inputs exceed the {MAX_RUN_INPUT_BYTES}-byte aggregate budget: {path}")


def _optional_json(path: Path, root: Path, consumed: dict[Path, str]):
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Optional boundary artifact is not a regular in-source file: {path}")
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError(f"Optional boundary artifact exceeds {MAX_ARTIFACT_BYTES} bytes: {path}")
    raw = path.read_bytes()
    consumed[path.resolve()] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise ValueError(f"Cannot parse optional boundary artifact: {path}") from exc


def _status_for_identity(values, *, local=False):
    if any(value is None for value in values):
        status = "unknown"
    elif values[0] != values[1]:
        status = "observed_distinct"
    else:
        status = "same_recorded_identifier"
    return {
        "status": status,
        "session_a": values[0],
        "session_b": values[1],
        **(
            {
                "scope": "run-local identifier; equality or difference does not establish process identity"
            }
            if local
            else {}
        ),
    }


def _episode_ids(record):
    return sorted(
        {
            event.get("episode_id")
            for event in record["events"]
            if isinstance(event.get("episode_id"), str)
        }
    )


def _event_run_ids(record):
    return sorted(
        {
            event.get("run_id")
            for event in record["events"]
            if isinstance(event.get("run_id"), str)
        }
    )


def _recorded_identity_values(record, key):
    values = {
        value
        for value in (record["summary"].get(key), record["manifest"].get(key))
        if isinstance(value, (str, int)) and not isinstance(value, bool)
    }
    values.update(
        event[key]
        for event in record["events"]
        if isinstance(event.get(key), (str, int)) and not isinstance(event.get(key), bool)
    )
    return sorted(values, key=str)


def _process_id(record):
    summary_pid = record["summary"].get("pid")
    manifest_pid = record["manifest"].get("pid")
    if summary_pid is not None and manifest_pid is not None and summary_pid != manifest_pid:
        return None, "mismatched_summary_and_manifest_pid"
    value = summary_pid if summary_pid is not None else manifest_pid
    return value, None


def _fresh_history(record):
    summary_flag = record["summary"].get("initial_history_empty")
    requests = sorted(
        (event for event in record["events"] if event.get("event_type") == "MODEL_REQUEST"),
        key=lambda event: (
            event.get("event_sequence")
            if isinstance(event.get("event_sequence"), int)
            else float("inf")
        ),
    )
    first = requests[0] if requests else None
    body = (first.get("data") or {}).get("body") if first else None
    messages = body.get("messages") if isinstance(body, dict) else None
    valid_messages = bool(
        isinstance(messages, list)
        and all(isinstance(message, dict) and isinstance(message.get("role"), str) for message in messages)
    )
    if not _recording_healthy(record) or not valid_messages:
        status = "unknown"
        roles = None
        derived_empty = None
    else:
        roles = [message.get("role") if isinstance(message, dict) else None for message in messages]
        derived_empty = all(role not in {"assistant", "tool"} for role in roles)
        if not isinstance(summary_flag, bool):
            status = "unknown"
        elif derived_empty != summary_flag:
            status = "mismatched_summary_and_first_request"
        else:
            status = "observed_empty" if derived_empty else "observed_not_empty"
    return {
        "status": status,
        "summary_initial_history_empty": summary_flag,
        "first_model_request_event_id": first.get("event_id") if first else None,
        "first_model_request_roles": roles,
        "derived_no_prior_assistant_or_tool_history": derived_empty,
        "contract": "first recorded model request contains no assistant or tool role",
    }


def _input_binding(
    *,
    name: str,
    artifact: Path,
    b_record: dict,
    b_spec: dict | None,
    spec_key: str,
    copied: Path | None,
    consumed: dict[Path, str],
):
    actual = consumed.get(artifact.resolve())
    recorded = (b_record["summary"].get("input_hashes") or {}).get(spec_key)
    spec_path = b_spec.get(spec_key) if isinstance(b_spec, dict) else None
    spec_resolves_to_a = None
    if isinstance(spec_path, str):
        spec_resolves_to_a = Path(spec_path).expanduser().resolve() == artifact.resolve()
    copied_hash = consumed.get(copied.resolve()) if copied is not None and copied.exists() else None
    contradictions = [
        actual is not None and recorded is not None and actual != recorded,
        spec_resolves_to_a is False,
        name == "lineage_checkpoint" and copied_hash is not None and actual is not None and copied_hash != actual,
    ]
    if any(contradictions):
        status = "mismatched"
    elif actual is not None and recorded is not None and actual == recorded:
        status = "observed_hash_bound"
    else:
        status = "unknown"
    return {
        "status": status,
        "a_artifact": artifact.name,
        "a_sha256": actual,
        "b_recorded_input_key": spec_key,
        "b_recorded_sha256": recorded,
        "b_spec_path": spec_path,
        "b_spec_resolves_to_a_artifact": spec_resolves_to_a,
        "b_copied_input_sha256": copied_hash,
    }


def _read_actions(session_comparison: dict, arm_index: int):
    return session_comparison["arms"][arm_index]["actions"]


def _read_ids(actions):
    reads = [
        {
            "action_index": index,
            "event_id": action.get("event_id"),
            "call_ref": action.get("call_ref"),
            "file_id": (action.get("arguments") or {}).get("file_id"),
            "execution_status": (action.get("execution") or {}).get("status"),
        }
        for index, action in enumerate(actions)
        if action.get("function") == "get_file_by_id"
    ]
    return reads


def _recording_healthy(record):
    return (record.get("audit") or {}).get("valid") is True and record["summary"].get(
        "recording", {}
    ).get("complete") is True


def _created_to_read(a_record, b_record, reads):
    created = a_record["summary"].get("created_file_id")
    ids = [row["file_id"] for row in reads if row["file_id"] is not None]
    successful = [row for row in reads if row["execution_status"] == "returned_successfully"]
    successful_ids = [row["file_id"] for row in successful if row["file_id"] is not None]
    if not created or not ids:
        proposal_status = "unknown"
    elif len(ids) != 1:
        proposal_status = "ambiguous_multiple_b_read_proposals"
    elif ids[0] == created:
        proposal_status = "proposal_argument_match"
    else:
        proposal_status = "proposal_argument_mismatch"
    healthy = _recording_healthy(b_record)
    if not created or not reads or not healthy:
        execution_status = "unknown"
    elif not successful_ids:
        execution_status = "none_observed"
    elif len(successful_ids) != 1:
        execution_status = "ambiguous_multiple_successful_b_reads"
    elif successful_ids[0] == created:
        execution_status = "observed_match"
    else:
        execution_status = "observed_mismatch"
    return {
        "status": execution_status,
        "proposal_argument_correspondence": proposal_status,
        "successful_execution_correspondence": execution_status,
        "a_created_file_id": created,
        "b_read_actions": reads,
    }


def _source_exposure(b_record, reads):
    read_refs = {row["call_ref"] for row in reads if row["call_ref"]}
    rows = [
        {
            "event_id": event.get("event_id"),
            "event_sequence": event.get("event_sequence"),
            "call_ref": event.get("call_ref"),
            "model_request_id": event.get("model_request_id"),
            "source_result_event_id": (event.get("data") or {}).get("source_result_event_id"),
            "semantics": (event.get("data") or {}).get("semantics"),
        }
        for event in b_record["events"]
        if event.get("event_type") == "TOOL_OUTPUT_EXPOSED" and event.get("call_ref") in read_refs
    ]
    healthy = _recording_healthy(b_record)
    status = "observed" if rows and healthy else "none_observed" if healthy and reads else "unknown"
    return {
        "status": status,
        "scope": "included_in_recorded_outbound_model_request; server receipt is not inferred",
        "events": rows,
    }


def _memory_rows(record):
    checkpoint = record.get("lineage_state")
    if not isinstance(checkpoint, dict):
        return "unknown", []
    state = checkpoint.get("state")
    expected = checkpoint.get("state_sha256")
    if not isinstance(state, dict) or not _valid_content_hash(expected):
        return "mismatched_or_malformed", []
    try:
        actual = hashlib.sha256(_canonical(state)).hexdigest()
    except (TypeError, ValueError):
        return "mismatched_or_malformed", []
    if actual != expected:
        return "digest_mismatch", []
    rows = state.get("memory_bindings")
    if not isinstance(rows, list):
        return "mismatched_or_malformed", []
    return "canonical_state_digest_valid", rows


def _valid_content_hash(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _single_visible_tool_result_record(event):
    message = (event.get("data") or {}).get("message") if isinstance(event, dict) else None
    if not isinstance(message, dict) or message.get("role") != "tool" or message.get("error") is not None:
        return None
    content = message.get("content")
    if isinstance(content, str):
        texts = [content]
    elif isinstance(content, list) and len(content) == 1:
        part = content[0]
        text = part.get("text", part.get("content")) if isinstance(part, dict) else None
        texts = [text] if isinstance(text, str) and part.get("type") == "text" else []
    else:
        texts = []
    if len(texts) != 1:
        return None
    try:
        value = yaml.safe_load(texts[0])
    except (TypeError, yaml.YAMLError):
        return None
    return value if isinstance(value, dict) else None


def _memory_write(a_record, actions):
    created = a_record["summary"].get("created_file_id")
    successful_actions = {
        action.get("call_ref"): action
        for action in actions
        if action.get("function") == "create_file"
        and (action.get("execution") or {}).get("status") == "returned_successfully"
        and action.get("call_ref")
    }
    event_by_id = {
        event.get("event_id"): event for event in a_record["events"] if event.get("event_id")
    }
    checkpoint_integrity, all_bindings = _memory_rows(a_record)
    candidates = [
        row
        for row in all_bindings
        if isinstance(row, dict) and created and row.get("record_key") == created
    ]
    bindings = []
    malformed = []
    for row in candidates:
        confirmed = event_by_id.get(row.get("confirmed_write_event_id"))
        successful_action = (
            successful_actions.get(confirmed.get("call_ref")) if confirmed else None
        )
        runtime_return_refs = (successful_action or {}).get("execution", {}).get(
            "runtime_returns", []
        )
        runtime_returns = [
            event_by_id.get(reference.get("event_id")) for reference in runtime_return_refs
        ]
        runtime_return = runtime_returns[0] if len(runtime_returns) == 1 else None
        runtime_result = (
            (runtime_return.get("data") or {}).get("result")
            if isinstance(runtime_return, dict)
            else None
        )
        arguments = (successful_action or {}).get("arguments")
        proposal_event = (
            event_by_id.get(successful_action.get("event_id")) if successful_action else None
        )
        confirmed_call = (
            ((confirmed.get("data") or {}).get("message") or {}).get("tool_call")
            if confirmed
            else None
        )
        visible_record = _single_visible_tool_result_record(confirmed)
        confirmed_sequence = confirmed.get("event_sequence") if confirmed else None
        return_sequences = [
            returned.get("event_sequence")
            for returned in (successful_action or {}).get("execution", {}).get("runtime_returns", [])
        ]
        ordered_after_returns = bool(
            isinstance(confirmed_sequence, int)
            and return_sequences
            and all(
                isinstance(sequence, int) and sequence < confirmed_sequence
                for sequence in return_sequences
            )
        )
        content = row.get("content")
        content_hash_matches = bool(
            isinstance(content, str)
            and _valid_content_hash(row.get("content_sha256"))
            and hashlib.sha256(content.encode("utf-8")).hexdigest() == row["content_sha256"]
        )
        valid = bool(
            row.get("active") is True
            and len(candidates) == 1
            and isinstance(row.get("version"), int)
            and not isinstance(row.get("version"), bool)
            and row["version"] > 0
            and content_hash_matches
            and isinstance(row.get("confirmed_write_event_id"), str)
            and isinstance(row.get("node_id"), str)
            and row.get("node_id")
            and confirmed
            and confirmed.get("event_type") == "TOOL_RESULT"
            and confirmed.get("call_ref") in successful_actions
            and ordered_after_returns
            and isinstance(arguments, dict)
            and isinstance(runtime_result, dict)
            and runtime_result.get("id_") == created == row.get("record_key")
            and runtime_result.get("content") == arguments.get("content") == content
            and runtime_result.get("filename") == arguments.get("filename")
            and isinstance(confirmed_call, dict)
            and confirmed_call.get("function") == "create_file"
            and confirmed_call.get("args") == arguments
            and isinstance(visible_record, dict)
            and visible_record.get("id_") == runtime_result.get("id_") == row.get("record_key")
            and visible_record.get("content") == runtime_result.get("content") == content
            and visible_record.get("filename") == runtime_result.get("filename")
            and isinstance(proposal_event, dict)
            and row.get("run_id") == proposal_event.get("run_id")
            and row.get("episode_id") == proposal_event.get("episode_id")
            and successful_action.get("event_id") in confirmed.get("parent_event_ids", [])
            and runtime_return.get("event_id") in confirmed.get("parent_event_ids", [])
            and _recording_healthy(a_record)
        )
        selected = {
            key: row.get(key)
            for key in (
                "record_key",
                "version",
                "content_sha256",
                "confirmed_write_event_id",
                "run_id",
                "episode_id",
                "node_id",
                "active",
            )
        }
        selected["bound_successful_create_call_ref"] = (
            confirmed.get("call_ref")
            if confirmed and confirmed.get("call_ref") in successful_actions
            else None
        )
        selected["visible_tool_result_record"] = {
            key: visible_record.get(key) for key in ("id_", "content", "filename")
        } if isinstance(visible_record, dict) else None
        (bindings if valid else malformed).append(selected)
    if bindings and checkpoint_integrity == "canonical_state_digest_valid":
        status = "canonical_digest_valid_bound_row_graph_unknown"
    elif checkpoint_integrity not in {"canonical_state_digest_valid", "unknown"} or malformed or (created and all_bindings):
        status = "mismatched_or_malformed"
    else:
        status = "unknown"
    return {
        "status": status,
        "checkpoint_integrity": checkpoint_integrity,
        "graph_connectivity": "unknown_not_validated",
        "created_file_id": created,
        "bound_rows": bindings,
        "rejected_rows": malformed,
    }


def _restored_reads(b_record, reads):
    successful = {
        row["call_ref"]: row["file_id"]
        for row in reads
        if row["call_ref"]
        and row["file_id"] is not None
        and row["execution_status"] == "returned_successfully"
    }
    events = []
    recovered = []
    for row in b_record.get("provenance", []):
        call = row.get("call") if row.get("record_type") == "call_analysis" else None
        lineage = call.get("lineage") if isinstance(call, dict) else None
        if not isinstance(lineage, dict):
            continue
        for event in lineage.get("memory_events", []):
            if isinstance(event, dict) and event.get("status") == "lineage_restored":
                events.append(
                    {
                        key: event.get(key)
                        for key in (
                            "event_id",
                            "call_ref",
                            "record_key",
                            "version",
                            "run_id",
                            "episode_id",
                            "status",
                            "label_count",
                        )
                    }
                )
        for source in lineage.get("recovered_sources", []):
            if isinstance(source, dict):
                recovered.append(
                    {
                        key: source.get(key)
                        for key in (
                            "record_key",
                            "version",
                            "carrier_event_id",
                            "carrier_source_id",
                            "origin_source_id",
                            "content_sha256",
                            "path_edge_ids",
                        )
                    }
                )
    matching = [
        event
        for event in events
        if event["call_ref"] in successful and event["record_key"] == successful[event["call_ref"]]
    ]
    complete = b_record["summary"].get("online_provenance", {}).get("complete") is True
    healthy = _recording_healthy(b_record)
    if matching and complete and healthy:
        status = "observed"
    elif events and successful and complete and healthy:
        status = "mismatched_call_or_record_key"
    elif reads and complete and healthy:
        status = "none_observed"
    else:
        status = "unknown"
    return {
        "status": status,
        "restored_read_events": events,
        "events_matching_recorded_b_read_ids": matching,
        "recovered_lineage_candidates": recovered,
        "interpretation": "recorded restored ancestry candidates; causal influence is not assessed",
    }


def _b_spec_evidence(b_record, reads, artifacts):
    spec = artifacts["b_spec_value"]
    spec_path = artifacts["b_spec_path"]
    artifact_sha = artifacts["consumed"].get(spec_path.resolve())
    if not isinstance(spec, dict):
        return {"status": "unknown", "artifact": spec_path.name, "sha256": artifact_sha}
    content = spec.get("source_content")
    source_id = spec.get("source_id")
    content_sha = (
        hashlib.sha256(content.encode("utf-8")).hexdigest() if isinstance(content, str) else None
    )
    successful_refs = {
        row["call_ref"]
        for row in reads
        if row["call_ref"]
        and row["file_id"] == source_id
        and row["execution_status"] == "returned_successfully"
    }
    returns = [
        event
        for event in b_record["events"]
        if event.get("event_type") == "TOOL_RUNTIME_RETURNED"
        and event.get("call_ref") in successful_refs
    ]
    returned = [
        (event.get("data") or {}).get("result") for event in returns if isinstance((event.get("data") or {}).get("result"), dict)
    ]
    matching = [
        value
        for value in returned
        if value.get("id_") == source_id and value.get("content") == content
    ]
    if artifact_sha and matching and _recording_healthy(b_record):
        status = "observed_content_bound"
    elif returned and not matching:
        status = "mismatched"
    else:
        status = "unknown"
    return {
        "status": status,
        "artifact": spec_path.name,
        "sha256": artifact_sha,
        "stage": spec.get("stage"),
        "source_id": source_id,
        "source_content": content,
        "source_content_sha256": content_sha,
        "successful_read_return_event_ids": [event.get("event_id") for event in returns],
    }


def _boundary(
    a_record,
    b_record,
    session_comparisons,
    arm_index,
    artifacts,
):
    a_pid, a_pid_error = _process_id(a_record)
    b_pid, b_pid_error = _process_id(b_record)
    process = _status_for_identity([a_pid, b_pid])
    if a_pid_error or b_pid_error:
        process["status"] = "mismatched_recorded_pid_fields"
    process["field_errors"] = [error for error in (a_pid_error, b_pid_error) if error]
    a_actions = _read_actions(session_comparisons["A"], arm_index)
    b_actions = _read_actions(session_comparisons["B"], arm_index)
    reads = _read_ids(b_actions)
    episodes = _status_for_identity([_episode_ids(a_record) or None, _episode_ids(b_record) or None], local=True)
    episodes["global_session_identity"] = "unknown"
    return {
        "identities": {
            "run": _status_for_identity(
                [_event_run_ids(a_record) or None, _event_run_ids(b_record) or None]
            ),
            "session": _status_for_identity(
                [
                    _recorded_identity_values(a_record, "session_id") or None,
                    _recorded_identity_values(b_record, "session_id") or None,
                ]
            ),
            "source_directory": _status_for_identity([a_record["run_id"], b_record["run_id"]]),
            "recorded_episode": episodes,
            "process": process,
            "fresh_b_history": _fresh_history(b_record),
        },
        "checkpoint_inputs": {
            "native_state": _input_binding(
                name="native_state",
                artifact=artifacts["a_native"],
                b_record=b_record,
                b_spec=artifacts["b_spec_value"],
                spec_key="native_input",
                copied=None,
                consumed=artifacts["consumed"],
            ),
            "lineage_checkpoint": _input_binding(
                name="lineage_checkpoint",
                artifact=artifacts["a_lineage"],
                b_record=b_record,
                b_spec=artifacts["b_spec_value"],
                spec_key="lineage_input",
                copied=artifacts["b_lineage_initial"],
                consumed=artifacts["consumed"],
            ),
        },
        "b_spec": _b_spec_evidence(b_record, reads, artifacts),
        "consumed_boundary_hashes": {
            label: artifacts["consumed"].get(path.resolve())
            for label, path in artifacts["consumed_paths"].items()
            if artifacts["consumed"].get(path.resolve()) is not None
        },
        "created_file_id_to_b_read_id": _created_to_read(a_record, b_record, reads),
        "b_actual_source_exposure": _source_exposure(b_record, reads),
        "a_memory_write_and_version": _memory_write(a_record, a_actions),
        "b_restored_read": _restored_reads(b_record, reads),
        "causal_influence": "not_assessed",
    }


def compare_cross_session_records(clean, attacked, *, labels=("clean", "attacked"), artifacts):
    """Compare ordered ``(session_a, session_b)`` records for two conditions."""
    if len(clean) != 2 or len(attacked) != 2 or len(labels) != 2:
        raise ValueError("Exactly two ordered sessions and two condition labels are required")
    if any(not isinstance(label, str) or not label or len(label) > 256 for label in labels):
        raise ValueError("Condition labels must be non-empty strings of at most 256 characters")
    if labels[0] == labels[1]:
        raise ValueError("Condition labels must be distinct")
    session_results = {
        "A": compare_records(clean[0], attacked[0]),
        "B": compare_records(clean[1], attacked[1]),
    }
    for comparison in session_results.values():
        for arm, label in zip(comparison["arms"], labels, strict=True):
            arm["condition"] = label
    boundaries = {
        labels[0]: _boundary(clean[0], clean[1], session_results, 0, artifacts[0]),
        labels[1]: _boundary(attacked[0], attacked[1], session_results, 1, artifacts[1]),
    }
    return {
        "schema_version": 1,
        "protocol": "offline-cross-session-pair-v1",
        "scope": SCOPE,
        "condition_labels": list(labels),
        "session_order": ["A", "B"],
        "session_comparisons": session_results,
        "session_boundaries": boundaries,
        "causal_influence": "not_assessed",
        "attack_success": "unknown; use a separately declared native state oracle",
    }


def _page(result, records, output):
    esc = html.escape

    def dump(value):
        return "<pre>" + esc(json.dumps(value, ensure_ascii=False, indent=2)) + "</pre>"

    def event_anchor(condition, stage, event_id):
        return f"{condition}-{stage}-{event_id}"

    def event_link(condition, stage, event_id, label=None):
        if not event_id:
            return "Absent"
        target = quote(event_anchor(condition, stage, event_id), safe="")
        return f'<a href="#{esc(target, quote=True)}">{esc(label or event_id)}</a>'

    boundary_links = []
    for condition in result["condition_labels"]:
        boundary = result["session_boundaries"][condition]
        links = []
        for binding in boundary["a_memory_write_and_version"]["bound_rows"]:
            links.append(
                event_link(
                    condition,
                    "A",
                    binding["confirmed_write_event_id"],
                    "A digest-valid bound memory row [graph connectivity unknown] "
                    + str(binding["confirmed_write_event_id"]),
                )
            )
        exposure_status = boundary["b_actual_source_exposure"]["status"]
        for exposure in boundary["b_actual_source_exposure"]["events"]:
            exposure_label = (
                "B observed exposure"
                if exposure_status == "observed"
                else f"Candidate B exposure [{exposure_status}]"
            )
            links.append(
                event_link(
                    condition,
                    "B",
                    exposure["event_id"],
                    exposure_label + " " + str(exposure["event_id"]),
                )
            )
            links.append(
                event_link(
                    condition,
                    "B",
                    exposure["source_result_event_id"],
                    exposure_label + " result " + str(exposure["source_result_event_id"]),
                )
            )
        restored_status = boundary["b_restored_read"]["status"]
        restored_rows = (
            boundary["b_restored_read"]["events_matching_recorded_b_read_ids"]
            if restored_status == "observed"
            else boundary["b_restored_read"]["restored_read_events"]
        )
        for restored in restored_rows:
            restored_label = (
                "B validated restored read"
                if restored_status == "observed"
                else f"Candidate B restored read [{restored_status}]"
            )
            links.append(
                event_link(
                    condition,
                    "B",
                    restored["event_id"],
                    restored_label + " " + str(restored["event_id"]),
                )
            )
        boundary_links.append(
            f"<p>{esc(condition)} boundary evidence: " + " · ".join(links or ["No linked events recorded."]) + "</p>"
        )

    sections = []
    for condition, pair in zip(result["condition_labels"], records, strict=True):
        for stage, record in zip(("A", "B"), pair, strict=True):
            report = Path(record["path"]) / "report.html"
            link = "Per-run report unavailable."
            if report.is_symlink():
                raise ValueError(f"Per-run report must not be a symlink: {report}")
            if report.exists() and not report.resolve().is_relative_to(Path(record["path"]).resolve()):
                raise ValueError(f"Per-run report resolves outside its source run: {report}")
            if report.is_file():
                href = quote(Path(os.path.relpath(report, output)).as_posix(), safe="/")
                link = f'<a href="{esc(href, quote=True)}">Open per-run report</a>'
            events = "".join(
                f'<details id="{esc(event_anchor(condition, stage, event["event_id"]), quote=True)}">'
                f'<summary>{esc(event["event_id"])} · {esc(event["event_type"])}</summary>{dump(event)}</details>'
                for event in record["events"]
                if event.get("event_id") and event.get("event_type") not in {"MODEL_REQUEST", "MODEL_RESPONSE"}
            )
            sections.append(
                f"<section><h2>{esc(condition)} session {stage}: {esc(record['run_id'])}</h2>"
                f"<p>{link}</p><h3>Recorded events</h3>{events}</section>"
            )
    alignments = []
    for stage in ("A", "B"):
        comparison = result["session_comparisons"][stage]
        rows = []
        for row in comparison["alignment"]["rows"]:
            refs = []
            for condition, key in zip(result["condition_labels"], ("clean_event_id", "attacked_event_id"), strict=True):
                event_id = row[key]
                refs.append(event_link(condition, stage, event_id))
            rows.append(
                f"<tr><td>{row['index']}</td><td>{esc(row['status'])}</td><td>{esc(str(row['function']))}</td>"
                f"<td>{refs[0]}</td><td>{refs[1]}</td><td>{dump(row['argument_changes'])}</td></tr>"
            )
        alignments.append(
            f"<h2>Session {stage} action alignment</h2><p>{esc(comparison['alignment']['rule'])}. "
            "An ambiguous alignment displays one equally optimal possibility.</p><div class=table><table><thead><tr>"
            f"<th>Row</th><th>Status</th><th>Tool</th><th>{esc(result['condition_labels'][0])}</th>"
            f"<th>{esc(result['condition_labels'][1])}</th><th>Argument changes</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>"
        )
    overview = {
        "scope": result["scope"],
        "session_boundaries": result["session_boundaries"],
        "causal_influence": result["causal_influence"],
        "attack_success": result["attack_success"],
    }
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Cross-session trace comparison</title><style>body{{font:16px/1.5 system-ui;max-width:1200px;margin:32px auto;padding:0 20px}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border:1px solid #999;text-align:left;vertical-align:top}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere}}summary{{cursor:pointer}}details{{margin:10px 0}}.table{{overflow-x:auto}}</style></head>
<body><h1>Cross-session trace comparison</h1>{dump(overview)}{''.join(boundary_links)}{''.join(alignments)}{''.join(sections)}</body></html>"""


def export_cross_session_pair(
    clean_a: Path,
    clean_b: Path,
    attacked_a: Path,
    attacked_b: Path,
    output: Path,
    *,
    labels=("clean", "attacked"),
):
    """Export JSON and inert HTML without modifying the four source runs."""
    paths = [Path(path).expanduser().resolve() for path in (clean_a, clean_b, attacked_a, attacked_b)]
    output = Path(output).expanduser().resolve()
    if len(set(paths)) != 4:
        raise ValueError("The four ordered session run directories must be distinct")
    if output.exists():
        raise FileExistsError(output)
    if any(output == path or output.is_relative_to(path) for path in paths):
        raise ValueError("Report output must not be inside a source run directory")
    for path in paths:
        _validate_run_budget(path)
    records = [collect_run_record(path) for path in paths]
    consumed = {}
    artifacts = []
    for a_path, b_path in ((paths[0], paths[1]), (paths[2], paths[3])):
        branch_root = a_path.parent
        if b_path.parent != branch_root:
            branch_root = Path(os.path.commonpath((a_path, b_path)))
        branch_consumed = {}
        a_native = a_path / "native-memory.json"
        a_lineage = a_path / "lineage-state.json"
        b_initial = b_path / "lineage-initial-state.json"
        b_spec_path = b_path.parent / f"{b_path.name}-spec.json"
        for artifact in (a_native, a_lineage, b_initial):
            _optional_json(artifact, branch_root, branch_consumed)
        b_spec = _optional_json(b_spec_path, branch_root, branch_consumed)
        consumed.update(branch_consumed)
        artifacts.append(
            {
                "a_native": a_native,
                "a_lineage": a_lineage,
                "b_lineage_initial": b_initial,
                "b_spec_path": b_spec_path,
                "b_spec_value": b_spec,
                "consumed": branch_consumed,
                "consumed_paths": {
                    "session_a/native-memory.json": a_native,
                    "session_a/lineage-state.json": a_lineage,
                    "session_b/lineage-initial-state.json": b_initial,
                    f"session_b_spec/{b_spec_path.name}": b_spec_path,
                },
            }
        )
    for path, record in zip(paths, records, strict=True):
        for name, expected in record["source_hashes"].items():
            if _sha256(path / name) != expected:
                raise ValueError("Source changed while reading; preserve it before exporting")
    if any(_sha256(path) != expected for path, expected in consumed.items()):
        raise ValueError("Boundary source changed while reading; preserve it before exporting")
    result = compare_cross_session_records(
        (records[0], records[1]), (records[2], records[3]), labels=labels, artifacts=artifacts
    )
    for record, path in zip(records, paths, strict=True):
        record["path"] = str(path)
    for comparison in result["session_comparisons"].values():
        for arm, path in zip(comparison["arms"], (paths[0], paths[2]), strict=True):
            # Session B uses its own ordered paths.
            if comparison is result["session_comparisons"]["B"]:
                path = paths[1] if arm is comparison["arms"][0] else paths[3]
            arm["path"] = str(path)
    page = _page(result, ((records[0], records[1]), (records[2], records[3])), output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "cross-session.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (output / "index.html").write_text(page, encoding="utf-8")
    return result
