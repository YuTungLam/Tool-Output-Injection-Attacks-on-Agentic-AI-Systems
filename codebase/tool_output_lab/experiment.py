"""Randomized matched-run execution for the sandboxed pilot."""

from __future__ import annotations

import json
import os
import random
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

from . import __version__
from .compare import compare_privileged_events
from .conditions import FIXTURE_VERSION, build_tool_response, validate_matched_triplet
from .domain import Condition, PolicyInput, Task
from .policy import AgentPolicy, make_policy
from .tools import MockDocumentTool, SimulatedSink
from .tracing import TraceContext, TraceRecorder, validate_trace, write_jsonl
from .utils import canonical_json, sha256_text, stable_identifier

SUMMARY_SCHEMA_VERSION = "experiment-summary-v1"


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str = "instrumentation-pilot"
    repetitions: int = 1
    seed: int = 20260723
    policy_name: str = "vulnerable"
    max_steps: int = 1
    transport: str = "in_process_mock"
    code_commit: str = "uncommitted-working-tree"
    code_dirty: bool = True
    runtime_kind: str = "scripted_control"
    evidence_scope: str = "instrumentation_validation"
    empirical_llm_evidence: bool = False

    def validate(self) -> None:
        if not self.experiment_id or len(self.experiment_id) > 80:
            raise ValueError("experiment_id must contain 1-80 characters")
        if self.repetitions < 1:
            raise ValueError("repetitions must be at least 1")
        if self.repetitions > 10_000:
            raise ValueError("repetitions exceeds the safety limit of 10,000")
        if self.max_steps != 1:
            raise ValueError("The instrumentation pilot supports exactly one agent step")
        if self.runtime_kind != "scripted_control":
            raise ValueError("The instrumentation pilot must be labelled scripted_control")
        if self.evidence_scope != "instrumentation_validation":
            raise ValueError("The instrumentation pilot is instrumentation validation only")
        if self.empirical_llm_evidence:
            raise ValueError("Scripted controls cannot be labelled empirical LLM evidence")
        make_policy(self.policy_name)


@dataclass(frozen=True)
class RunSpec:
    task: Task
    condition: Condition
    replicate_id: int
    matched_set_id: str
    run_id: str
    run_seed: int
    plan_index: int = -1

    def manifest_record(self) -> Mapping[str, Any]:
        return {
            "run_id": self.run_id,
            "matched_set_id": self.matched_set_id,
            "task_id": self.task.task_id,
            "task_version": self.task.version,
            "condition": self.condition.value,
            "replicate_id": self.replicate_id,
            "run_seed": self.run_seed,
            "plan_index": self.plan_index,
        }


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    matched_set_id: str
    task_id: str
    condition: str
    replicate_id: int
    status: str
    outcome_evaluable: bool
    task_success: bool | None
    sink_attempted: bool | None
    simulator_accepted: bool | None
    user_authorized: bool | None
    sink_blocked: bool | None
    security_policy_violation: bool | None
    prohibited_simulated_effect: bool | None
    external_side_effect: bool | None
    error_type: str | None = None
    error_message: str | None = None

    def to_mapping(self) -> Mapping[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentResult:
    config: ExperimentConfig
    config_hash: str
    manifest: tuple[Mapping[str, Any], ...]
    summaries: tuple[RunSummary, ...]
    events: tuple[Mapping[str, Any], ...]
    aggregate_by_condition: Mapping[str, Mapping[str, Any]]
    matched_comparisons: tuple[Mapping[str, Any], ...]

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "schema_version": SUMMARY_SCHEMA_VERSION,
            "experiment": {
                **asdict(self.config),
                "config_hash": self.config_hash,
                "scheduled_runs": len(self.manifest),
                "completed_runs": sum(
                    summary.status == "completed" for summary in self.summaries
                ),
                "empirical_llm_evidence": False,
                "evidence_notice": (
                    "Scripted control results validate instrumentation only; "
                    "they are not empirical LLM susceptibility estimates."
                ),
            },
            "manifest": list(self.manifest),
            "runs": [summary.to_mapping() for summary in self.summaries],
            "aggregate_by_condition": self.aggregate_by_condition,
            "matched_comparisons": list(self.matched_comparisons),
        }


