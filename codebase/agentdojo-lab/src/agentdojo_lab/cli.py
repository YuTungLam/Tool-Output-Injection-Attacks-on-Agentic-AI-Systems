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
    live = commands.add_parser("run", help="Run selected clean tasks against Groq")
    live.add_argument("--config", type=Path, default=ROOT / "configs" / "groq.toml")
    live.add_argument("--model", help="Override the Groq model ID")
    live.add_argument("--task", action="append", help="Replace configured tasks; repeat to select more")
    live.add_argument("--no-record", action="store_true", help="Disable event recording for a control run")
    live.add_argument(
        "--output", type=Path, help="New output directory; existing paths are never overwritten"
    )
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
            result = run_clean(RunConfig(record_events=not args.no_record), offline=True, output=args.output)
        else:
            config = load_config(args.config)
            data = config.model_dump()
            if args.model:
                data["model"] = args.model
                if not args.model.startswith("openai/gpt-oss"):
                    data["reasoning_effort"] = None
            if args.task:
                data["user_tasks"] = args.task
            if args.no_record:
                data["record_events"] = False
            result = run_clean(RunConfig.model_validate(data), output=args.output)
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
    if args.command in {"run", "smoke"} and result.get("recording", {}).get("complete") is False:
        return 2
    if args.command in {"run", "smoke"} and result.get("status") == "completed_with_issues":
        return 2
    if args.command in {"run", "smoke"} and result["task_success_count"] != result["task_count"]:
        return 1
    return 0
