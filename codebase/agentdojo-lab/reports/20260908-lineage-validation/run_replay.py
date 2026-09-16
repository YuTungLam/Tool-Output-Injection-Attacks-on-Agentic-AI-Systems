"""Frozen local replay validation; execute only after runtime/protocol freeze.

This script adds one new report and one verification JSON. Existing recordings,
reports, and annotations are read-only. It never executes an agent or model API.
The local MiniLM encoder is the only model evaluated. Network connections are
blocked in this process, including accidental fallback attempts.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import socket
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "runs/20260907T025045Z-clean-pilot-b93eae95"
BASELINE = ROOT / "reports/20260908-cascade-pilot-v1"
OUTPUT = ROOT / "reports/20260908-lineage-pilot-v1"
VALIDATION = ROOT / "reports/20260908-lineage-validation"
RESULT = VALIDATION / "replay-verification.json"
MODEL_PATH = ROOT / ".model-cache/all-MiniLM-L6-v2-1110a243"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
POLICY_PATH = ROOT / "configs/workspace_policy_v1.yaml"
NAMESPACE = "workspace-recorded-lineage-v1"
ORDINARY_METHOD = "nt_style_ordered_cascade_v1"
NETWORK_ATTEMPTS = 0


def canonical(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def value_sha256(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hashes(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("An existing local directory is required for protected inputs")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Protected input trees must not contain symlinks")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = file_sha256(path)
    return result


def runtime_hashes() -> dict:
    paths = [
        *sorted((ROOT / "src/agentdojo_lab").glob("*.py")),
        ROOT / "src/agentdojo_lab/model_pins/minilm-v1.json",
        ROOT / "uv.lock",
        POLICY_PATH,
        Path(__file__).resolve(),
    ]
    return {path.relative_to(ROOT).as_posix(): file_sha256(path) for path in paths}


def forbid_network(*_args, **_kwargs):
    global NETWORK_ATTEMPTS
    NETWORK_ATTEMPTS += 1
    raise RuntimeError("Network access is forbidden during this frozen local replay")


def require(condition: bool, name: str, checks: dict) -> None:
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def direct_calls(calls: list[dict]) -> list[dict]:
    result = copy.deepcopy(calls)
    for call in result:
        if "lineage" not in call:
            raise ValueError("Expected the added call.lineage field")
        del call["lineage"]
    return result


def graph_counts(runs: list[dict]) -> dict:
    nodes, edges, registry, bindings, memory_events = [], [], [], [], []
    call_statuses, pair_statuses, first_tiers = Counter(), Counter(), Counter()
    path_lengths, restored_path_lengths = Counter(), Counter()
    recovered_occurrences = recovered_calls = comparison_count = matched_count = incomplete_count = 0
    for run in runs:
        graph = run["lineage_graph"]
        nodes.extend(graph["nodes"])
        edges.extend(graph["edges"])
        registry.extend(graph["registry"])
        bindings.extend(graph["memory_bindings"])
        memory_events.extend(graph["memory_events"])
        edge_map = {edge["edge_id"]: edge for edge in graph["edges"]}
        for call in run["calls"]:
            evidence = call["lineage"]
            call_statuses[evidence["summary"]["status"]] += 1
            recovered_occurrences += len(evidence["recovered_sources"])
            recovered_calls += bool(evidence["recovered_sources"])
            comparison_count += len(evidence["comparisons"])
            for comparison in evidence["comparisons"]:
                pair_statuses[comparison["status"]] += 1
                matched_count += comparison["matched"] is True
                incomplete_count += not comparison["complete"] and comparison["status"] != "not_applicable"
                if comparison["first_matched_tier"] is not None:
                    first_tiers[comparison["first_matched_tier"]] += 1
            for path in evidence["paths"]:
                length = len(path["edge_ids"])
                path_lengths[str(length)] += 1
                if any(edge_map[edge]["relation"] == "memory_restore" for edge in path["edge_ids"]):
                    restored_path_lengths[str(length)] += 1
    return {
        "graph_count": len(runs),
        "node_count": len(nodes),
        "node_kinds": dict(Counter(node["kind"] for node in nodes)),
        "edge_count": len(edges),
        "edge_relations": dict(Counter(edge["relation"] for edge in edges)),
        "candidate_content_edges": sum(edge["candidate"] is True for edge in edges),
        "structural_edges": sum(edge["candidate"] is False for edge in edges),
        "registry_labels": len(registry),
        "binding_count": len(bindings),
        "active_bindings_at_run_end": sum(binding["active"] is True for binding in bindings),
        "inactive_bindings_at_run_end": sum(binding["active"] is False for binding in bindings),
        "memory_event_statuses": dict(Counter(event["status"] for event in memory_events)),
        "confirmed_binding_commits": sum(event["status"] == "binding_committed" for event in memory_events),
        "call_lineage_statuses": dict(call_statuses),
        "calls_with_recovered_lineage": recovered_calls,
        "recovered_source_occurrences": recovered_occurrences,
        "recovered_comparison_count": comparison_count,
        "recovered_comparison_statuses": dict(pair_statuses),
        "matched_recovered_comparisons": matched_count,
        "incomplete_recovered_comparisons": incomplete_count,
        "recovered_first_matched_tiers": dict(first_tiers),
        "all_candidate_path_length_histogram": dict(path_lengths),
        "memory_restored_path_length_histogram": dict(restored_path_lengths),
        "path_count_scope": "paths retained per proposal; repeated observations are counted separately",
        "binding_count_scope": "latest binding per record in each independent run graph",
        "accuracy": None,
        "maliciousness_verdicts": 0,
        "causal_verdicts": 0,
    }


def main() -> None:
    if OUTPUT.exists() or RESULT.exists():
        raise FileExistsError("Frozen replay output/result must not already exist; no overwrites are allowed")
    if Path(__file__).resolve().parent != VALIDATION:
        raise ValueError("Execute the frozen script from its declared validation directory")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    socket.socket.connect = forbid_network
    socket.socket.connect_ex = forbid_network
    socket.create_connection = forbid_network

    checks, timing, per_run = {}, {}, []
    verification = {
        "schema_version": 1,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "batch": str(BATCH),
        "baseline_report": str(BASELINE),
        "output_report": str(OUTPUT),
        "lineage_namespace": NAMESPACE,
        "model_path": str(MODEL_PATH),
        "model_revision": REVISION,
        "checks": checks,
        "timing": timing,
        "per_run": per_run,
        "real_api_calls_added": 0,
        "agent_executions_added": 0,
        "export_provenance_invocations": 0,
        "notes": [
            "All matching uses recorded request prefixes and the local pinned MiniLM model.",
            "The first export and subsequent replay use the same encoder instance; cache warmth affects timing.",
            "Graph serialization and replay equality do not establish provenance accuracy or maliciousness.",
            "Each recorded run starts an independent graph; this batch does not establish cross-session storage continuity.",
            "No accuracy estimate, causal probe, canary insertion, action interception, or parameter update is performed.",
        ],
    }
    started = time.perf_counter()
    protected_before = runtime_before = None
    stage = "input_fingerprints"
    try:
        protected_before = {"batch": tree_hashes(BATCH), "baseline": tree_hashes(BASELINE)}
        runtime_before = runtime_hashes()
        verification["protected_inputs_before"] = protected_before
        verification["runtime_inputs_before"] = runtime_before
        old = json.loads((BASELINE / "analysis.json").read_text())
        require(old["component_mode"] == "ordered_cascade", "baseline_is_ordered_cascade", checks)
        require(old["mode"] == "offline_prefix_replay", "baseline_is_offline_replay", checks)
        require(
            all("lineage" not in call for run in old["runs"] for call in run["calls"]),
            "baseline_calls_have_no_lineage_field",
            checks,
        )

        stage = "local_model_initialization"
        from agentdojo_lab.cascade import CascadeMatcher
        from agentdojo_lab.policy import load_policy
        from agentdojo_lab.provenance_report import _read_run, export_provenance
        from agentdojo_lab.semantic import LocalMiniLMEncoder, SemanticMatcher

        model_started = time.perf_counter()
        matcher = SemanticMatcher(LocalMiniLMEncoder(MODEL_PATH, revision=REVISION))
        timing["model_initialization_seconds"] = time.perf_counter() - model_started
        frozen_method = copy.deepcopy(matcher.metadata)
        loaded_policy = load_policy(POLICY_PATH)
        require(
            canonical(CascadeMatcher(matcher).metadata) == canonical(old["methods"][ORDINARY_METHOD]),
            "ordinary_cascade_metadata_matches_baseline_before_export",
            checks,
        )
        require(
            canonical(loaded_policy.metadata) == canonical(old["policy"]), "policy_matches_baseline", checks
        )

        stage = "single_export"
        export_started = time.perf_counter()
        verification["export_provenance_invocations"] += 1
        verification["export_result"] = export_provenance(
            batch=BATCH,
            output=OUTPUT,
            semantic_matcher=matcher,
            policy=loaded_policy,
            lineage_namespace=NAMESPACE,
        )
        timing["export_including_report_write_seconds"] = time.perf_counter() - export_started
        report = json.loads((OUTPUT / "analysis.json").read_text())
        timing["export_internal_analysis_seconds"] = report["analysis_wall_seconds"]
        timing["export_internal_scope"] = report["analysis_timing_scope"]
        old_runs = {run["run_id"]: run for run in old["runs"]}
        require(
            [run["run_id"] for run in report["runs"]] == [run["run_id"] for run in old["runs"]],
            "same_selected_runs_and_order",
            checks,
        )
        require(
            all(
                canonical(report["methods"][key]) == canonical(value) for key, value in old["methods"].items()
            ),
            "all_existing_method_metadata_unchanged",
            checks,
        )
        require(canonical(report["policy"]) == canonical(old["policy"]), "exported_policy_unchanged", checks)
        require(report["real_llm_calls_added"] == 0, "export_added_no_llm_calls", checks)

        stage = "independent_repeat_replay"
        repeated_started = time.perf_counter()
        for run in report["runs"]:
            run_started = time.perf_counter()
            repeated = _read_run(
                Path(run["run_dir"]),
                semantic_matcher=matcher,
                policy=loaded_policy,
                lineage_namespace=NAMESPACE,
            )
            item = {
                "run_id": run["run_id"],
                "calls_sha256": value_sha256(run["calls"]),
                "repeated_calls_sha256": value_sha256(repeated["calls"]),
                "graph_sha256": value_sha256(run["lineage_graph"]),
                "repeated_graph_sha256": value_sha256(repeated["lineage_graph"]),
                "direct_calls_sha256": value_sha256(direct_calls(run["calls"])),
                "baseline_calls_sha256": value_sha256(old_runs[run["run_id"]]["calls"]),
                "repeat_seconds": time.perf_counter() - run_started,
            }
            per_run.append(item)
            require(
                item["calls_sha256"] == item["repeated_calls_sha256"],
                f"{run['run_id']}:full_calls_repeat_exactly",
                checks,
            )
            require(
                item["graph_sha256"] == item["repeated_graph_sha256"],
                f"{run['run_id']}:full_graph_repeats_exactly",
                checks,
            )
            require(
                item["direct_calls_sha256"] == item["baseline_calls_sha256"],
                f"{run['run_id']}:only_call_lineage_was_added",
                checks,
            )
            require(
                run["source_hashes"] == repeated["source_hashes"] == old_runs[run["run_id"]]["source_hashes"],
                f"{run['run_id']}:source_file_hashes_match_baseline",
                checks,
            )
            graph = run["lineage_graph"]
            require(graph["failed"] is False, f"{run['run_id']}:graph_complete", checks)
            require(
                graph["parent_checkpoint_sha256"] is None,
                f"{run['run_id']}:fresh_graph_without_import",
                checks,
            )
            require(
                all(node["run_id"] == run["run_id"] for node in graph["nodes"]),
                f"{run['run_id']}:no_other_run_nodes",
                checks,
            )
        timing["repeat_analysis_seconds"] = time.perf_counter() - repeated_started
        timing["repeat_scope"] = (
            "Second local reads, audit, complete prefix replay and DCPG construction; warm shared encoder; no model construction or report writing"
        )

        stage = "annotation_and_metadata_checks"
        require(
            tree_hashes(OUTPUT / "annotations") == tree_hashes(BASELINE / "annotations"),
            "blank_annotation_files_byte_identical",
            checks,
        )
        annotations = (OUTPUT / "annotations/items.jsonl").read_text().splitlines()
        require(
            all(json.loads(line)["review"]["status"] == "unreviewed" for line in annotations if line),
            "annotations_remain_unreviewed",
            checks,
        )
        require(
            canonical(matcher.metadata) == canonical(frozen_method),
            "ordinary_encoder_metadata_not_mutated_by_memory_profile",
            checks,
        )
        verification["counts"] = graph_counts(report["runs"])
        verification["report_counts"] = report["counts"]
        verification["status"] = "passed"
    except Exception as error:
        verification.update(status="failed", failure_stage=stage, error_type=type(error).__name__)
    finally:
        try:
            if protected_before is not None:
                after = {"batch": tree_hashes(BATCH), "baseline": tree_hashes(BASELINE)}
                verification["protected_inputs_after"] = after
                checks["all_old_files_and_file_sets_unchanged"] = after == protected_before
            if runtime_before is not None:
                after = runtime_hashes()
                verification["runtime_inputs_after"] = after
                checks["runtime_policy_pin_lock_and_script_unchanged"] = after == runtime_before
        except Exception as error:
            verification.update(status="failed", final_integrity_error_type=type(error).__name__)
        checks["no_network_connections_attempted"] = NETWORK_ATTEMPTS == 0
        checks["exactly_one_export_invocation"] = verification["export_provenance_invocations"] == 1
        verification["network_connection_attempts"] = NETWORK_ATTEMPTS
        timing["whole_validation_seconds"] = time.perf_counter() - started
        timing["whole_validation_scope"] = (
            "Input hashing, local model construction, one report export, one repeat per run, comparison and final integrity checks; no live agent timing"
        )
        verification["finished_at"] = datetime.now(timezone.utc).isoformat()
        if not all(checks.values()):
            verification["status"] = "failed"
        with RESULT.open("x", encoding="utf-8") as stream:
            json.dump(verification, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
    if verification["status"] != "passed":
        raise SystemExit("Frozen replay validation failed; inspect replay-verification.json")
    print(
        json.dumps(
            {
                "status": "passed",
                "verification": str(RESULT),
                "output": str(OUTPUT),
                "counts": verification["counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