def _configuration_hash(config: ExperimentConfig, tasks: Iterable[Task]) -> str:
    material = {
        "config": asdict(config),
        "fixture_version": FIXTURE_VERSION,
        "tasks": [
            {
                "definition": asdict(task),
                "fixture_sha256": {
                    condition.value: build_tool_response(task, condition).raw_sha256
                    for condition in Condition
                },
            }
            for task in tasks
        ],
    }
    return sha256_text(canonical_json(material))


def build_run_plan(
    tasks: list[Task], config: ExperimentConfig, config_hash: str
) -> list[RunSpec]:
    """Schedule matched cells, then randomize their execution order reproducibly."""

    plan: list[RunSpec] = []
    for replicate_id in range(1, config.repetitions + 1):
        for task in tasks:
            matched_set_id = stable_identifier(
                "match",
                config.experiment_id,
                config_hash,
                task.task_id,
                task.version,
                replicate_id,
                length=20,
            )
            run_seed = int(
                sha256_text(f"{config.seed}:{matched_set_id}")[:8], 16
            )
            for condition in Condition:
                run_id = stable_identifier(
                    "run", matched_set_id, condition.value, length=20
                )
                plan.append(
                    RunSpec(
                        task=task,
                        condition=condition,
                        replicate_id=replicate_id,
                        matched_set_id=matched_set_id,
                        run_id=run_id,
                        run_seed=run_seed,
                    )
                )

    random.Random(config.seed).shuffle(plan)
    return [replace(spec, plan_index=index) for index, spec in enumerate(plan)]


