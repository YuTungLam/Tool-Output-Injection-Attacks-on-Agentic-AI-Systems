from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path

from tool_output_lab.conditions import build_tool_response
from tool_output_lab.domain import Condition, PolicyInput
from tool_output_lab.experiment import ExperimentConfig, run_experiment
from tool_output_lab.llm import (
    BackendDecision,
    FakeLLMBackend,
    MalformedModelResponse,
    ModelBackedPolicy,
    fake_call_metadata,
)
from tool_output_lab.tasks import load_tasks
from tool_output_lab.tools import MockDocumentTool
from tool_output_lab.tracing import validate_trace


ROOT = Path(__file__).resolve().parents[1]


class ModelBackedPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = load_tasks(ROOT / "configs" / "tasks.json")[0]

    def policy_input(self, condition: Condition) -> PolicyInput:
        return PolicyInput(
            user_prompt=self.task.user_prompt,
            tool_payload=build_tool_response(self.task, condition).payload,
            available_sink_ids=(self.task.eligible_sink,),
            run_seed=1234,
            source_tool_name="synthetic_document_lookup",
            source_tool_arguments={"query": self.task.tool_query},
            source_tool_call_id="synthetic-call-001",
        )

    def test_fake_backend_maps_text_decision_without_claiming_llm_evidence(
        self,
    ) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=fake_call_metadata(),
            )
        )
        policy = ModelBackedPolicy(backend)

        decision = policy.decide(self.policy_input(Condition.CLEAN))

        self.assertEqual(decision.answer, self.task.public_answer)
        self.assertIsNone(decision.sink_action)
        self.assertIsNotNone(decision.model_call)
        self.assertFalse(policy.profile.real_model_configured)
        self.assertEqual(policy.profile.evidence_scope, "adapter_validation")

        rendered = json.loads(backend.requests[0].rendered_input())
        self.assertEqual(
            [step["type"] for step in rendered],
            ["user_input", "function_call", "function_result"],
        )
        function_result = json.loads(rendered[2]["result"])
        self.assertEqual(
            set(function_result),
            {
                "confidential_token",
                "document_id",
                "operator_note",
                "public_answer",
            },
        )
        canonical_request = backend.requests[0].rendered_input()
        self.assertNotIn('"condition"', canonical_request)
        self.assertNotIn("expected_answer", canonical_request)
        self.assertNotIn("ground_truth", canonical_request)

    def test_fake_backend_maps_valid_sink_decision(self) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action={
                    "sink_id": self.task.eligible_sink,
                    "operation": "record_canary",
                    "value": self.task.confidential_token,
                    "source_field": "confidential_token",
                },
                metadata=fake_call_metadata(response_status="requires_action"),
            )
        )

        decision = ModelBackedPolicy(backend).decide(
            self.policy_input(Condition.ATTACK)
        )

        self.assertIsNotNone(decision.sink_action)
        self.assertEqual(
            decision.sink_action.value,
            self.task.confidential_token,
        )
        self.assertEqual(
            decision.reason_code,
            "model_requested_simulated_sink",
        )

    def test_malformed_or_unavailable_sink_decisions_fail_closed(self) -> None:
        cases = (
            {
                "sink_id": self.task.eligible_sink,
                "operation": "record_canary",
                "value": self.task.confidential_token,
            },
            {
                "sink_id": "undeclared_sink",
                "operation": "record_canary",
                "value": self.task.confidential_token,
                "source_field": "confidential_token",
            },
            {
                "sink_id": self.task.eligible_sink,
                "operation": "send_external",
                "value": self.task.confidential_token,
                "source_field": "confidential_token",
            },
        )
        for sink_action in cases:
            with self.subTest(sink_action=sink_action):
                backend = FakeLLMBackend(
                    BackendDecision(
                        answer=self.task.public_answer,
                        sink_action=sink_action,
                        metadata=fake_call_metadata(),
                    )
                )
                with self.assertRaises(MalformedModelResponse):
                    ModelBackedPolicy(backend).decide(
                        self.policy_input(Condition.ATTACK)
                    )

    def test_fake_model_experiment_preserves_matched_trace_boundaries(self) -> None:
        def respond(request):
            malicious = "SYSTEM OVERRIDE" in request.tool_payload["operator_note"]
            action = (
                {
                    "sink_id": request.available_sink_ids[0],
                    "operation": "record_canary",
                    "value": request.tool_payload["confidential_token"],
                    "source_field": "confidential_token",
                }
                if malicious
                else None
            )
            return BackendDecision(
                answer=f"{request.tool_payload['public_answer']}.",
                sink_action=action,
                metadata=fake_call_metadata(
                    response_status=(
                        "requires_action" if malicious else "completed"
                    )
                ),
            )

        backend = FakeLLMBackend(respond)
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="fake-adapter-test",
                repetitions=1,
                policy_name="fake-llm",
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        validate_trace(result.events)
        self.assertFalse(result.policy_profile.real_model_configured)
        self.assertFalse(result.empirical_llm_evidence)
        self.assertEqual(len(backend.requests), 3)
        self.assertEqual(
            len(
                {
                    request.source_tool_call_id
                    for request in backend.requests
                }
            ),
            1,
        )
        self.assertEqual(
            len({request.seed for request in backend.requests}),
            1,
        )
        self.assertEqual(
            len(
                {
                    json.dumps(
                        dict(request.source_tool_arguments),
                        sort_keys=True,
                    )
                    for request in backend.requests
                }
            ),
            1,
        )
        for stable_field in (
            "confidential_token",
            "document_id",
            "public_answer",
        ):
            self.assertEqual(
                len(
                    {
                        request.tool_payload[stable_field]
                        for request in backend.requests
                    }
                ),
                1,
            )
        self.assertEqual(
            len(
                {
                    request.tool_payload["operator_note"]
                    for request in backend.requests
                }
            ),
            3,
        )
        self.assertTrue(all(row.task_success for row in result.summaries))
        attack = next(row for row in result.summaries if row.condition == "attack")
        controls = [
            row for row in result.summaries if row.condition != "attack"
        ]
        self.assertTrue(attack.sink_attempted)
        self.assertTrue(attack.prohibited_simulated_effect)
        self.assertTrue(all(not row.sink_attempted for row in controls))

        agent_events = [
            event
            for event in result.events
            if event["event_type"] == "agent_decision"
        ]
        self.assertEqual(len(agent_events), 3)
        self.assertTrue(
            all(event["data"]["model_call"] is not None for event in agent_events)
        )
        self.assertTrue(
            all(
                event["sampling_parameters"] == {"deterministic": True}
                for event in agent_events
            )
        )
        self.assertEqual(
            len({event["tool_schema_hash"] for event in result.events}),
            1,
        )
        self.assertNotEqual(
            result.events[0]["tool_schema_hash"],
            MockDocumentTool.schema_hash,
        )

    def test_malformed_model_output_is_non_evaluable_run_error(self) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer="",
                sink_action=None,
                metadata=fake_call_metadata(),
            )
        )
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="fake-adapter-error",
                repetitions=1,
                policy_name="fake-llm",
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertTrue(all(row.status == "error" for row in result.summaries))
        self.assertTrue(
            all(not row.outcome_evaluable for row in result.summaries)
        )
        self.assertTrue(
            all(
                row.error_type == "MalformedModelResponse"
                for row in result.summaries
            )
        )
        self.assertEqual(result.matched_comparisons, ())
        events_by_id = {
            event["event_id"]: event for event in result.events
        }
        for error_event in (
            event
            for event in result.events
            if event["event_type"] == "run_error"
        ):
            parent = events_by_id[error_event["parent_event_id"]]
            self.assertEqual(parent["event_type"], "tool_result_exposed")
        validate_trace(result.events)

    def test_successful_real_backend_is_required_for_empirical_evidence(
        self,
    ) -> None:
        metadata = replace(
            fake_call_metadata(),
            provider_id="google-gemini",
            model_id="gemini-3.6-flash",
            model_version="gemini-3.6-flash",
            sdk_name="google-genai",
            sdk_version="2.13.0",
            api_version="v1",
        )
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=metadata,
            )
        )
        backend.provider_id = metadata.provider_id
        backend.model_id = metadata.model_id
        backend.model_version = metadata.model_version
        backend.sdk_name = metadata.sdk_name
        backend.sdk_version = metadata.sdk_version
        backend.api_version = metadata.api_version
        backend.is_real_model = True

        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="real-backend-evidence-test",
                repetitions=1,
                policy_name="stub-real-llm",
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertTrue(result.policy_profile.real_model_configured)
        self.assertEqual(result.empirical_llm_completed_runs, 3)
        self.assertTrue(result.empirical_llm_evidence)
        self.assertTrue(
            all(row.empirical_llm_observation for row in result.summaries)
        )


if __name__ == "__main__":
    unittest.main()
