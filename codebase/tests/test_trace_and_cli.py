from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tool_output_lab.cli import main
from tool_output_lab.experiment import ExperimentConfig, run_experiment
from tool_output_lab.tasks import load_tasks
from tool_output_lab.tracing import read_jsonl
from tool_output_lab.tracing import validate_trace
from tool_output_lab.utils import canonical_json


ROOT = Path(__file__).resolve().parents[1]


class TraceAndCliTests(unittest.TestCase):
    def test_jsonl_is_canonical_and_complete(self) -> None:
        task = load_tasks(ROOT / "configs" / "tasks.json")[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            run_experiment(
                [task],
                ExperimentConfig(repetitions=1),
                trace_path=trace_path,
            )
            raw_lines = trace_path.read_text(encoding="utf-8").splitlines()
            events = read_jsonl(trace_path)
            self.assertEqual(len(raw_lines), len(events))
            self.assertTrue(trace_path.read_bytes().endswith(b"\n"))
            for raw_line, event in zip(raw_lines, events, strict=True):
                self.assertEqual(raw_line, canonical_json(event))
                for field in (
                    "schema_version",
                    "run_id",
                    "matched_set_id",
                    "condition",
                    "event_index",
                    "event_type",
                    "data",
                ):
                    self.assertIn(field, event)

    def test_cli_writes_declared_artifacts_and_reports_no_external_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "pilot.jsonl"
            summary_path = Path(temp_dir) / "pilot.summary.json"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "run",
                        "--tasks",
                        str(ROOT / "configs" / "tasks.json"),
                        "--trace",
                        str(trace_path),
                        "--summary",
                        str(summary_path),
                        "--repetitions",
                        "1",
                    ]
                )
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["external_side_effects"], 0)
            self.assertFalse(output["empirical_llm_evidence"])
            self.assertEqual(output["runtime_kind"], "scripted_control")
            self.assertEqual(output["evidence_scope"], "instrumentation_validation")
            self.assertEqual(output["scheduled_runs"], 15)
            self.assertTrue(trace_path.exists())
            self.assertTrue(summary_path.exists())

    def test_cli_refuses_to_overwrite_without_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "pilot.jsonl"
            trace_path.write_text("sentinel", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "run",
                        "--tasks",
                        str(ROOT / "configs" / "tasks.json"),
                        "--trace",
                        str(trace_path),
                    ]
                )
            self.assertEqual(exit_code, 1)
            self.assertEqual(trace_path.read_text(encoding="utf-8"), "sentinel")
            self.assertIn("Refusing to overwrite", stderr.getvalue())

    def test_trace_validator_rejects_empty_and_corrupt_traces(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one event"):
            validate_trace([])

        task = load_tasks(ROOT / "configs" / "tasks.json")[0]
        result = run_experiment([task], ExperimentConfig(repetitions=1))
        missing_field = [dict(event) for event in result.events]
        missing_field[0].pop("schema_version")
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_trace(missing_field)

        changed_context = [dict(event) for event in result.events]
        changed_context[1]["task_id"] = "different-task"
        with self.assertRaisesRegex(ValueError, "invariant fields"):
            validate_trace(changed_context)

        broken_parent = [dict(event) for event in result.events]
        broken_parent[1]["parent_event_id"] = "nonexistent-event"
        with self.assertRaisesRegex(ValueError, "preceding parent"):
            validate_trace(broken_parent)

    def test_trace_and_summary_paths_cannot_alias(self) -> None:
        task = load_tasks(ROOT / "configs" / "tasks.json")[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "same-output.json"
            with self.assertRaisesRegex(ValueError, "different files"):
                run_experiment(
                    [task],
                    ExperimentConfig(repetitions=1),
                    trace_path=output_path,
                    summary_path=output_path,
                    overwrite=True,
                )
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
