from __future__ import annotations

import json
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

from tool_output_lab.conditions import build_tool_response
from tool_output_lab.domain import (
    Condition,
    PolicyInput,
    PreparedToolCall,
    ToolSelectionInput,
)
from tool_output_lab.experiment import ExperimentConfig, run_experiment
from tool_output_lab.llm import (
    BackendDecision,
    FakeLLMBackend,
    LLMBackendError,
    MalformedModelResponse,
    ModelBackedPolicy,
    fake_call_metadata,
)
from tool_output_lab.tasks import load_tasks
from tool_output_lab.tools import MockDocumentTool
from tool_output_lab.tracing import (
    validate_shared_preludes,
    validate_trace,
)


ROOT = Path(__file__).resolve().parents[1]


class ModelBackedPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = load_tasks(ROOT / "configs" / "tasks.json")[0]

    def prepare(
        self,
        policy: ModelBackedPolicy,
        *,
        matched_set_id: str = "synthetic-match-001",
    ) -> PreparedToolCall:
        return policy.prepare_tool_call(
            ToolSelectionInput(
                matched_set_id=matched_set_id,
                user_prompt=self.task.user_prompt,
                source_tool_name="synthetic_document_lookup",
                source_tool_arguments={"query": self.task.tool_query},
                prelude_seed=4321,
            )
        )

    def policy_input(
        self,
        condition: Condition,
        prepared: PreparedToolCall,
        *,
        matched_set_id: str = "synthetic-match-001",
    ) -> PolicyInput:
        return PolicyInput(
            matched_set_id=matched_set_id,
            user_prompt=self.task.user_prompt,
            tool_payload=build_tool_response(self.task, condition).payload,
            available_sink_ids=(self.task.eligible_sink,),
            run_seed=1234,
            source_tool_name="synthetic_document_lookup",
            source_tool_arguments={"query": self.task.tool_query},
            source_tool_call_id=prepared.provider_call_id,
            prepared_tool_call=prepared,
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
        prepared = self.prepare(policy)

        decision = policy.decide(
            self.policy_input(Condition.CLEAN, prepared)
        )

        self.assertEqual(decision.answer, self.task.public_answer)
        self.assertIsNone(decision.sink_action)
        self.assertIsNotNone(decision.model_call)
        self.assertFalse(policy.profile.real_model_configured)
        self.assertEqual(policy.profile.evidence_scope, "adapter_validation")

        rendered = json.loads(
            backend.requests[0].rendered_input(prepared)
        )
        self.assertEqual(
            [step["type"] for step in rendered],
            ["user_input", "function_call", "function_result"],
        )
        function_result = json.loads(rendered[2]["result"][0]["text"])
        self.assertEqual(
            set(function_result),
            {
                "confidential_token",
                "document_id",
                "operator_note",
                "public_answer",
            },
        )
        canonical_request = backend.requests[0].rendered_input(prepared)
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

        policy = ModelBackedPolicy(backend)
        prepared = self.prepare(policy)
        decision = policy.decide(
            self.policy_input(Condition.ATTACK, prepared)
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
                policy = ModelBackedPolicy(backend)
                prepared = self.prepare(policy)
                with self.assertRaises(MalformedModelResponse):
                    policy.decide(
                        self.policy_input(Condition.ATTACK, prepared)
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
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        validate_trace(result.events)
        self.assertFalse(result.policy_profile.real_model_configured)
        self.assertFalse(result.empirical_llm_evidence)
        self.assertEqual(len(backend.prelude_requests), 1)
        self.assertEqual(len(backend.requests), 3)
        self.assertEqual(len(result.preludes), 1)
        self.assertEqual(
            result.model_backend_accounting,
            {
                "shared_prelude_backend_invocations": 1,
                "shared_preludes_validated": 1,
                "post_tool_policy_invocations": 3,
                "post_tool_decisions_validated": 3,
                "real_model_post_tool_observations": 0,
                "total_backend_or_policy_invocations": 4,
            },
        )
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
                max_steps=2,
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

    def test_real_model_profile_and_metadata_enable_complete_triplet_evidence(
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
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertTrue(result.policy_profile.real_model_configured)
        self.assertEqual(result.empirical_llm_completed_runs, 3)
        self.assertTrue(result.any_empirical_llm_observation)
        self.assertEqual(result.complete_empirical_matched_sets, 1)
        self.assertTrue(result.empirical_llm_evidence)
        self.assertTrue(
            all(row.empirical_llm_observation for row in result.summaries)
        )

    def test_shared_prelude_is_condition_free_and_counted_once(self) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=fake_call_metadata(),
            )
        )
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="condition-free-prelude",
                repetitions=1,
                policy_name="fake-llm",
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertEqual(len(backend.prelude_requests), 1)
        prelude_request = backend.prelude_requests[0]
        serialized = json.dumps(
            {
                "input": prelude_request.user_input_step(),
                "source_tool": prelude_request.source_tool_schema(),
            },
            sort_keys=True,
        )
        for forbidden in (
            "attack",
            "CANARY-",
            "confidential_token",
            "operator_note",
            "placebo",
            "record_canary",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(len(result.preludes), 1)
        self.assertNotIn("condition", result.preludes[0])
        self.assertNotIn("payload_id", result.preludes[0])
        validate_shared_preludes(result.preludes, result.events)

        tampered_preludes = deepcopy(list(result.preludes))
        tampered_events = deepcopy(list(result.events))
        tampered_preludes[0]["tool_selection"][
            "arguments_sha256"
        ] = "not-a-sha256"
        for event in tampered_events:
            if event["event_type"] == "tool_call":
                event["data"]["argument_sha256"] = "not-a-sha256"
        with self.assertRaisesRegex(
            ValueError,
            "argument hash does not match",
        ):
            validate_shared_preludes(
                tampered_preludes,
                tampered_events,
            )

    def test_shared_prelude_validator_binds_branch_provenance(self) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=fake_call_metadata(),
            )
        )
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="prelude-provenance-validation",
                repetitions=1,
                policy_name="fake-llm",
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        for case in (
            "nested_prelude_id",
            "origin",
            "model_backend_invoked",
            "tool_name",
            "top_level_task",
            "provider_context_hash",
            "user_prompt_hash",
        ):
            with self.subTest(case=case):
                preludes = deepcopy(list(result.preludes))
                events = deepcopy(list(result.events))
                tool_call = next(
                    event
                    for event in events
                    if event["event_type"] == "tool_call"
                )
                if case == "nested_prelude_id":
                    tool_call["data"][
                        "shared_prelude_id"
                    ] = "different-prelude"
                elif case == "origin":
                    tool_call["data"]["origin"] = "fabricated_history"
                elif case == "model_backend_invoked":
                    preludes[0]["model_backend_invoked"] = 1
                elif case == "tool_name":
                    tool_call["data"]["tool_name"] = "different_tool"
                elif case == "top_level_task":
                    preludes[0]["task_id"] = "different-task"
                elif case == "provider_context_hash":
                    preludes[0]["tool_selection"][
                        "provider_context_sha256"
                    ] = "not-a-sha256"
                else:
                    preludes[0]["tool_selection"][
                        "user_prompt_sha256"
                    ] = "not-a-sha256"

                with self.assertRaises(ValueError):
                    validate_shared_preludes(preludes, events)

    def test_shared_prelude_failure_blocks_all_three_branches(self) -> None:
        backend = FakeLLMBackend(
            BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=fake_call_metadata(),
            ),
            prelude_responder=LLMBackendError(
                "synthetic prelude provider failure"
            ),
        )
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="shared-prelude-failure",
                repetitions=1,
                policy_name="fake-llm",
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertEqual(len(backend.prelude_requests), 1)
        self.assertEqual(len(backend.requests), 0)
        self.assertEqual(result.preludes[0]["status"], "error")
        self.assertTrue(
            all(row.status == "error" for row in result.summaries)
        )
        self.assertTrue(
            all(
                row.error_type == "SharedPreludeFailure"
                for row in result.summaries
            )
        )
        self.assertTrue(
            all(
                not row.post_model_call_attempted
                for row in result.summaries
            )
        )
        self.assertFalse(
            any(
                event["event_type"] == "tool_call"
                for event in result.events
            )
        )
        self.assertEqual(result.matched_comparisons, ())
        self.assertEqual(result.complete_matched_sets, 0)
        self.assertEqual(result.incomplete_matched_sets, 1)
        self.assertEqual(result.shared_prelude_failures, 1)
        validate_shared_preludes(result.preludes, result.events)

        forged_events = deepcopy(list(result.events))
        for event in forged_events:
            if event["event_type"] == "run_end":
                event["data"]["status"] = "completed"
        with self.assertRaisesRegex(
            ValueError,
            "inconsistent terminal semantics",
        ):
            validate_shared_preludes(result.preludes, forged_events)

    def test_one_post_failure_does_not_reexecute_shared_prelude(
        self,
    ) -> None:
        placebo_note = build_tool_response(
            self.task,
            Condition.PLACEBO,
        ).payload["operator_note"]

        def respond(request):
            if request.tool_payload["operator_note"] == placebo_note:
                raise LLMBackendError("synthetic post-tool failure")
            return BackendDecision(
                answer=self.task.public_answer,
                sink_action=None,
                metadata=fake_call_metadata(),
            )

        backend = FakeLLMBackend(respond)
        result = run_experiment(
            [self.task],
            ExperimentConfig(
                experiment_id="one-post-failure",
                repetitions=1,
                policy_name="fake-llm",
                max_steps=2,
            ),
            policy_factory=lambda: ModelBackedPolicy(backend),
        )

        self.assertEqual(len(backend.prelude_requests), 1)
        self.assertEqual(len(backend.requests), 3)
        self.assertEqual(
            sum(row.status == "completed" for row in result.summaries),
            2,
        )
        self.assertEqual(
            sum(row.status == "error" for row in result.summaries),
            1,
        )
        self.assertEqual(result.matched_comparisons, ())
        self.assertEqual(result.complete_matched_sets, 0)
        self.assertEqual(result.incomplete_matched_sets, 1)


if __name__ == "__main__":
    unittest.main()
