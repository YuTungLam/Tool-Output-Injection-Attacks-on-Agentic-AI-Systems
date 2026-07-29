"""Versioned event-level JSONL tracing."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .utils import canonical_json

TRACE_SCHEMA_VERSION = "trace-event-v1"
ALLOWED_EVENT_TYPES = {
    "run_start",
    "user_input",
    "tool_call",
    "tool_result_raw",
    "defence_decision",
    "tool_result_exposed",
    "agent_decision",
    "sink_attempt",
    "sink_result",
    "sink_effect",
    "task_evaluation",
    "run_error",
    "run_end",
}
EVENT_DATA_REQUIREMENTS = {
    "run_start": {"scheduled", "policy_name", "initial_memory_state", "sink_state"},
    "user_input": {"prompt", "prompt_sha256"},
    "tool_call": {"tool_name", "canonical_arguments", "argument_sha256"},
    "tool_result_raw": {"origin", "trusted", "raw_result", "raw_result_sha256"},
    "defence_decision": {"policy_name", "decision", "input_sha256", "output_sha256"},
    "tool_result_exposed": {"exposed_result", "exposed_result_sha256", "transformed"},
    "agent_decision": {"answer", "sink_action", "termination_decision"},
    "sink_attempt": {"sink_id", "operation", "attempted"},
    "sink_result": {
        "simulator_accepted",
        "user_authorized",
        "blocked",
        "security_policy_violation",
        "prohibited_simulated_effect",
        "external_side_effect",
    },
    "sink_effect": {"prohibited_simulated_effect", "external_side_effect"},
    "task_evaluation": {"task_success", "sink_attempted", "external_side_effect"},
    "run_error": {"error_type", "error_message", "outcome_evaluable"},
    "run_end": {"status", "termination_reason", "step_count", "task_success"},
}


@dataclass(frozen=True)
class TraceContext:
    experiment_id: str
    run_id: str
    matched_set_id: str
    condition: str
    task_id: str
    task_version: str
    payload_id: str
    fixture_version: str
    replicate_id: int
    plan_index: int
    agent_version: str
    code_commit: str
    code_dirty: bool
    config_hash: str
    runtime_kind: str
    evidence_scope: str
    policy_id: str
    policy_version: str
    model_id: str | None
    model_version: str | None
    sampling_parameters: Mapping[str, Any]
    seed: int
    system_prompt_hash: str
    tool_schema_hash: str
    transport: str
    max_steps: int


class TraceRecorder:
    """Append-only recorder with deterministic event IDs and logical ordering."""

    def __init__(self, context: TraceContext) -> None:
        self.context = context
        self.events: list[dict[str, Any]] = []
        self._started_ns = time.perf_counter_ns()

    def emit(
        self,
        event_type: str,
        component: str,
        data: Mapping[str, Any],
        *,
        parent_event_id: str | None = None,
        tool_call_id: str | None = None,
    ) -> str:
        index = len(self.events)
        event_id = f"{self.context.run_id}:event-{index:04d}"
        event = {
            "schema_version": TRACE_SCHEMA_VERSION,
            "experiment_id": self.context.experiment_id,
            "run_id": self.context.run_id,
            "matched_set_id": self.context.matched_set_id,
            "condition": self.context.condition,
            "task_id": self.context.task_id,
            "task_version": self.context.task_version,
            "payload_id": self.context.payload_id,
            "fixture_version": self.context.fixture_version,
            "replicate_id": self.context.replicate_id,
            "plan_index": self.context.plan_index,
            "agent_version": self.context.agent_version,
            "code_commit": self.context.code_commit,
            "code_dirty": self.context.code_dirty,
            "config_hash": self.context.config_hash,
            "runtime_kind": self.context.runtime_kind,
            "evidence_scope": self.context.evidence_scope,
            "policy_id": self.context.policy_id,
            "policy_version": self.context.policy_version,
            "model_id": self.context.model_id,
            "model_version": self.context.model_version,
            "sampling_parameters": dict(self.context.sampling_parameters),
            "seed": self.context.seed,
            "system_prompt_hash": self.context.system_prompt_hash,
            "tool_schema_hash": self.context.tool_schema_hash,
            "transport": self.context.transport,
            "max_steps": self.context.max_steps,
            "event_id": event_id,
            "event_index": index,
            "event_type": event_type,
            "component": component,
            "parent_event_id": parent_event_id,
            "tool_call_id": tool_call_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_ns": time.perf_counter_ns() - self._started_ns,
            "data": dict(data),
        }
        self.events.append(event)
        return event_id


def write_jsonl(
    path: str | Path,
    events: Iterable[Mapping[str, Any]],
    *,
    overwrite: bool = False,
) -> None:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing trace: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(canonical_json(event))
            handle.write("\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}") from exc
            if not isinstance(event, dict):
                raise ValueError(f"Trace line {line_number} is not an object")
            events.append(event)
    return events


def validate_trace(events: Iterable[Mapping[str, Any]]) -> None:
    events = list(events)
    if not events:
        raise ValueError("Trace must contain at least one event")

    required_fields = {
        "schema_version",
        "experiment_id",
        "run_id",
        "matched_set_id",
        "condition",
        "task_id",
        "task_version",
        "payload_id",
        "fixture_version",
        "replicate_id",
        "plan_index",
        "agent_version",
        "code_commit",
        "code_dirty",
        "config_hash",
        "runtime_kind",
        "evidence_scope",
        "policy_id",
        "policy_version",
        "model_id",
        "model_version",
        "sampling_parameters",
        "seed",
        "system_prompt_hash",
        "tool_schema_hash",
        "transport",
        "max_steps",
        "event_id",
        "event_index",
        "event_type",
        "component",
        "parent_event_id",
        "tool_call_id",
        "timestamp_utc",
        "elapsed_ns",
        "data",
    }
    invariant_fields = {
        "schema_version",
        "experiment_id",
        "run_id",
        "matched_set_id",
        "condition",
        "task_id",
        "task_version",
        "payload_id",
        "fixture_version",
        "replicate_id",
        "plan_index",
        "agent_version",
        "code_commit",
        "code_dirty",
        "config_hash",
        "runtime_kind",
        "evidence_scope",
        "policy_id",
        "policy_version",
        "model_id",
        "model_version",
        "sampling_parameters",
        "seed",
        "system_prompt_hash",
        "tool_schema_hash",
        "transport",
        "max_steps",
    }

    by_run: dict[str, list[Mapping[str, Any]]] = {}
    all_event_ids: set[str] = set()
    for ordinal, event in enumerate(events):
        missing = sorted(required_fields - set(event))
        if missing:
            raise ValueError(
                f"Trace event {ordinal} is missing required fields: {', '.join(missing)}"
            )
        if event["schema_version"] != TRACE_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported trace schema at event {ordinal}: {event['schema_version']!r}"
            )
        if not isinstance(event["data"], Mapping):
            raise ValueError(f"Trace event {ordinal} data must be an object")
        if not isinstance(event["sampling_parameters"], Mapping):
            raise ValueError(
                f"Trace event {ordinal} sampling_parameters must be an object"
            )
        if not isinstance(event["event_index"], int) or event["event_index"] < 0:
            raise ValueError(f"Trace event {ordinal} has an invalid event_index")
        if not isinstance(event["event_type"], str) or not event["event_type"]:
            raise ValueError(f"Trace event {ordinal} has an invalid event_type")
        if event["event_type"] not in ALLOWED_EVENT_TYPES:
            raise ValueError(
                f"Trace event {ordinal} has unsupported event_type {event['event_type']!r}"
            )
        required_data = EVENT_DATA_REQUIREMENTS[event["event_type"]]
        missing_data = sorted(required_data - set(event["data"]))
        if missing_data:
            raise ValueError(
                f"Trace event {ordinal} ({event['event_type']}) is missing data fields: "
                f"{', '.join(missing_data)}"
            )
        if event["condition"] not in {"clean", "placebo", "attack"}:
            raise ValueError(f"Trace event {ordinal} has invalid condition")
        event_id = str(event["event_id"])
        if event_id in all_event_ids:
            raise ValueError(f"Duplicate event_id: {event_id}")
        all_event_ids.add(event_id)
        if bool(event["data"].get("external_side_effect", False)):
            raise ValueError(f"External side effect recorded in event {event_id}")

        run_id = str(event.get("run_id", ""))
        if not run_id:
            raise ValueError("Every event must have a run_id")
        by_run.setdefault(run_id, []).append(event)

    for run_id, run_events in by_run.items():
        baseline = run_events[0]
        for event in run_events[1:]:
            changed = [
                field
                for field in invariant_fields
                if event[field] != baseline[field]
            ]
            if changed:
                raise ValueError(
                    f"Run {run_id} changes invariant fields: {', '.join(sorted(changed))}"
                )

        indexes = [event.get("event_index") for event in run_events]
        if indexes != list(range(len(run_events))):
            raise ValueError(f"Non-contiguous event indexes in {run_id}")
        expected_event_ids = [
            f"{run_id}:event-{index:04d}" for index in range(len(run_events))
        ]
        actual_event_ids = [str(event["event_id"]) for event in run_events]
        if actual_event_ids != expected_event_ids:
            raise ValueError(f"Non-canonical event IDs in {run_id}")

        event_types = [event.get("event_type") for event in run_events]
        if event_types.count("run_start") != 1 or event_types.count("run_end") != 1:
            raise ValueError(f"Run {run_id} must have exactly one start and end")
        if event_types[0] != "run_start" or event_types[-1] != "run_end":
            raise ValueError(f"Run {run_id} has invalid terminal ordering")

        seen_calls: set[str] = set()
        seen_attempts: set[str] = set()
        seen_results: set[str] = set()
        seen_events: set[str] = set()
        seen_event_types: dict[str, str] = {}
        for index, event in enumerate(run_events):
            event_type = event.get("event_type")
            call_id = event.get("tool_call_id")
            parent_id = event.get("parent_event_id")
            if index == 0 and parent_id is not None:
                raise ValueError(f"run_start has a parent in {run_id}")
            if index > 0 and (
                parent_id is None or str(parent_id) not in seen_events
            ):
                raise ValueError(
                    f"Event {event['event_id']} lacks a preceding parent in {run_id}"
                )
            parent_type = None if parent_id is None else seen_event_types[str(parent_id)]
            required_parent_types = {
                "user_input": {"run_start"},
                "tool_call": {"user_input", "agent_decision"},
                "tool_result_raw": {"tool_call"},
                "defence_decision": {"tool_result_raw"},
                "tool_result_exposed": {"defence_decision"},
                "agent_decision": {"tool_result_exposed"},
                "sink_attempt": {"agent_decision"},
                "sink_result": {"sink_attempt"},
                "sink_effect": {"sink_result"},
                "task_evaluation": {"agent_decision", "sink_result", "sink_effect"},
                "run_error": set(ALLOWED_EVENT_TYPES - {"run_end"}),
                "run_end": {"task_evaluation", "run_error"},
            }
            if event_type in required_parent_types and parent_type not in required_parent_types[event_type]:
                raise ValueError(
                    f"Event {event['event_id']} has invalid parent type {parent_type!r}"
                )
            if event_type == "tool_call" and call_id:
                if str(call_id) in seen_calls:
                    raise ValueError(f"Duplicate tool_call_id in {run_id}: {call_id}")
                seen_calls.add(str(call_id))
            if event_type in {
                "tool_result_raw",
                "defence_decision",
                "tool_result_exposed",
            }:
                if not call_id or str(call_id) not in seen_calls:
                    raise ValueError(f"Tool result without preceding call in {run_id}")
            if event_type == "sink_attempt":
                seen_attempts.add(str(event.get("event_id")))
            if event_type == "sink_result":
                parent = str(event.get("parent_event_id"))
                if parent not in seen_attempts:
                    raise ValueError(f"Sink result without preceding attempt in {run_id}")
                seen_results.add(str(event.get("event_id")))
            if event_type == "sink_effect":
                parent = str(event.get("parent_event_id"))
                if parent not in seen_results:
                    raise ValueError(f"Sink effect without preceding result in {run_id}")
                if bool(event["data"].get("blocked", False)):
                    raise ValueError(f"Blocked sink attempt produced an effect in {run_id}")
            seen_events.add(str(event["event_id"]))
            seen_event_types[str(event["event_id"])] = str(event_type)

    by_match: dict[str, list[Mapping[str, Any]]] = {}
    for run_events in by_run.values():
        by_match.setdefault(str(run_events[0]["matched_set_id"]), []).append(
            run_events[0]
        )
    matched_invariants = {
        "experiment_id",
        "matched_set_id",
        "task_id",
        "task_version",
        "replicate_id",
        "agent_version",
        "code_commit",
        "code_dirty",
        "config_hash",
        "runtime_kind",
        "evidence_scope",
        "policy_id",
        "policy_version",
        "model_id",
        "model_version",
        "sampling_parameters",
        "seed",
        "system_prompt_hash",
        "tool_schema_hash",
        "transport",
        "max_steps",
    }
    for matched_set_id, first_events in by_match.items():
        baseline = first_events[0]
        conditions: set[str] = set()
        for event in first_events:
            condition = str(event["condition"])
            if condition in conditions:
                raise ValueError(
                    f"Matched set {matched_set_id} repeats condition {condition}"
                )
            conditions.add(condition)
            changed = [
                field
                for field in matched_invariants
                if event[field] != baseline[field]
            ]
            if changed:
                raise ValueError(
                    f"Matched set {matched_set_id} changes fields: "
                    f"{', '.join(sorted(changed))}"
                )
