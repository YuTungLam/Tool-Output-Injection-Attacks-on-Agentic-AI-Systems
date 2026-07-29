"""Command-line entry point for the instrumentation pilot."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

from .experiment import (
    ExperimentConfig,
    require_external_artifact_path,
    run_experiment,
)
from .gemini import DEFAULT_GEMINI_MODEL, GeminiBackend
from .llm import ModelBackedPolicy
from .policy import AgentPolicy
from .tasks import load_tasks
from .utils import canonical_json

CODEBASE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = CODEBASE_ROOT.parent
DEFAULT_TASKS_PATH = CODEBASE_ROOT / "configs" / "tasks.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tool_output_lab",
        description="Run the sandboxed matched tool-output injection pilot.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run all matched conditions")
    run_parser.add_argument(
        "--tasks",
        type=Path,
        default=DEFAULT_TASKS_PATH,
        help="path to the synthetic task JSON file",
    )
    run_parser.add_argument(
        "--allow-custom-synthetic-tasks",
        action="store_true",
        help=(
            "confirm that a custom Gemini task file contains synthetic, "
            "non-private data only"
        ),
    )
    run_parser.add_argument(
        "--trace",
        type=Path,
        required=True,
        help="output JSONL trace path outside the shared repository",
    )
    run_parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="output summary JSON path (defaults next to the trace)",
    )
    run_parser.add_argument("--experiment-id", default=None)
    run_parser.add_argument(
        "--repetitions",
        type=int,
        default=None,
        help="matched repetitions (defaults to 3 for Gemini and 2 for scripts)",
    )
    run_parser.add_argument("--seed", type=int, default=20260723)
    run_parser.add_argument(
        "--policy",
        choices=("vulnerable", "safe", "gemini"),
        default="vulnerable",
    )
    run_parser.add_argument(
        "--model",
        default=DEFAULT_GEMINI_MODEL,
        help="fixed Gemini model ID; moving *-latest aliases are rejected",
    )
    run_parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "run one synthetic task; Gemini defaults to the first task "
            "to keep the initial pilot to 9 branches and at most 12 model "
            "backend calls (3 shared preludes plus 9 post-tool calls)"
        ),
    )
    run_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing trace and summary files",
    )
    return parser


def _run(args: argparse.Namespace) -> int:
    if (
        args.policy == "gemini"
        and args.tasks.resolve() != DEFAULT_TASKS_PATH.resolve()
        and not args.allow_custom_synthetic_tasks
    ):
        raise ValueError(
            "Custom Gemini task files require "
            "--allow-custom-synthetic-tasks to confirm synthetic-only data"
        )
    tasks = load_tasks(args.tasks)
    if args.task_id is not None:
        tasks = [task for task in tasks if task.task_id == args.task_id]
        if not tasks:
            raise ValueError(f"Unknown task_id: {args.task_id}")

    summary_path = args.summary or args.trace.with_suffix(".summary.json")
    require_external_artifact_path(args.trace, label="trace")
    require_external_artifact_path(summary_path, label="summary")

    policy_factory: Callable[[], AgentPolicy] | None = None
    if args.policy == "gemini":
        if args.task_id is None:
            tasks = tasks[:1]
        backend = GeminiBackend(model_id=args.model)
        policy_factory = lambda backend=backend: ModelBackedPolicy(backend)

    repetitions = args.repetitions
    if repetitions is None:
        repetitions = 3 if args.policy == "gemini" else 2
    experiment_id = args.experiment_id
    if experiment_id is None:
        experiment_id = (
            "gemini-real-llm-pilot"
            if args.policy == "gemini"
            else "instrumentation-pilot"
        )
    code_commit, code_dirty = _git_provenance()

    config = ExperimentConfig(
        experiment_id=experiment_id,
        repetitions=repetitions,
        seed=args.seed,
        policy_name=args.policy,
        max_steps=2 if args.policy == "gemini" else 1,
        transport=(
            "google_gemini_interactions_v1"
            if args.policy == "gemini"
            else "in_process_mock"
        ),
        code_commit=code_commit,
        code_dirty=code_dirty,
    )
    result = run_experiment(
        tasks,
        config,
        policy_factory=policy_factory,
        trace_path=args.trace,
        summary_path=summary_path,
        overwrite=args.overwrite,
    )
    external_effects = sum(
        bool(summary.external_side_effect) for summary in result.summaries
    )
    error_runs = sum(summary.status == "error" for summary in result.summaries)
    profile = result.policy_profile
    result_experiment = result.to_mapping()["experiment"]
    print(
        canonical_json(
            {
                "experiment_id": config.experiment_id,
                "policy": config.policy_name,
                "runtime_kind": profile.runtime_kind,
                "evidence_scope": profile.evidence_scope,
                "provider_id": profile.provider_id,
                "model_id": profile.model_id,
                "model_version": profile.model_version,
                "sdk_name": profile.sdk_name,
                "sdk_version": profile.sdk_version,
                "api_version": profile.api_version,
                "real_model_configured": profile.real_model_configured,
                "empirical_llm_completed_runs": (
                    result.empirical_llm_completed_runs
                ),
                "any_empirical_llm_observation": (
                    result.any_empirical_llm_observation
                ),
                "empirical_llm_evidence": result.empirical_llm_evidence,
                "complete_matched_sets": result.complete_matched_sets,
                "incomplete_matched_sets": result.incomplete_matched_sets,
                "complete_empirical_matched_sets": (
                    result.complete_empirical_matched_sets
                ),
                "shared_prelude_failures": result.shared_prelude_failures,
                "model_backend_accounting": dict(
                    result.model_backend_accounting
                ),
                "evidence_notice": (
                    result_experiment["evidence_notice"]
                ),
                "scheduled_runs": len(result.manifest),
                "completed_runs": len(result.manifest) - error_runs,
                "error_runs": error_runs,
                "aggregate_by_condition": result.aggregate_by_condition,
                "matched_comparisons": len(result.matched_comparisons),
                "external_side_effects": external_effects,
                "trace_path": str(args.trace.resolve()),
                "summary_path": str(summary_path.resolve()),
            }
        )
    )
    return 1 if error_runs else 0


def _git_provenance() -> tuple[str, bool]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return "unavailable", True
    return commit or "unavailable", bool(status.strip())


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return _run(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"I/O error: {exc}", file=sys.stderr)
        return 1
    parser.error(f"Unsupported command: {args.command}")
    return 2
