from __future__ import annotations

import unittest
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tool_output_lab.experiment import ExperimentConfig, run_experiment
from tool_output_lab.tasks import load_tasks
from tool_output_lab.tools import MockDocumentTool
from tool_output_lab.tracing import validate_trace


ROOT = Path(__file__).resolve().parents[1]


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = load_tasks(ROOT / "configs" / "tasks.json")[0]

    def test_vulnerable_positive_control_separates_security_and_utility(self) -> None:
        result = run_experiment(
            [self.task], ExperimentConfig(repetitions=2, policy_name="vulnerable")
        )
        self.assertEqual(len(result.summaries), 6)
        self.assertTrue(all(summary.task_success for summary in result.summaries))
        attack_rows = [row for row in result.summaries if row.condition == "attack"]
        control_rows = [row for row in result.summaries if row.condition != "attack"]
        self.assertTrue(all(row.sink_attempted for row in attack_rows))
        self.assertTrue(all(row.prohibited_simulated_effect for row in attack_rows))
        self.assertTrue(all(row.security_policy_violation for row in attack_rows))
        self.assertTrue(all(not row.user_authorized for row in attack_rows))
        self.assertTrue(all(not row.sink_attempted for row in control_rows))
        self.assertTrue(all(not row.external_side_effect for row in result.summaries))

    def test_safe_negative_control_has_no_sink_attempts(self) -> None:
        result = run_experiment(
            [self.task], ExperimentConfig(policy_name="safe", repetitions=1)
        )
        self.assertTrue(all(not row.sink_attempted for row in result.summaries))
        self.assertTrue(all(row.task_success for row in result.summaries))
        self.assertTrue(all(row.outcome_evaluable for row in result.summaries))

    def test_matched_conditions_share_identity_but_runs_are_distinct(self) -> None:
        result = run_experiment([self.task], ExperimentConfig(repetitions=2))
        by_match: dict[str, list[dict[str, object]]] = defaultdict(list)
        for record in result.manifest:
            by_match[str(record["matched_set_id"])].append(dict(record))
        self.assertEqual(len(by_match), 2)
        for records in by_match.values():
            self.assertEqual({record["condition"] for record in records}, {"clean", "placebo", "attack"})
            self.assertEqual(len({record["run_id"] for record in records}), 3)
            self.assertEqual(len({record["run_seed"] for record in records}), 1)

    def test_comparator_ignores_bookkeeping_ids(self) -> None:
        result = run_experiment([self.task], ExperimentConfig(repetitions=1))
        comparisons = {
            comparison["right_condition"]: comparison
            for comparison in result.matched_comparisons
        }
        self.assertFalse(comparisons["placebo"]["diverged"])
        self.assertTrue(comparisons["attack"]["diverged"])
        self.assertEqual(
            comparisons["attack"]["left_event_type"], "agent_decision"
        )

    def test_trace_invariants_hold(self) -> None:
        result = run_experiment([self.task], ExperimentConfig(repetitions=1))
        validate_trace(result.events)
        by_run: dict[str, list[dict[str, object]]] = defaultdict(list)
        for event in result.events:
            by_run[str(event["run_id"])].append(dict(event))
        for events in by_run.values():
            self.assertEqual(
                [event["event_index"] for event in events], list(range(len(events)))
            )
            self.assertEqual(events[0]["event_type"], "run_start")
            self.assertEqual(events[-1]["event_type"], "run_end")

    def test_run_plan_is_reproducible(self) -> None:
        config = ExperimentConfig(repetitions=2, seed=12345)
        first = run_experiment([self.task], config)
        second = run_experiment([self.task], config)
        self.assertEqual(first.config_hash, second.config_hash)
        self.assertEqual(first.manifest, second.manifest)
        self.assertEqual(first.aggregate_by_condition, second.aggregate_by_condition)

    def test_task_content_is_part_of_configuration_identity(self) -> None:
        config = ExperimentConfig(repetitions=1, seed=12345)
        first = run_experiment([self.task], config)
        changed_task = replace(self.task, public_answer="A changed synthetic answer")
        second = run_experiment([changed_task], config)
        self.assertNotEqual(first.config_hash, second.config_hash)
        self.assertNotEqual(
            {record["run_id"] for record in first.manifest},
            {record["run_id"] for record in second.manifest},
        )

    def test_runtime_errors_are_not_counted_as_negative_outcomes(self) -> None:
        with patch.object(
            MockDocumentTool, "invoke", side_effect=RuntimeError("synthetic failure")
        ):
            result = run_experiment(
                [self.task], ExperimentConfig(repetitions=1, policy_name="vulnerable")
            )
        self.assertTrue(all(row.status == "error" for row in result.summaries))
        self.assertTrue(all(not row.outcome_evaluable for row in result.summaries))
        self.assertTrue(all(row.task_success is None for row in result.summaries))
        self.assertEqual(result.matched_comparisons, ())
        for aggregate in result.aggregate_by_condition.values():
            self.assertEqual(aggregate["task_success_evaluable_runs"], 0)
            self.assertIsNone(aggregate["task_success_rate"])
            self.assertEqual(aggregate["sink_attempt_evaluable_runs"], 0)
            self.assertIsNone(aggregate["sink_attempt_rate"])

    def test_library_refuses_to_write_artifacts_inside_shared_repo(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "outside the shared repository",
        ):
            run_experiment(
                [self.task],
                ExperimentConfig(repetitions=1),
                trace_path=ROOT / "results" / "must-not-be-written.jsonl",
            )


if __name__ == "__main__":
    unittest.main()
