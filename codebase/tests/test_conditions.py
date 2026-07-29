from __future__ import annotations

import unittest
from pathlib import Path

from tool_output_lab.conditions import build_tool_response, validate_matched_triplet
from tool_output_lab.domain import Condition
from tool_output_lab.tasks import load_tasks


ROOT = Path(__file__).resolve().parents[1]


class MatchedConditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = load_tasks(ROOT / "configs" / "tasks.json")

    def test_every_task_has_a_valid_matched_triplet(self) -> None:
        for task in self.tasks:
            with self.subTest(task=task.task_id):
                validate_matched_triplet(task)

    def test_conditions_have_equal_schema_and_serialized_length(self) -> None:
        task = self.tasks[0]
        responses = {
            condition: build_tool_response(task, condition) for condition in Condition
        }
        self.assertEqual(
            len({tuple(response.payload) for response in responses.values()}), 1
        )
        self.assertEqual(
            len(
                {
                    len(response.raw_text.encode("utf-8"))
                    for response in responses.values()
                }
            ),
            1,
        )

    def test_condition_label_is_not_exposed_in_tool_payload(self) -> None:
        task = self.tasks[0]
        for condition in Condition:
            response = build_tool_response(task, condition)
            self.assertNotIn("condition", response.payload)
            self.assertNotIn('"condition"', response.raw_text)

    def test_only_declared_carrier_changes(self) -> None:
        task = self.tasks[0]
        responses = [build_tool_response(task, condition) for condition in Condition]
        for field in ("confidential_token", "document_id", "public_answer"):
            self.assertEqual(len({response.payload[field] for response in responses}), 1)
        self.assertEqual(
            len({response.payload["operator_note"] for response in responses}), 3
        )


if __name__ == "__main__":
    unittest.main()
