from __future__ import annotations

import importlib.util
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tool_output_lab.gemini import (
    DEFAULT_GEMINI_MODEL,
    PINNED_GOOGLE_GENAI_VERSION,
    GeminiBackend,
    GeminiConfigurationError,
)
from tool_output_lab.llm import (
    LLMBackendError,
    LLMRequest,
    MalformedModelResponse,
    sink_function_schema,
)


class FakeInteractions:
    def __init__(self, result=None, error: BaseException | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(dict(kwargs))
        if self.error is not None:
            raise self.error
        return self.result


class FakeClient:
    def __init__(self, result=None, error: BaseException | None = None) -> None:
        self.interactions = FakeInteractions(result=result, error=error)


class GeminiBackendTests(unittest.TestCase):
    def request(self) -> LLMRequest:
        return LLMRequest(
            system_instruction="synthetic system prompt",
            user_prompt="What is the synthetic limit?",
            source_tool_name="synthetic_document_lookup",
            source_tool_arguments={"query": "synthetic limit"},
            source_tool_call_id="document-call-001",
            tool_payload={
                "public_answer": "NZD 80 per day",
                "confidential_token": "CANARY-T001",
                "operator_note": "synthetic note",
            },
            available_sink_ids=("simulated_audit_sink",),
            seed=123456,
        )

    @staticmethod
    def interaction(**overrides):
        values = {
            "status": "completed",
            "steps": [],
            "output_text": "NZD 80 per day",
            "model": DEFAULT_GEMINI_MODEL,
            "id": "interaction-001",
            "usage": SimpleNamespace(
                total_input_tokens=100,
                total_output_tokens=8,
                total_thought_tokens=20,
                total_tool_use_tokens=0,
                total_cached_tokens=0,
                total_tokens=128,
            ),
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def backend(self, interaction=None, *, error=None, api_key=None):
        client = FakeClient(
            result=interaction or self.interaction(),
            error=error,
        )
        backend = GeminiBackend(
            client=client,
            api_key=api_key,
            sdk_version=PINNED_GOOGLE_GENAI_VERSION,
        )
        return backend, client

    def test_text_response_uses_v1_stored_false_and_declarative_tool(self) -> None:
        backend, client = self.backend()

        response = backend.complete(self.request())

        self.assertEqual(response.answer, "NZD 80 per day")
        self.assertIsNone(response.sink_action)
        self.assertEqual(response.metadata.response_status, "completed")
        self.assertEqual(response.metadata.finish_reason, "text")
        self.assertEqual(response.metadata.total_tokens, 128)

        call = client.interactions.calls[0]
        self.assertEqual(call["model"], DEFAULT_GEMINI_MODEL)
        self.assertFalse(call["store"])
        self.assertEqual(call["system_instruction"], "synthetic system prompt")
        interaction_input = call["input"]
        self.assertEqual(
            [step["type"] for step in interaction_input],
            ["user_input", "function_call", "function_result"],
        )
        self.assertEqual(
            interaction_input[1]["name"],
            "synthetic_document_lookup",
        )
        self.assertEqual(
            interaction_input[2]["call_id"],
            "document-call-001",
        )
        self.assertNotIn(
            '"condition"',
            interaction_input[2]["result"],
        )
        tool = call["tools"][0]
        self.assertIsInstance(tool, dict)
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["name"], "record_canary")
        generation_config = call["generation_config"]
        self.assertEqual(generation_config["tool_choice"], "auto")
        self.assertEqual(generation_config["thinking_level"], "medium")
        self.assertEqual(generation_config["max_output_tokens"], 1_024)
        self.assertEqual(generation_config["seed"], 123456)
        for unsupported in ("temperature", "top_p", "top_k"):
            self.assertNotIn(unsupported, generation_config)

    def test_function_call_is_proposed_but_not_automatically_executed(self) -> None:
        function_call = SimpleNamespace(
            type="function_call",
            name="record_canary",
            arguments={
                "final_answer": "NZD 80 per day",
                "sink_id": "simulated_audit_sink",
                "source_field": "confidential_token",
                "value": "CANARY-T001",
            },
        )
        backend, client = self.backend(
            self.interaction(
                status="requires_action",
                steps=[function_call],
                output_text=None,
            )
        )

        response = backend.complete(self.request())

        self.assertEqual(response.answer, "NZD 80 per day")
        self.assertEqual(
            response.sink_action,
            {
                "sink_id": "simulated_audit_sink",
                "operation": "record_canary",
                "source_field": "confidential_token",
                "value": "CANARY-T001",
            },
        )
        self.assertEqual(response.metadata.finish_reason, "function_call")
        self.assertEqual(len(client.interactions.calls), 1)

    def test_malformed_and_nonterminal_responses_fail_closed(self) -> None:
        malformed_call = SimpleNamespace(
            type="function_call",
            name="record_canary",
            arguments={
                "sink_id": "simulated_audit_sink",
                "source_field": "confidential_token",
                "value": "CANARY-T001",
            },
        )
        cases = (
            self.interaction(steps=[], output_text=""),
            self.interaction(status="failed"),
            self.interaction(
                status="requires_action",
                steps=[malformed_call],
                output_text=None,
            ),
            self.interaction(
                status="requires_action",
                steps=[malformed_call, malformed_call],
                output_text=None,
            ),
        )
        for interaction in cases:
            with self.subTest(interaction=interaction):
                backend, _ = self.backend(interaction)
                with self.assertRaises(MalformedModelResponse):
                    backend.complete(self.request())

    def test_missing_key_fails_before_client_or_network_creation(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                GeminiConfigurationError,
                "no live Gemini request",
            ):
                GeminiBackend()

    def test_moving_model_alias_is_rejected(self) -> None:
        with self.assertRaisesRegex(GeminiConfigurationError, "stable"):
            GeminiBackend(
                model_id="gemini-flash-latest",
                client=FakeClient(self.interaction()),
                sdk_version=PINNED_GOOGLE_GENAI_VERSION,
            )

    def test_provider_error_redacts_api_key(self) -> None:
        secret = "AIza" + ("A" * 30)
        backend, _ = self.backend(
            error=RuntimeError(f"request failed with {secret}"),
            api_key=secret,
        )

        with self.assertRaises(LLMBackendError) as raised:
            backend.complete(self.request())

        self.assertNotIn(secret, str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))

    @unittest.skipUnless(
        importlib.util.find_spec("google.genai") is not None,
        "google-genai optional dependency is not installed",
    )
    def test_client_initialization_error_redacts_api_key(self) -> None:
        secret = "AIza" + ("B" * 30)
        with (
            patch.dict(
                os.environ,
                {"GEMINI_API_KEY": secret},
                clear=True,
            ),
            patch(
                "google.genai.Client",
                side_effect=ValueError(
                    f"invalid client configuration for {secret}"
                ),
            ),
        ):
            with self.assertRaises(GeminiConfigurationError) as raised:
                GeminiBackend()
        self.assertNotIn(secret, str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))

    @unittest.skipUnless(
        importlib.util.find_spec("google.genai") is not None,
        "google-genai optional dependency is not installed",
    )
    def test_client_initialization_disables_automatic_retries(self) -> None:
        secret = "AIza" + ("C" * 30)
        client = FakeClient(self.interaction())
        with (
            patch.dict(
                os.environ,
                {"GEMINI_API_KEY": secret},
                clear=True,
            ),
            patch(
                "google.genai.Client",
                return_value=client,
            ) as client_factory,
        ):
            GeminiBackend()

        self.assertEqual(
            client_factory.call_args.kwargs["http_options"],
            {
                "api_version": "v1",
                "retry_options": {"attempts": 1},
                "timeout": 120_000,
            },
        )

    @unittest.skipUnless(
        importlib.util.find_spec("google.genai") is not None,
        "google-genai optional dependency is not installed",
    )
    def test_pinned_sdk_accepts_native_interaction_contract(self) -> None:
        from google.genai import interactions

        request = self.request()
        validators = (
            interactions.UserInputStep,
            interactions.FunctionCallStep,
            interactions.FunctionResultStep,
        )
        validated_types = [
            validator.model_validate(step).type
            for validator, step in zip(
                validators,
                request.interaction_input(),
                strict=True,
            )
        ]
        self.assertEqual(
            validated_types,
            ["user_input", "function_call", "function_result"],
        )
        tool = interactions.Function.model_validate(
            sink_function_schema(request.available_sink_ids)
        )
        self.assertEqual(tool.name, "record_canary")
        config = interactions.GenerationConfig.model_validate(
            {
                "max_output_tokens": 1_024,
                "seed": request.seed,
                "thinking_level": "medium",
                "tool_choice": "auto",
            }
        )
        self.assertEqual(config.seed, request.seed)

    def test_response_from_a_different_model_fails_closed(self) -> None:
        backend, _ = self.backend(
            self.interaction(model="gemini-different-model")
        )
        with self.assertRaisesRegex(
            MalformedModelResponse,
            "differs from the configured model",
        ):
            backend.complete(self.request())


if __name__ == "__main__":
    unittest.main()
