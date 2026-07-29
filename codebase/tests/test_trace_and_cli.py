from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tool_output_lab.cli import main
from tool_output_lab.experiment import ExperimentConfig, run_experiment
from tool_output_lab.llm import FakeLLMBackend, LLMBackendError
from tool_output_lab.tasks import load_tasks
from tool_output_lab.tracing import read_jsonl
from tool_output_lab.tracing import validate_trace
from tool_output_lab.tracing import validate_trace_records
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

    def test_trace_validator_enforces_terminal_grammar(self) -> None:
        task = load_tasks(ROOT / "configs" / "tasks.json")[0]
        result = run_experiment([task], ExperimentConfig(repetitions=1))

        forged_status = deepcopy(list(result.events))
        run_end = next(
            event
            for event in forged_status
            if event["condition"] == "clean"
            and event["event_type"] == "run_end"
        )
        run_end["data"]["status"] = "error"
        with self.assertRaisesRegex(
            ValueError,
            "Error run .* exactly one run_error",
        ):
            validate_trace(forged_status)

        forged_evaluability = deepcopy(list(result.events))
        evaluation = next(
            event
            for event in forged_evaluability
            if event["condition"] == "clean"
            and event["event_type"] == "task_evaluation"
        )
        evaluation["data"]["outcome_evaluable"] = False
        with self.assertRaisesRegex(
            ValueError,
            "must be outcome-evaluable",
        ):
            validate_trace(forged_evaluability)

        forged_phase_count = deepcopy(list(result.events))
        run_end = next(
            event
            for event in forged_phase_count
            if event["condition"] == "clean"
            and event["event_type"] == "run_end"
        )
        run_end["data"]["step_count"] = 0
        with self.assertRaisesRegex(
            ValueError,
            "step count disagrees with phase flags",
        ):
            validate_trace(forged_phase_count)

    def test_trace_records_require_complete_matched_triplet(self) -> None:
        task = load_tasks(ROOT / "configs" / "tasks.json")[0]
        result = run_experiment([task], ExperimentConfig(repetitions=1))
        truncated = [
            event
            for event in result.events
            if event["condition"] != "attack"
        ]

        with self.assertRaisesRegex(
            ValueError,
            "exactly clean, placebo, and attack",
        ):
            validate_trace_records(truncated)

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

    def test_gemini_cli_missing_key_creates_no_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "gemini.jsonl"
            summary_path = Path(temp_dir) / "gemini.summary.json"
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, {}, clear=True),
                redirect_stdout(io.StringIO()),
                redirect_stderr(stderr),
            ):
                exit_code = main(
                    [
                        "run",
                        "--policy",
                        "gemini",
                        "--trace",
                        str(trace_path),
                        "--summary",
                        str(summary_path),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertFalse(trace_path.exists())
            self.assertFalse(summary_path.exists())
            self.assertIn("GEMINI_API_KEY", stderr.getvalue())
            self.assertIn("no live Gemini request", stderr.getvalue())

    def test_gemini_cli_requires_confirmation_for_custom_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            custom_tasks = temp_root / "custom-tasks.json"
            custom_tasks.write_text(
                (ROOT / "configs" / "tasks.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            trace_path = temp_root / "custom.jsonl"
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "run",
                        "--policy",
                        "gemini",
                        "--tasks",
                        str(custom_tasks),
                        "--trace",
                        str(trace_path),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertFalse(trace_path.exists())
            self.assertIn(
                "--allow-custom-synthetic-tasks",
                stderr.getvalue(),
            )

    def test_cli_rejects_artifacts_inside_shared_repository(self) -> None:
        paths = (
            ROOT / "results" / "must-not-be-created.jsonl",
            ROOT.parent / "outputs" / "must-not-be-created.jsonl",
        )
        for trace_path in paths:
            with self.subTest(trace_path=trace_path):
                summary_path = trace_path.with_suffix(".summary.json")
                stderr = io.StringIO()
                with (
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(stderr),
                ):
                    exit_code = main(
                        [
                            "run",
                            "--trace",
                            str(trace_path),
                            "--summary",
                            str(summary_path),
                        ]
                    )
                self.assertEqual(exit_code, 2)
                self.assertFalse(trace_path.exists())
                self.assertFalse(summary_path.exists())
                self.assertIn(
                    "outside the shared repository",
                    stderr.getvalue(),
                )

    def test_gemini_cli_returns_failure_when_all_model_runs_error(self) -> None:
        class FailingRealBackend(FakeLLMBackend):
            provider_id = "google-gemini"
            model_id = "gemini-3.6-flash"
            model_version = "gemini-3.6-flash"
            sdk_name = "google-genai"
            sdk_version = "2.13.0"
            api_version = "v1"
            is_real_model = True
            sampling_parameters = {
                "http_max_attempts_including_initial": 1,
                "post_tool_max_output_tokens": 1_024,
                "post_tool_thinking_level": "medium",
                "post_tool_tool_choice": "validated_sink_only",
                "pre_tool_max_output_tokens": 512,
                "pre_tool_thinking_level": "medium",
                "pre_tool_tool_choice": "any_source_only",
                "seed_source": "matched_phase_seeds",
                "store": False,
            }
            model_tool_schema_hash = (
                FakeLLMBackend.model_tool_schema_hash
            )

            def __init__(self):
                def fail(request):
                    raise LLMBackendError(
                        "synthetic provider failure"
                    )

                super().__init__(fail)

        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "gemini.jsonl"
            summary_path = Path(temp_dir) / "gemini.summary.json"
            stdout = io.StringIO()
            with (
                patch(
                    "tool_output_lab.cli.GeminiBackend",
                    return_value=FailingRealBackend(),
                ),
                redirect_stdout(stdout),
                redirect_stderr(io.StringIO()),
            ):
                exit_code = main(
                    [
                        "run",
                        "--policy",
                        "gemini",
                        "--trace",
                        str(trace_path),
                        "--summary",
                        str(summary_path),
                    ]
                )
            output = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(output["scheduled_runs"], 9)
            self.assertEqual(output["error_runs"], 9)
            self.assertEqual(output["completed_runs"], 0)
            self.assertTrue(output["real_model_configured"])
            self.assertEqual(output["empirical_llm_completed_runs"], 0)
            self.assertFalse(output["empirical_llm_evidence"])
            self.assertEqual(
                output["model_backend_accounting"],
                {
                    "post_tool_decisions_validated": 0,
                    "post_tool_policy_invocations": 9,
                    "real_model_post_tool_observations": 0,
                    "shared_prelude_backend_invocations": 3,
                    "shared_preludes_validated": 3,
                    "total_backend_or_policy_invocations": 12,
                },
            )
            self.assertTrue(trace_path.exists())
            self.assertTrue(summary_path.exists())
            events = read_jsonl(trace_path)
            validate_trace_records(events)
            prelude_records = [
                event
                for event in events
                if event["schema_version"] == "matched-set-prelude-v1"
            ]
            self.assertEqual(len(prelude_records), 3)
            for prelude in prelude_records:
                self.assertNotIn("condition", prelude)
                self.assertNotIn("payload_id", prelude)
                self.assertNotIn("run_id", prelude)
                serialized_prelude = canonical_json(prelude)
                self.assertNotIn("provider_context_json", serialized_prelude)
                self.assertNotIn('"signature"', serialized_prelude)
            self.assertEqual(
                {event["transport"] for event in events},
                {"google_gemini_interactions_v1"},
            )
            self.assertTrue(
                all(
                    event["code_commit"] != "uncommitted-working-tree"
                    for event in events
                )
            )


if __name__ == "__main__":
    unittest.main()
