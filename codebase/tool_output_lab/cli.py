"""Command-line entry point for the instrumentation pilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .experiment import ExperimentConfig, run_experiment
from .tasks import load_tasks
from .utils import canonical_json

CODEBASE_ROOT = Path(__file__).resolve().parents[1]


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
        default=CODEBASE_ROOT / "configs" / "tasks.json",
        help="path to the synthetic task JSON file",
    )
    run_parser.add_argument(
        "--trace",
        type=Path,
        default=CODEBASE_ROOT / "results" / "sample_traces" / "pilot.jsonl",
        help="output JSONL trace path",
    )
    run_parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="output summary JSON path (defaults next to the trace)",
    )
    run_parser.add_argument("--experiment-id", default="instrumentation-pilot")
    run_parser.add_argument("--repetitions", type=int, default=2)
    run_parser.add_argument("--seed", type=int, default=20260723)
    run_parser.add_argument(
        "--policy", choices=("vulnerable", "safe"), default="vulnerable"
    )
    run_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing trace and summary files",
    )
    return parser


def _run(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    summary_path = args.summary or args.trace.with_suffix(".summary.json")
    config = ExperimentConfig(
        experiment_id=args.experiment_id,
        repetitions=args.repetitions,
        seed=args.seed,
        policy_name=args.policy,
    )
    result = run_experiment(
        tasks,
        config,
        trace_path=args.trace,
        summary_path=summary_path,
        overwrite=args.overwrite,
    )
    external_effects = sum(
        bool(summary.external_side_effect) for summary in result.summaries
    )
    print(
        canonical_json(
            {
                "experiment_id": config.experiment_id,
                "policy": config.policy_name,
                "runtime_kind": config.runtime_kind,
                "evidence_scope": config.evidence_scope,
                "empirical_llm_evidence": False,
                "evidence_notice": (
                    "Scripted control results validate instrumentation only."
                ),
                "scheduled_runs": len(result.manifest),
                "aggregate_by_condition": result.aggregate_by_condition,
                "matched_comparisons": len(result.matched_comparisons),
                "external_side_effects": external_effects,
                "trace_path": str(args.trace.resolve()),
                "summary_path": str(summary_path.resolve()),
            }
        )
    )
    return 0


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
