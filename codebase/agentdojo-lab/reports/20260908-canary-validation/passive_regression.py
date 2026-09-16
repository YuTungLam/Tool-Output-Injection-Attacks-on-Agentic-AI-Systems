"""Replay ten frozen passive runs locally and compare full calls and graphs exactly.

No agent or provider API is invoked. Network attempts fail and are counted. Only
the declared new report and validation result may be created; failures remain.
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

from preflight import (
    HERE,
    MODEL_PATH,
    POLICY_PATH,
    REVISION,
    ROOT,
    TARGETS,
    absent,
    canonical,
    file_sha256,
    local_files,
    protected_hashes,
    source_hashes,
    write_exclusive,
)

BATCH = ROOT / "runs/20260907T025045Z-clean-pilot-b93eae95"
BASELINE = ROOT / "reports/20260908-lineage-pilot-v1"
OUTPUT = ROOT / TARGETS["legacy_replay"]
RESULT = HERE / "passive-regression.json"
NAMESPACE = "workspace-recorded-lineage-v1"


def value_sha256(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def relative_tree_hashes(folder: Path) -> dict[str, str]:
    return {path.relative_to(folder).as_posix(): file_sha256(path) for path in local_files(folder)}


def require(condition: bool, name: str, checks: dict) -> None:
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def main() -> None:
    if Path(__file__).resolve().parent != HERE:
        raise ValueError("Execute the frozen script at its declared validation path")
    if not absent(OUTPUT) or not absent(RESULT):
        raise FileExistsError("The new report and verification result must be absent")
    frozen = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
    network_attempts = []

    def forbid_network(*_args, **_kwargs):
        network_attempts.append(True)
        raise RuntimeError("Network access is forbidden during passive replay")

    os.environ.update(
        HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1"
    )
    socket.socket.connect = forbid_network
    socket.socket.connect_ex = forbid_network
    socket.create_connection = forbid_network
    socket.getaddrinfo = forbid_network
    checks, timings, per_run = {}, {}, []
    verification = {
        "schema_version": 1,
        "status": "running",
        "passed": False,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "batch": str(BATCH),
        "baseline_report": str(BASELINE / "analysis.json"),
        "output_report": str(OUTPUT),
        "lineage_namespace": NAMESPACE,
        "model_path": str(MODEL_PATH),
        "model_revision": REVISION,
        "preflight_sha256": file_sha256(HERE / "preflight.json"),
        "checks": checks,
        "timing": timings,
        "per_run": per_run,
        "agent_executions_added": 0,
        "real_api_calls_added": 0,
        "export_provenance_invocations": 0,
        "notes": [
            "The full call and graph values are compared, including lineage fields; no fields are removed to obtain equality.",
            "Timestamps, report timing, report-location links and implementation fingerprints are not expected to equal the earlier report.",
            "Every run reconstructs an independent graph from recorded request prefixes; no cross-session continuity is inferred.",
            "Exact replay compatibility is an engineering check, not an accuracy, efficacy, maliciousness or causal result.",
        ],
    }
    protected_before = sources_before = None
    started = time.perf_counter()
    stage = "freeze_and_input_checks"
    try:
        sources_before = source_hashes()
        protected_before = protected_hashes(additional_excluded=(OUTPUT,))
        require(sources_before == frozen["source_sha256"], "all_frozen_source_files_and_set_match", checks)
        require(
            all(protected_before.get(path) == digest for path, digest in frozen["protected_sha256"].items()),
            "every_preflight_protected_file_matches",
            checks,
        )
        verification["protected_inputs_before"] = protected_before
        verification["source_inputs_before"] = sources_before
        old = json.loads((BASELINE / "analysis.json").read_text(encoding="utf-8"))
        require(old["mode"] == "offline_prefix_replay", "baseline_is_recorded_prefix_replay", checks)
        require(old["component_mode"] == "ordered_cascade", "baseline_uses_ordered_cascade", checks)
        require(old["lineage"]["namespace"] == NAMESPACE, "baseline_namespace_matches", checks)
        require(len(old["runs"]) == 10, "ten_frozen_runs", checks)
        require(
            all("lineage" in call for run in old["runs"] for call in run["calls"]),
            "baseline_contains_full_lineage_calls",
            checks,
        )
        require(
            all(not run["agent_config"].get("canary_enabled", False) for run in old["runs"]),
            "baseline_is_passive",
            checks,
        )

        stage = "local_model_initialization"
        from agentdojo_lab.cascade import CascadeMatcher
        from agentdojo_lab.policy import load_policy
        from agentdojo_lab.provenance_report import export_provenance
        from agentdojo_lab.semantic import LocalMiniLMEncoder, SemanticMatcher

        model_started = time.perf_counter()
        matcher = SemanticMatcher(LocalMiniLMEncoder(MODEL_PATH, revision=REVISION))
        timings["local_model_initialization_seconds"] = time.perf_counter() - model_started
        timings["local_model_initialization_scope"] = (
            "One local pin validation and encoder initialization; no live agent execution."
        )
        method_before = copy.deepcopy(matcher.metadata)
        policy = load_policy(POLICY_PATH)
        require(canonical(policy.metadata) == canonical(old["policy"]), "policy_matches_baseline", checks)
        require(
            canonical(CascadeMatcher(matcher).metadata)
            == canonical(old["methods"]["nt_style_ordered_cascade_v1"]),
            "cascade_method_matches_baseline",
            checks,
        )

        stage = "single_local_export"
        export_started = time.perf_counter()
        verification["export_provenance_invocations"] += 1
        verification["export_result"] = export_provenance(
            batch=BATCH,
            output=OUTPUT,
            semantic_matcher=matcher,
            policy=policy,
            lineage_namespace=NAMESPACE,
        )
        timings["export_including_report_write_seconds"] = time.perf_counter() - export_started
        report = json.loads((OUTPUT / "analysis.json").read_text(encoding="utf-8"))
        timings["export_internal_analysis_seconds"] = report["analysis_wall_seconds"]
        timings["export_internal_scope"] = report["analysis_timing_scope"]
        require(
            [run["run_id"] for run in report["runs"]] == [run["run_id"] for run in old["runs"]],
            "same_ten_runs_and_order",
            checks,
        )
        require(
            canonical(report["methods"]) == canonical(old["methods"]),
            "all_method_metadata_and_set_exact",
            checks,
        )
        require(canonical(report["policy"]) == canonical(old["policy"]), "exported_policy_exact", checks)
        require(
            canonical(report["lineage"]) == canonical(old["lineage"]), "lineage_configuration_exact", checks
        )
        require(report["counts"] == old["counts"], "all_aggregate_counts_exact", checks)
        require(report["real_llm_calls_added"] == 0, "export_adds_no_llm_calls", checks)

        stage = "full_call_and_graph_comparisons"
        for run, prior in zip(report["runs"], old["runs"], strict=True):
            item = {
                "run_id": run["run_id"],
                "calls_sha256": value_sha256(run["calls"]),
                "baseline_calls_sha256": value_sha256(prior["calls"]),
                "graph_sha256": value_sha256(run["lineage_graph"]),
                "baseline_graph_sha256": value_sha256(prior["lineage_graph"]),
            }
            per_run.append(item)
            require(
                canonical(run["calls"]) == canonical(prior["calls"]),
                f"{run['run_id']}:full_calls_exact",
                checks,
            )
            require(
                canonical(run["lineage_graph"]) == canonical(prior["lineage_graph"]),
                f"{run['run_id']}:full_graph_exact",
                checks,
            )
            require(
                run["source_hashes"] == prior["source_hashes"],
                f"{run['run_id']}:recorded_inputs_exact",
                checks,
            )
            require(run["lineage_graph"]["failed"] is False, f"{run['run_id']}:complete_graph", checks)
            require("input_condition" not in run, f"{run['run_id']}:passive_report_condition", checks)

        stage = "annotation_and_metadata_checks"
        require(
            relative_tree_hashes(OUTPUT / "annotations") == relative_tree_hashes(BASELINE / "annotations"),
            "blank_annotations_byte_identical",
            checks,
        )
        annotations = (OUTPUT / "annotations/items.jsonl").read_text(encoding="utf-8").splitlines()
        require(
            all(json.loads(line)["review"]["status"] == "unreviewed" for line in annotations if line),
            "annotations_remain_unreviewed",
            checks,
        )
        require(
            canonical(matcher.metadata) == canonical(method_before), "semantic_metadata_unchanged", checks
        )
        graphs = [run["lineage_graph"] for run in report["runs"]]
        edges = [edge for graph in graphs for edge in graph["edges"]]
        verification["report_counts"] = report["counts"]
        verification["graph_counts"] = {
            "nodes": sum(len(graph["nodes"]) for graph in graphs),
            "edges": len(edges),
            "candidate_content_edges": sum(edge["candidate"] is True for edge in edges),
            "structural_edges": sum(edge["candidate"] is False for edge in edges),
            "edge_relations": dict(Counter(edge["relation"] for edge in edges)),
            "confirmed_binding_commits": sum(
                event["status"] == "binding_committed" for graph in graphs for event in graph["memory_events"]
            ),
        }
        verification["status"] = "passed"
    except Exception as error:
        verification.update(status="failed", failure_stage=stage, error_type=type(error).__name__)
    finally:
        try:
            if protected_before is not None:
                after = protected_hashes(additional_excluded=(OUTPUT,))
                verification["protected_inputs_after"] = after
                checks["all_preexisting_runs_reports_files_and_sets_unchanged"] = after == protected_before
            if sources_before is not None:
                after = source_hashes()
                verification["source_inputs_after"] = after
                checks["all_source_files_and_sets_unchanged"] = after == sources_before
        except Exception as error:
            verification.update(status="failed", final_integrity_error_type=type(error).__name__)
        checks["no_network_attempts"] = len(network_attempts) == 0
        checks["exactly_one_export_invocation"] = verification["export_provenance_invocations"] == 1
        verification["network_connection_attempts"] = len(network_attempts)
        timings["whole_validation_seconds"] = time.perf_counter() - started
        timings["whole_validation_scope"] = (
            "Protected-input hashing, local model initialization, one report export, exact comparisons and final integrity checks; excludes live agent execution."
        )
        verification["finished_at"] = datetime.now(timezone.utc).isoformat()
        verification["passed"] = verification["status"] == "passed" and all(checks.values())
        if not verification["passed"]:
            verification["status"] = "failed"
        write_exclusive(RESULT, verification)
    print(
        json.dumps(
            {"passed": verification["passed"], "verification": str(RESULT), "report": str(OUTPUT)}, indent=2
        )
    )
    if not verification["passed"]:
        raise SystemExit("Passive regression failed; retained evidence is in passive-regression.json")


if __name__ == "__main__":
    main()
