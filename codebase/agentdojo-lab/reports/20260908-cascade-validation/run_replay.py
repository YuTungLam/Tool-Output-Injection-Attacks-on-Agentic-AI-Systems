"""Frozen local replay operation; no API calls and no model-input intervention."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from agentdojo_lab.policy import load_policy
from agentdojo_lab.provenance_report import _read_run, export_provenance
from agentdojo_lab.semantic import LocalMiniLMEncoder, SemanticMatcher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/20260908-cascade-pilot-v1"
POLICY = load_policy(ROOT / "configs/workspace_policy_v1.yaml")
MODEL = ROOT / ".model-cache/all-MiniLM-L6-v2-1110a243"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


def instrumented():
    encoder = LocalMiniLMEncoder(MODEL, revision=REVISION)
    matcher = SemanticMatcher(encoder)
    calls, entries, current = Counter(), [], [None]
    encode = encoder.encode

    def counted(texts):
        entries.append({"stage": current[0], "text_count": len(texts)})
        return encode(texts)

    encoder.encode = counted
    for tier in ("tier3", "tier4"):
        original = getattr(matcher, "compare_" + tier)

        def staged(source, target, stage=tier, compare=original):
            current[0] = stage
            calls[stage] += 1
            try:
                return compare(source, target)
            finally:
                current[0] = None

        setattr(matcher, "compare_" + tier, staged)
    return matcher, calls, entries


matcher, calls, entries = instrumented()
result = export_provenance(
    batch=ROOT / "runs/20260907T025045Z-clean-pilot-b93eae95",
    output=OUT, semantic_matcher=matcher, policy=POLICY,
)
analysis = json.loads((OUT / "analysis.json").read_text())
repeat_matcher, repeat_calls, repeat_entries = instrumented()
repeat = [_read_run(Path(run["run_dir"]), repeat_matcher, POLICY) for run in analysis["runs"]]
first_calls = [run["calls"] for run in analysis["runs"]]
repeated_calls = [run["calls"] for run in repeat]
blank = OUT / "annotations/items.jsonl"
previous_blank = ROOT / "reports/20260908-semantic-pilot-v1/annotations/items.jsonl"
checks = {
    "repeat_calls_identical": first_calls == repeated_calls,
    "repeat_stage_invocations_identical": calls == repeat_calls,
    "repeat_encoder_entries_identical": entries == repeat_entries,
    "blank_annotation_package_unchanged": blank.read_bytes() == previous_blank.read_bytes(),
    "ten_recorded_runs": result["analyzed_runs"] == 10,
    "policy_coverage_no_unclassified_proposals": result["cascade"]["unclassified_proposals"] == 0,
    "policy_coverage_no_unclassified_sources": result["cascade"]["unclassified_source_occurrences"] == 0,
    "all_applicable_pairs_complete": result["cascade"]["incomplete_pair_count"] == 0,
}
record = {
    "passed": all(checks.values()), "checks": checks, "result": result,
    "stage_method_invocations": dict(calls),
    "encoder_entry_invocations": len(entries), "encoder_entries": entries,
    "encoder_measurement_scope": "TextEncoder.encode entry, before any cache; model forward calls not measured",
    "repeat_condition": "New LocalMiniLMEncoder and SemanticMatcher; identical frozen inputs and policy",
    "blank_annotation_sha256": hashlib.sha256(blank.read_bytes()).hexdigest(),
    "interpretation": "Routing and repeatability only; no attribution accuracy, safety, causal or latency-benefit claim",
}
with (Path(__file__).parent / "replay-verification.json").open("x") as stream:
    stream.write(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
raise SystemExit(0 if record["passed"] else 1)
