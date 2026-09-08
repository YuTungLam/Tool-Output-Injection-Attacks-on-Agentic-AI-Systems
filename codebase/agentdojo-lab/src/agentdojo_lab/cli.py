"""Small entry point for installing and running the clean AgentDojo baseline."""

import argparse
import json
import sys
from pathlib import Path

from agentdojo.task_suite.load_suites import get_suites

from agentdojo_lab.inspection import inspect_events
from agentdojo_lab.runner import ROOT, RunConfig, RunExecutionError, doctor, load_config, run_clean


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check installation and credentials without network requests")
    tasks = commands.add_parser("tasks", help="List native clean user tasks")
    tasks.add_argument("--suite", default="workspace")
    tasks.add_argument("--benchmark-version", default="v1.2.2")
    smoke = commands.add_parser("smoke", help="Verify the native pipeline with a fixed offline fixture")
    smoke.add_argument("--offline", action="store_true", required=True)
    smoke.add_argument("--output", type=Path)
    smoke.add_argument("--no-record", action="store_true", help="Disable event recording for a control run")
    inspect = commands.add_parser("inspect", help="Check event links and completeness without model calls")
    inspect.add_argument("--events", type=Path, required=True)
    report = commands.add_parser("report", help="Export paper-style tables and a trace from saved clean runs")
    report.add_argument("--runs", type=Path, default=ROOT / "runs")
    report.add_argument("--output", type=Path, help="New directory for CSV, LaTeX, PNG, SVG and PDF exports")
    html = commands.add_parser("html", help="Rebuild a self-contained interactive HTML record from one run")
    html.add_argument("--run", type=Path, required=True)
    html.add_argument("--output", type=Path, help="HTML path; defaults to RUN/report.html")
    pilot = commands.add_parser("pilot", help="Run a frozen clean pilot, one task per independent run")
    pilot.add_argument("--config", type=Path)
    pilot.add_argument("--output", type=Path)
    pilot.add_argument("--resume", type=Path, help="Continue only never-started trials in this frozen batch")
    pilot.add_argument("--through-repeat", type=int, default=1, choices=(1, 2, 3))
    pilot.add_argument(
        "--plan-only", action="store_true", help="Freeze the plan and export its index without model calls"
    )
    pilot_report = commands.add_parser(
        "pilot-report", help="Rebuild a pilot index and CSV files without model calls"
    )
    pilot_report.add_argument("--batch", type=Path, required=True)
    provenance = commands.add_parser(
        "provenance", help="Replay recorded prefixes into source candidates and blank review items"
    )
    inputs = provenance.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--run", type=Path, action="append", help="Source run; repeat for multiple runs")
    inputs.add_argument("--batch", type=Path, help="Frozen batch; analyzes recorded trials only")
    provenance.add_argument(
        "--output", type=Path, required=True, help="New analysis directory outside source runs"
    )
    provenance.add_argument(
        "--semantic-model", type=Path, help="Enable Tier 3/4 using a local pinned MiniLM snapshot"
    )
    provenance.add_argument(
        "--semantic-revision", help="Full model commit SHA; required with --semantic-model"
    )
    provenance.add_argument("--policy", type=Path, help="Select ordered cascade with a frozen tool policy")
    provenance.add_argument("--lineage-namespace", help="Build a DCPG independently for each recorded run")
    live = commands.add_parser("run", help="Run selected clean tasks against Groq")
    live.add_argument("--config", type=Path, default=ROOT / "configs" / "groq.toml")
    live.add_argument("--model", help="Override the Groq model ID")
    live.add_argument("--task", action="append", help="Replace configured tasks; repeat to select more")
    live.add_argument("--no-record", action="store_true", help="Disable event recording for a control run")
    live.add_argument("--pacing-state", type=Path, help="Shared quota state for one sequential paced batch")
    live.add_argument(
        "--output", type=Path, help="New output directory; existing paths are never overwritten"
    )
    for command in (smoke, live):
        command.add_argument(
            "--lineage-namespace", help="Observe DCPG in one native task and save a state sidecar"
        )
        command.add_argument("--policy", type=Path, help="Frozen tool policy for ordered online cascade")
        command.add_argument(
            "--online-provenance",
            action="store_true",
            help="Persist source candidates before tool runtime entry",
        )
        command.add_argument(
            "--semantic-model", type=Path, help="Local pinned MiniLM snapshot for online Tier 3/4"
        )
        command.add_argument("--semantic-revision", help="Full model commit SHA; use with --semantic-model")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor()
        elif args.command == "inspect":
            result = inspect_events(args.events)
        elif args.command == "report":
            from agentdojo_lab.reporting import export_report

            result = export_report(args.runs, args.output)
        elif args.command == "html":
            from agentdojo_lab.html_report import export_run_html

            result = export_run_html(args.run, output=args.output)
        elif args.command == "pilot":
            from agentdojo_lab.pilot import run_pilot

            result = run_pilot(
                config_path=args.config,
                output=args.output,
                resume=args.resume,
                through_repeat=args.through_repeat,
                plan_only=args.plan_only,
            )
        elif args.command == "pilot-report":
            from agentdojo_lab.pilot_report import export_pilot_report

            report_data = export_pilot_report(args.batch)
            result = {"batch_dir": str(args.batch.resolve()), **report_data["totals"]}
        elif args.command == "provenance":
            from agentdojo_lab.provenance_report import export_provenance

            if bool(args.semantic_model) != bool(args.semantic_revision):
                raise ValueError("Use --semantic-model and --semantic-revision together")
            matcher = None
            if args.semantic_model:
                from agentdojo_lab.semantic import LocalMiniLMEncoder, SemanticMatcher

                matcher = SemanticMatcher(
                    LocalMiniLMEncoder(args.semantic_model, revision=args.semantic_revision)
                )
            policy = None
            if args.policy:
                from agentdojo_lab.policy import load_policy

                policy = load_policy(args.policy)
            result = export_provenance(
                run_dirs=args.run,
                batch=args.batch,
                output=args.output,
                semantic_matcher=matcher,
                policy=policy,
                **(
                    {"lineage_namespace": args.lineage_namespace}
                    if args.lineage_namespace is not None
                    else {}
                ),
            )
        elif args.command == "tasks":
            suites = get_suites(args.benchmark_version)
            if args.suite not in suites:
                raise ValueError(f"Unknown suite/version: {args.suite}/{args.benchmark_version}")
            result = {
                "suite": args.suite,
                "benchmark_version": args.benchmark_version,
                "tasks": [{"id": t.ID, "prompt": t.PROMPT} for t in suites[args.suite].user_tasks.values()],
            }
        elif args.command == "smoke":
            result = run_clean(
                RunConfig(
                    record_events=not args.no_record,
                    online_provenance=args.online_provenance,
                    provenance_policy=str(args.policy) if args.policy else None,
                    lineage_namespace=args.lineage_namespace,
                    semantic_model=str(args.semantic_model) if args.semantic_model else None,
                    semantic_revision=args.semantic_revision,
                ),
                offline=True,
                output=args.output,
            )
        else:
            config = load_config(args.config)
            data = config.model_dump()
            if args.lineage_namespace is not None:
                data["lineage_namespace"] = args.lineage_namespace
            if args.model:
                data["model"] = args.model
                if not args.model.startswith("openai/gpt-oss"):
                    data["reasoning_effort"] = None
            if args.task:
                data["user_tasks"] = args.task
            if args.no_record:
                data["record_events"] = False
            if args.online_provenance:
                data["online_provenance"] = True
            if args.policy is not None:
                data["provenance_policy"] = str(args.policy)
            if args.semantic_model is not None:
                data["semantic_model"] = str(args.semantic_model)
            if args.semantic_revision is not None:
                data["semantic_revision"] = args.semantic_revision
            result = run_clean(
                RunConfig.model_validate(data), output=args.output, pacing_state=args.pacing_state
            )
        if args.command in {"run", "smoke"} and result.get("run_dir"):
            report_status = Path(result["run_dir"]) / "html-report-status.json"
            try:
                if report_status.is_file():
                    status_data = json.loads(report_status.read_text())
                    if not isinstance(status_data, dict):
                        raise ValueError("Invalid report status")
                else:
                    status_data = {"status": "unavailable"}
            except (OSError, ValueError) as exc:
                status_data = {"status": "unavailable", "error_type": type(exc).__name__}
            result = {**result, "html_report": status_data}
    except Exception as exc:
        # Don't echo SDK request bodies or credentials to the terminal.
        if isinstance(exc, (ValueError, FileNotFoundError, FileExistsError, RunExecutionError)):
            print(f"Error: {exc}", file=sys.stderr)
        else:
            print(
                f"Run failed ({type(exc).__name__}). Inspect the latest runs/*/summary.json.", file=sys.stderr
            )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "doctor" and not result["offline_ready"]:
        return 2
    if args.command == "inspect" and not result["valid"]:
        return 2
    if args.command == "pilot" and not args.plan_only:
        if result["unscorable_trials"] or result["complete_recordings"] != result["started_trials"]:
            return 2
        if result["failed_trials"]:
            return 1
    if args.command in {"run", "smoke"} and result.get("recording", {}).get("complete") is False:
        return 2
    if args.command in {"run", "smoke"} and result.get("online_provenance", {}).get("complete") is False:
        return 2
    if args.command in {"run", "smoke"} and result.get("status") == "completed_with_issues":
        return 2
    if args.command in {"run", "smoke"} and result["task_success_count"] != result["task_count"]:
        return 1
    return 0