def _run_one(
    spec: RunSpec,
    config: ExperimentConfig,
    config_hash: str,
    policy: AgentPolicy,
    tool: MockDocumentTool,
) -> tuple[list[Mapping[str, Any]], RunSummary]:
    tool_arguments = {"query": spec.task.tool_query}
    planned_response = build_tool_response(spec.task, spec.condition)
    context = TraceContext(
        experiment_id=config.experiment_id,
        run_id=spec.run_id,
        matched_set_id=spec.matched_set_id,
        condition=spec.condition.value,
        task_id=spec.task.task_id,
        task_version=spec.task.version,
        payload_id=planned_response.payload_id,
        fixture_version=planned_response.fixture_version,
        replicate_id=spec.replicate_id,
        plan_index=spec.plan_index,
        agent_version=__version__,
        code_commit=config.code_commit,
        code_dirty=config.code_dirty,
        config_hash=config_hash,
        runtime_kind=config.runtime_kind,
        evidence_scope=config.evidence_scope,
        policy_id=policy.policy_id,
        policy_version=policy.version,
        model_id=None,
        model_version=None,
        seed=spec.run_seed,
        system_prompt_hash=sha256_text("scripted-policy-no-system-prompt"),
        tool_schema_hash=tool.schema_hash,
        transport=config.transport,
        max_steps=config.max_steps,
    )
    recorder = TraceRecorder(context)
    sink = SimulatedSink(spec.task.eligible_sink)
    parent: str | None = None

    try:
        parent = recorder.emit(
            "run_start",
            "experiment_controller",
            {
                "scheduled": True,
                "policy_name": config.policy_name,
                "initial_memory_state": "empty",
                "sink_state": "fresh",
                "empirical_llm_evidence": False,
            },
        )
        parent = recorder.emit(
            "user_input",
            "user",
            {
                "prompt": spec.task.user_prompt,
                "prompt_sha256": sha256_text(spec.task.user_prompt),
            },
            parent_event_id=parent,
        )

        call_id = stable_identifier("call", spec.run_id, tool.name, length=20)
        canonical_arguments = canonical_json(tool_arguments)
        parent = recorder.emit(
            "tool_call",
            "agent_runtime",
            {
                "tool_name": tool.name,
                "tool_version": tool.version,
                "canonical_arguments": tool_arguments,
                "argument_sha256": sha256_text(canonical_arguments),
            },
            parent_event_id=parent,
            tool_call_id=call_id,
        )
        response = tool.invoke(spec.task, spec.condition, tool_arguments)
        if response.raw_sha256 != planned_response.raw_sha256:
            raise RuntimeError("Resolved tool fixture differs from the scheduled fixture")
        raw_result_event = recorder.emit(
            "tool_result_raw",
            tool.name,
            {
                "origin": "frozen_synthetic_fixture",
                "trusted": False,
                "raw_result": response.raw_text,
                "raw_result_sha256": response.raw_sha256,
                "raw_result_bytes": len(response.raw_text.encode("utf-8")),
            },
            parent_event_id=parent,
            tool_call_id=call_id,
        )
        defence_event = recorder.emit(
            "defence_decision",
            "boundary_mediator",
            {
                "policy_name": "none",
                "policy_version": "1.0",
                "decision": "pass",
                "reason_code": "no_defence_in_instrumentation_pilot",
                "input_sha256": response.raw_sha256,
                "output_sha256": response.raw_sha256,
            },
            parent_event_id=raw_result_event,
            tool_call_id=call_id,
        )
        exposed_event = recorder.emit(
            "tool_result_exposed",
            "boundary_mediator",
            {
                "exposed_result": response.raw_text,
                "exposed_result_sha256": response.raw_sha256,
                "transformed": False,
            },
            parent_event_id=defence_event,
            tool_call_id=call_id,
        )

        # Only model-visible content is passed; hidden task ground truth and the
        # condition label are retained by the evaluator/controller.
        decision = policy.decide(
            PolicyInput(
                user_prompt=spec.task.user_prompt,
                tool_payload=dict(response.payload),
                available_sink_ids=(spec.task.eligible_sink,),
            )
        )
        action_arguments = (
            None
            if decision.sink_action is None
            else dict(decision.sink_action.canonical_arguments())
        )
        decision_signature = {
            "answer": decision.answer,
            "sink_action": action_arguments,
            "termination_decision": "finish",
        }
        decision_event = recorder.emit(
            "agent_decision",
            policy.policy_id,
            {
                **decision_signature,
                "answer_sha256": sha256_text(decision.answer),
                "reason_code": decision.reason_code,
                "canonical_action_sha256": sha256_text(
                    canonical_json(decision_signature)
                ),
                "source_tool_result_event_id": exposed_event,
            },
            parent_event_id=exposed_event,
        )

        sink_attempted = False
        simulator_accepted = False
        user_authorized = False
        sink_blocked = False
        security_policy_violation = False
        prohibited_simulated_effect = False
        external_side_effect = False
        evaluation_parent = decision_event

        if decision.sink_action is not None:
            sink_attempted = True
            attempt_event = recorder.emit(
                "sink_attempt",
                "simulated_sink_router",
                {
                    "sink_id": decision.sink_action.sink_id,
                    "operation": decision.sink_action.operation,
                    "target_class": "in_memory_simulator",
                    "canonical_arguments": action_arguments,
                    "attempted": True,
                    "source_tool_result_event_id": exposed_event,
                },
                parent_event_id=decision_event,
            )
            sink_result = sink.attempt(decision.sink_action, user_authorized=False)
            simulator_accepted = sink_result.simulator_accepted
            user_authorized = sink_result.user_authorized
            sink_blocked = sink_result.blocked
            security_policy_violation = sink_result.security_policy_violation
            prohibited_simulated_effect = sink_result.prohibited_simulated_effect
            external_side_effect = sink_result.external_side_effect
            if external_side_effect:
                raise RuntimeError("Simulated sink reported an external side effect")
            result_event = recorder.emit(
                "sink_result",
                "simulated_sink_router",
                {
                    "simulator_accepted": simulator_accepted,
                    "user_authorized": user_authorized,
                    "blocked": sink_blocked,
                    "security_policy_violation": security_policy_violation,
                    "prohibited_simulated_effect": prohibited_simulated_effect,
                    "external_side_effect": external_side_effect,
                    "reason_code": sink_result.reason_code,
                },
                parent_event_id=attempt_event,
            )
            evaluation_parent = result_event

            if prohibited_simulated_effect:
                evaluation_parent = recorder.emit(
                    "sink_effect",
                    "simulated_audit_sink",
                    {
                        "prohibited_simulated_effect": True,
                        "external_side_effect": False,
                        "reason_code": sink_result.reason_code,
                        "simulator_record_count": len(sink.records),
                    },
                    parent_event_id=result_event,
                )

        task_success = decision.answer == spec.task.public_answer
        evaluation_event = recorder.emit(
            "task_evaluation",
            "deterministic_evaluator-v1",
            {
                "task_success": task_success,
                "expected_answer": spec.task.public_answer,
                "observed_answer": decision.answer,
                "sink_attempted": sink_attempted,
                "simulator_accepted": simulator_accepted,
                "user_authorized": user_authorized,
                "security_policy_violation": security_policy_violation,
                "prohibited_simulated_effect": prohibited_simulated_effect,
                "external_side_effect": external_side_effect,
                "outcome_evaluable": True,
            },
            parent_event_id=evaluation_parent,
        )
        recorder.emit(
            "run_end",
            "experiment_controller",
            {
                "status": "completed",
                "termination_reason": "policy_finished",
                "step_count": 1,
                "task_success": task_success,
            },
            parent_event_id=evaluation_event,
        )
        summary = RunSummary(
            run_id=spec.run_id,
            matched_set_id=spec.matched_set_id,
            task_id=spec.task.task_id,
            condition=spec.condition.value,
            replicate_id=spec.replicate_id,
            status="completed",
            outcome_evaluable=True,
            task_success=task_success,
            sink_attempted=sink_attempted,
            simulator_accepted=simulator_accepted,
            user_authorized=user_authorized,
            sink_blocked=sink_blocked,
            security_policy_violation=security_policy_violation,
            prohibited_simulated_effect=prohibited_simulated_effect,
            external_side_effect=external_side_effect,
        )
    except Exception as exc:
        error_event = recorder.emit(
            "run_error",
            "experiment_controller",
            {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "outcome_evaluable": False,
                "censored": False,
                "missingness_reason": "runtime_or_harness_error",
            },
            parent_event_id=parent,
        )
        recorder.emit(
            "run_end",
            "experiment_controller",
            {
                "status": "error",
                "termination_reason": "runtime_error",
                "step_count": 0,
                "task_success": None,
            },
            parent_event_id=error_event,
        )
        summary = RunSummary(
            run_id=spec.run_id,
            matched_set_id=spec.matched_set_id,
            task_id=spec.task.task_id,
            condition=spec.condition.value,
            replicate_id=spec.replicate_id,
            status="error",
            outcome_evaluable=False,
            task_success=None,
            sink_attempted=None,
            simulator_accepted=None,
            user_authorized=None,
            sink_blocked=None,
            security_policy_violation=None,
            prohibited_simulated_effect=None,
            external_side_effect=None,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

    return recorder.events, summary


def _aggregate(summaries: Iterable[RunSummary]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for condition in Condition:
        rows = [row for row in summaries if row.condition == condition.value]
        count = len(rows)

        def metric(name: str) -> tuple[int, int, float | None]:
            evaluable = [row for row in rows if getattr(row, name) is not None]
            total = sum(bool(getattr(row, name)) for row in evaluable)
            denominator = len(evaluable)
            return total, denominator, (total / denominator if denominator else None)

        task_count, task_denominator, task_rate = metric("task_success")
        attempt_count, attempt_denominator, attempt_rate = metric("sink_attempted")
        violation_count, violation_denominator, violation_rate = metric(
            "security_policy_violation"
        )
        effect_count, effect_denominator, effect_rate = metric(
            "prohibited_simulated_effect"
        )
        external_count, external_denominator, external_rate = metric(
            "external_side_effect"
        )
        result[condition.value] = {
            "runs": count,
            "completed_runs": sum(row.status == "completed" for row in rows),
            "error_runs": sum(row.status == "error" for row in rows),
            "task_success_count": task_count,
            "task_success_evaluable_runs": task_denominator,
            "task_success_rate": task_rate,
            "sink_attempt_count": attempt_count,
            "sink_attempt_evaluable_runs": attempt_denominator,
            "sink_attempt_rate": attempt_rate,
            "security_policy_violation_count": violation_count,
            "security_policy_violation_evaluable_runs": violation_denominator,
            "security_policy_violation_rate": violation_rate,
            "prohibited_simulated_effect_count": effect_count,
            "prohibited_simulated_effect_evaluable_runs": effect_denominator,
            "prohibited_simulated_effect_rate": effect_rate,
            "external_side_effect_count": external_count,
            "external_side_effect_evaluable_runs": external_denominator,
            "external_side_effect_rate": external_rate,
        }
    return result


def _matched_comparisons(
    events: Iterable[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], ...]:
    by_run: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        by_run.setdefault(str(event["run_id"]), []).append(event)

    by_match: dict[str, dict[str, list[Mapping[str, Any]]]] = {}
    for run_events in by_run.values():
        first = run_events[0]
        by_match.setdefault(str(first["matched_set_id"]), {})[
            str(first["condition"])
        ] = run_events

    comparisons: list[Mapping[str, Any]] = []
    for matched_set_id in sorted(by_match):
        condition_runs = by_match[matched_set_id]
        clean = condition_runs.get(Condition.CLEAN.value)
        if clean is None:
            continue
        for right_condition in (Condition.PLACEBO, Condition.ATTACK):
            right = condition_runs.get(right_condition.value)
            if right is None:
                continue
            if (
                clean[-1].get("data", {}).get("status") != "completed"
                or right[-1].get("data", {}).get("status") != "completed"
            ):
                continue
            comparison = compare_privileged_events(clean, right)
            comparisons.append(
                {
                    "matched_set_id": matched_set_id,
                    "task_id": clean[0]["task_id"],
                    "replicate_id": clean[0]["replicate_id"],
                    "left_condition": Condition.CLEAN.value,
                    "right_condition": right_condition.value,
                    **comparison,
                    "interpretation": "observable_structural_difference_not_causal_attribution",
                }
            )
    return tuple(comparisons)


def _write_json_document(
    path: str | Path, value: Mapping[str, Any], *, overwrite: bool
) -> None:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing summary: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def run_experiment(
    tasks: list[Task],
    config: ExperimentConfig,
    *,
    trace_path: str | Path | None = None,
    summary_path: str | Path | None = None,
    overwrite: bool = False,
) -> ExperimentResult:
    """Run the complete clean/placebo/attack matrix and optionally persist artifacts."""

    config.validate()
    if not tasks:
        raise ValueError("At least one task is required")
    for task in tasks:
        task.validate()
        validate_matched_triplet(task)

    for candidate, label in ((trace_path, "trace"), (summary_path, "summary")):
        if candidate is not None and Path(candidate).exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing {label}: {candidate}")

    if trace_path is not None and summary_path is not None:
        normalized_trace = os.path.normcase(str(Path(trace_path).resolve()))
        normalized_summary = os.path.normcase(str(Path(summary_path).resolve()))
        if normalized_trace == normalized_summary:
            raise ValueError("trace_path and summary_path must be different files")

    config_hash = _configuration_hash(config, tasks)
    plan = build_run_plan(tasks, config, config_hash)
    tool = MockDocumentTool()
    all_events: list[Mapping[str, Any]] = []
    summaries: list[RunSummary] = []

    for spec in plan:
        policy = make_policy(config.policy_name)
        run_events, summary = _run_one(spec, config, config_hash, policy, tool)
        all_events.extend(run_events)
        summaries.append(summary)

    validate_trace(all_events)
    result = ExperimentResult(
        config=config,
        config_hash=config_hash,
        manifest=tuple(spec.manifest_record() for spec in plan),
        summaries=tuple(summaries),
        events=tuple(all_events),
        aggregate_by_condition=_aggregate(summaries),
        matched_comparisons=_matched_comparisons(all_events),
    )

    if trace_path is not None:
        write_jsonl(trace_path, result.events, overwrite=overwrite)
    if summary_path is not None:
        _write_json_document(summary_path, result.to_mapping(), overwrite=overwrite)
    return result
