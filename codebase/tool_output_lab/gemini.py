"""Google Gemini adapter for one controlled post-tool decision."""

from __future__ import annotations

import os
import time
from importlib import metadata as package_metadata
from typing import Any, Mapping

from .domain import ModelCallMetadata
from .llm import (
    BackendDecision,
    DEFAULT_SIMULATED_SINK_IDS,
    LLMBackendError,
    LLMRequest,
    MalformedModelResponse,
    SINK_FUNCTION_NAME,
    safe_backend_error,
    sink_function_schema,
)
from .utils import canonical_json, sha256_text

DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
GOOGLE_GENAI_PACKAGE = "google-genai"
PINNED_GOOGLE_GENAI_VERSION = "2.13.0"
GEMINI_API_VERSION = "v1"
TERMINAL_INTERACTION_STATUSES = {"completed", "requires_action"}


class GeminiConfigurationError(ValueError):
    """The live adapter cannot be constructed safely."""


class GeminiBackend:
    """Use Gemini Interactions without automatic or external tool execution."""

    provider_id = "google-gemini"
    sdk_name = GOOGLE_GENAI_PACKAGE
    api_version = GEMINI_API_VERSION
    is_real_model = True
    sampling_parameters: Mapping[str, Any] = {
        "http_retry_attempts": 1,
        "max_output_tokens": 1_024,
        "seed_source": "matched_trace_seed",
        "thinking_level": "medium",
        "tool_choice": "auto",
    }
    model_tool_schema_hash = sha256_text(
        canonical_json(
            sink_function_schema(DEFAULT_SIMULATED_SINK_IDS)
        )
    )

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_GEMINI_MODEL,
        client: Any | None = None,
        api_key: str | None = None,
        sdk_version: str | None = None,
    ) -> None:
        if not model_id.strip():
            raise GeminiConfigurationError("Gemini model ID must not be empty")
        if model_id.endswith("-latest") or model_id.endswith("/latest"):
            raise GeminiConfigurationError(
                "Use a stable Gemini model ID, not a moving latest alias"
            )
        self.model_id = model_id
        self.model_version: str | None = model_id
        self._secrets: tuple[str, ...] = ()

        if client is not None:
            self._client = client
            self.sdk_version = sdk_version or self._installed_sdk_version(
                fallback="injected-client"
            )
            if api_key:
                self._secrets = (api_key,)
            return

        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not set; no live Gemini request was made"
            )
        try:
            from google import genai
        except ImportError as exc:
            raise GeminiConfigurationError(
                "Gemini support is not installed; install the 'gemini' extra"
            ) from exc

        installed_version = self._installed_sdk_version()
        if installed_version != PINNED_GOOGLE_GENAI_VERSION:
            raise GeminiConfigurationError(
                "Gemini SDK version mismatch: expected "
                f"{PINNED_GOOGLE_GENAI_VERSION}, found {installed_version}"
            )
        self._secrets = (resolved_key,)
        self.sdk_version = installed_version
        try:
            self._client = genai.Client(
                api_key=resolved_key,
                http_options={
                    "api_version": self.api_version,
                    "retry_options": {"attempts": 1},
                    "timeout": 120_000,
                },
            )
        except Exception as exc:
            raise GeminiConfigurationError(
                safe_backend_error(exc, secrets=self._secrets)
            ) from exc

    @staticmethod
    def _installed_sdk_version(*, fallback: str | None = None) -> str:
        try:
            return package_metadata.version(GOOGLE_GENAI_PACKAGE)
        except package_metadata.PackageNotFoundError:
            if fallback is not None:
                return fallback
            raise GeminiConfigurationError(
                "Gemini support is not installed; install the 'gemini' extra"
            ) from None

    def complete(self, request: LLMRequest) -> BackendDecision:
        started_ns = time.perf_counter_ns()
        try:
            interaction = self._client.interactions.create(
                model=self.model_id,
                input=request.interaction_input(),
                system_instruction=request.system_instruction,
                store=False,
                tools=[sink_function_schema(request.available_sink_ids)],
                generation_config={
                    "max_output_tokens": self.sampling_parameters[
                        "max_output_tokens"
                    ],
                    "seed": request.seed,
                    "thinking_level": self.sampling_parameters["thinking_level"],
                    "tool_choice": self.sampling_parameters["tool_choice"],
                },
            )
            latency_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
            return self._parse_interaction(interaction, latency_ms=latency_ms)
        except MalformedModelResponse:
            raise
        except Exception as exc:
            raise LLMBackendError(
                safe_backend_error(exc, secrets=self._secrets)
            ) from exc

    def _parse_interaction(
        self,
        interaction: Any,
        *,
        latency_ms: float,
    ) -> BackendDecision:
        status = self._optional_string(getattr(interaction, "status", None))
        if status not in TERMINAL_INTERACTION_STATUSES:
            raise MalformedModelResponse(
                f"Gemini interaction ended with non-terminal status {status!r}"
            )

        # Current Interactions responses may surface a function call under either
        # terminal status, so classify the observed steps instead of inferring
        # response shape from status alone.
        function_calls = [
            step
            for step in (getattr(interaction, "steps", None) or ())
            if getattr(step, "type", None) == "function_call"
        ]
        if len(function_calls) > 1:
            raise MalformedModelResponse(
                "Gemini returned more than one function call in a one-step policy"
            )

        output_text = getattr(interaction, "output_text", None)
        text_answer = output_text.strip() if isinstance(output_text, str) else ""
        sink_action: Mapping[str, Any] | None = None
        finish_reason: str

        if function_calls:
            call = function_calls[0]
            if getattr(call, "name", None) != SINK_FUNCTION_NAME:
                raise MalformedModelResponse(
                    "Gemini returned an unexpected function name"
                )
            raw_arguments = getattr(call, "arguments", None)
            if not isinstance(raw_arguments, Mapping):
                raise MalformedModelResponse(
                    "Gemini function arguments must be an object"
                )
            required = {"final_answer", "sink_id", "source_field", "value"}
            missing = sorted(required - set(raw_arguments))
            unknown = sorted(set(raw_arguments) - required)
            if missing:
                raise MalformedModelResponse(
                    f"Gemini function call is missing fields: {', '.join(missing)}"
                )
            if unknown:
                raise MalformedModelResponse(
                    f"Gemini function call has unknown fields: {', '.join(unknown)}"
                )
            function_answer = raw_arguments["final_answer"]
            if not isinstance(function_answer, str) or not function_answer.strip():
                raise MalformedModelResponse(
                    "Gemini function call final_answer must be a non-empty string"
                )
            answer = function_answer.strip()
            if text_answer and text_answer != answer:
                raise MalformedModelResponse(
                    "Gemini returned conflicting text and function-call answers"
                )
            sink_action = {
                "sink_id": raw_arguments["sink_id"],
                "operation": SINK_FUNCTION_NAME,
                "source_field": raw_arguments["source_field"],
                "value": raw_arguments["value"],
            }
            finish_reason = "function_call"
        else:
            if not text_answer:
                raise MalformedModelResponse(
                    "Gemini returned neither answer text nor a function call"
                )
            answer = text_answer
            finish_reason = "text"

        usage = getattr(interaction, "usage", None)
        observed_model = self._optional_string(
            getattr(interaction, "model", None)
        )
        if observed_model is not None and observed_model != self.model_id:
            raise MalformedModelResponse(
                "Gemini response model differs from the configured model ID"
            )
        metadata = ModelCallMetadata(
            provider_id=self.provider_id,
            model_id=self.model_id,
            model_version=observed_model or self.model_version,
            sdk_name=self.sdk_name,
            sdk_version=self.sdk_version,
            api_version=self.api_version,
            response_id=self._optional_string(
                getattr(interaction, "id", None)
            ),
            response_status=status,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
            input_tokens=self._usage_value(usage, "total_input_tokens"),
            output_tokens=self._usage_value(usage, "total_output_tokens"),
            thought_tokens=self._usage_value(usage, "total_thought_tokens"),
            tool_use_tokens=self._usage_value(usage, "total_tool_use_tokens"),
            cached_tokens=self._usage_value(usage, "total_cached_tokens"),
            total_tokens=self._usage_value(usage, "total_tokens"),
        )
        return BackendDecision(
            answer=answer,
            sink_action=sink_action,
            metadata=metadata,
        )

    @staticmethod
    def _optional_string(value: object) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _usage_value(usage: object, field: str) -> int | None:
        if usage is None:
            return None
        value = getattr(usage, field, None)
        return value if isinstance(value, int) and value >= 0 else None
