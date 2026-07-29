"""Typed domain objects for tasks, agent decisions, and simulated sinks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class Condition(str, Enum):
    """The matched tool-response treatments in the pilot."""

    CLEAN = "clean"
    PLACEBO = "placebo"
    ATTACK = "attack"


@dataclass(frozen=True)
class Task:
    """One synthetic task with deterministic utility and security ground truth."""

    task_id: str
    version: str
    user_prompt: str
    tool_query: str
    public_answer: str
    confidential_token: str
    eligible_sink: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Task":
        if not isinstance(value, Mapping):
            raise ValueError("Each task must be a JSON object")
        required = {
            "task_id",
            "version",
            "user_prompt",
            "tool_query",
            "public_answer",
            "confidential_token",
            "eligible_sink",
        }
        missing = sorted(required - set(value))
        unknown = sorted(set(value) - required)
        if missing:
            raise ValueError(f"Task is missing required fields: {', '.join(missing)}")
        if unknown:
            raise ValueError(f"Task has unknown fields: {', '.join(unknown)}")
        non_strings = sorted(field for field in required if not isinstance(value[field], str))
        if non_strings:
            raise ValueError(f"Task fields must be strings: {', '.join(non_strings)}")
        empty = sorted(field for field in required if not value[field].strip())
        if empty:
            raise ValueError(f"Task fields must not be empty: {', '.join(empty)}")

        task = cls(**{field: value[field] for field in required})
        task.validate()
        return task

    def validate(self) -> None:
        if not self.task_id.replace("-", "").isalnum():
            raise ValueError(f"Unsafe task_id: {self.task_id!r}")
        if not self.confidential_token.startswith("CANARY-"):
            raise ValueError("Only synthetic CANARY-* tokens are allowed")
        if self.eligible_sink != "simulated_audit_sink":
            raise ValueError("Tasks may target only simulated_audit_sink")
        if len(self.user_prompt) > 1_000 or len(self.tool_query) > 1_000:
            raise ValueError("Task prompt and query must each be at most 1,000 characters")
        if len(self.public_answer) > 500:
            raise ValueError("Synthetic public answer must be at most 500 characters")


@dataclass(frozen=True)
class PolicyInput:
    """Only the information visible to the post-tool policy under test."""

    user_prompt: str
    tool_payload: Mapping[str, str]
    available_sink_ids: tuple[str, ...]
    run_seed: int | None = None
    source_tool_name: str | None = None
    source_tool_arguments: Mapping[str, str] | None = None
    source_tool_call_id: str | None = None


@dataclass(frozen=True)
class ToolResponse:
    """A fixture selected by the harness; the condition is not shown to the policy."""

    condition: Condition
    fixture_version: str
    payload_id: str
    payload: Mapping[str, str]
    raw_text: str
    raw_sha256: str


@dataclass(frozen=True)
class SinkAction:
    """A policy decision requesting a sensitive simulated action."""

    sink_id: str
    operation: str
    value: str
    source_field: str

    def canonical_arguments(self) -> Mapping[str, str]:
        return {
            "operation": self.operation,
            "sink_id": self.sink_id,
            "source_field": self.source_field,
            "value": self.value,
        }


@dataclass(frozen=True)
class ModelCallMetadata:
    """Non-sensitive metadata retained from one provider call."""

    provider_id: str
    model_id: str
    model_version: str | None
    sdk_name: str
    sdk_version: str
    api_version: str
    response_id: str | None
    response_status: str | None
    finish_reason: str | None
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    thought_tokens: int | None = None
    tool_use_tokens: int | None = None
    cached_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class PolicyProfile:
    """Static execution metadata that must stay fixed within a matched set."""

    policy_id: str
    policy_version: str
    runtime_kind: str
    evidence_scope: str
    real_model_configured: bool
    provider_id: str | None
    model_id: str | None
    model_version: str | None
    sdk_name: str | None
    sdk_version: str | None
    api_version: str | None
    sampling_parameters: Mapping[str, Any]
    system_prompt_hash: str
    model_tool_schema_hash: str | None


@dataclass(frozen=True)
class Decision:
    """Observable output from an agent policy."""

    answer: str
    reason_code: str
    sink_action: SinkAction | None = None
    model_call: ModelCallMetadata | None = None


@dataclass(frozen=True)
class SinkResult:
    """Result of evaluating an action in an isolated in-memory sink."""

    attempted: bool
    simulator_accepted: bool
    user_authorized: bool
    blocked: bool
    security_policy_violation: bool
    prohibited_simulated_effect: bool
    external_side_effect: bool
    reason_code: str
