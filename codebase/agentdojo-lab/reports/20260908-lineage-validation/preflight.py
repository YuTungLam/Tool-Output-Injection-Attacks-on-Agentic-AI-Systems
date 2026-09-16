"""Prospective gate 5 freeze; local checks only, no model endpoint request."""
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from agentdojo.task_suite.load_suites import get_suite
from agentdojo_lab.policy import load_policy
from agentdojo_lab.runner import doctor, load_config
from agentdojo_lab.semantic import LocalMiniLMEncoder, SemanticMatcher

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
TARGETS = {
    "native": "runs/20260908-lineage-memory-control",
    "replay": "reports/20260908-lineage-pilot-v1",
    "live": "runs/20260908-lineage-groq-task32",
    "live_replay": "reports/20260908-lineage-task32-prefix-replay",
    "memory_replay": "reports/20260908-lineage-memory-prefix-replay",
}
assert not (HERE / "preflight.json").exists()
assert all(not (ROOT / target).exists() for target in TARGETS.values())
paths = [p for p in (ROOT / "src/agentdojo_lab").rglob("*") if p.suffix in {".py", ".html", ".json"}]
paths += list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
paths += [ROOT / name for name in ("LINEAGE.md", "configs/groq_lineage.toml", "configs/workspace_policy_v1.yaml", "pyproject.toml", "uv.lock", "upstream.json")]
paths += [HERE / "preflight.py", HERE / "run_replay.py"]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

protected = [ROOT / "runs/20260907T025045Z-clean-pilot-b93eae95", ROOT / "runs/20260908-cascade-groq-task20", ROOT / "reports/20260908-cascade-pilot-v1", ROOT / "reports/20260908-cascade-validation"]
status = doctor()
assert status["live_prerequisites_ready"] and not status["upstream"]["modified"]
config = load_config(ROOT / "configs/groq_lineage.toml")
policy = load_policy(ROOT / config.provenance_policy)
start = time.perf_counter_ns()
matcher = SemanticMatcher(LocalMiniLMEncoder(ROOT / config.semantic_model, revision=config.semantic_revision))
loading_ns = time.perf_counter_ns() - start
record = {
    "schema_version": 1,
    "frozen_at": datetime.now(timezone.utc).isoformat(),
    "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
    "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)},
    "protected_sha256": {str(p.relative_to(ROOT)): digest(p) for folder in protected for p in sorted(folder.rglob("*")) if p.is_file()},
    "doctor": status,
    "config": config.model_dump(mode="json"),
    "policy": policy.metadata,
    "semantic": matcher.metadata,
    "local_model_loading_ns": loading_ns,
    "local_model_loading_scope": "One local pin verification and encoder initialization; before agent execution; no endpoint call",
    "outputs": TARGETS,
    "single_live_trial_selected_before_execution": True,
    "live_trial_count": 1,
    "native_task_prompt": get_suite(config.benchmark_version, config.suite).user_tasks["user_task_32"].PROMPT,
    "selection_basis": "Native search/create/share task requirements, not a desired lineage result; seen previously in development, not held-out efficacy",
    "failure_policy": "Retain the selected trial, all native retry episodes and failures; no unreported replacement",
    "commands": [
        ".venv/bin/python scripts/validate_lineage_memory.py --output runs/20260908-lineage-memory-control",
        ".venv/bin/python reports/20260908-lineage-validation/run_replay.py",
        ".venv/bin/dojo-lab run --config configs/groq_lineage.toml --output runs/20260908-lineage-groq-task32",
        ".venv/bin/python scripts/verify_online_run.py --run runs/20260908-lineage-groq-task32 --output reports/20260908-lineage-validation/live-verification.json",
    ],
    "scope": "Gate 5 candidate lineage and actual native memory persistence; no canary, causal probes, efficacy labels, CTTA, model updates, enforcement or real-account tool operations",
    "tests_before_execution": {"report": "pytest-before.stdout.log", "ruff_passed": True},
}
with (HERE / "preflight.json").open("x") as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"frozen": True, "source_files": len(record["source_sha256"]), "protected_files": len(record["protected_sha256"]), "single_live_trial": config.user_tasks, "outputs": TARGETS}, indent=2))
