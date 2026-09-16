"""Static artifact, package and frozen-input verification; no browser or model calls."""
import hashlib
import json
import subprocess
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Parser(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.scripts, self.current, self.ids = [], None, []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "script":
            self.current = {"attrs": attrs, "text": ""}
            self.scripts.append(self.current)

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.current = None

preflight = json.loads((HERE / "preflight.json").read_text())
protected_roots = ["runs/20260907T025045Z-clean-pilot-b93eae95", "runs/20260908-cascade-groq-task20", "reports/20260908-cascade-pilot-v1", "reports/20260908-cascade-validation"]
protected = {str(p.relative_to(ROOT)): digest(p) for name in protected_roots for p in (ROOT / name).rglob("*") if p.is_file()}
checks = {
    "frozen_runtime_protocol_tests_scripts_unchanged": all(digest(ROOT / name) == value for name, value in preflight["source_sha256"].items()),
    "protected_old_file_sets_and_hashes_unchanged": protected == preflight["protected_sha256"],
}
reports = []
for name in preflight["outputs"].values():
    for path in sorted((ROOT / name).rglob("*.html")):
        parsed = Parser(path.read_text())
        item = {"path": str(path.relative_to(ROOT)), "sha256": digest(path), "unique_ids": len(parsed.ids) == len(set(parsed.ids)), "scripts_valid": True, "external_scripts": False}
        for script in parsed.scripts:
            if script["attrs"].get("src"):
                item["external_scripts"] = True
            elif script["attrs"].get("type") == "application/json":
                data = json.loads(script["text"])
                if script["attrs"].get("id") == "record" and "lineage_state" in data:
                    item["embedded_checkpoint_equals_saved"] = data["lineage_state"] == json.loads((path.parent / "lineage-state.json").read_text())
                    item["checkpoint_source_hash_matches"] = data["source_hashes"]["lineage-state.json"] == digest(path.parent / "lineage-state.json")
            else:
                result = subprocess.run(["/opt/homebrew/bin/node", "--check"], input=script["text"], text=True, capture_output=True)
                item["scripts_valid"] &= result.returncode == 0
                if result.returncode:
                    item["script_error"] = result.stderr
        item["passed"] = item["unique_ids"] and item["scripts_valid"] and not item["external_scripts"] and item.get("embedded_checkpoint_equals_saved", True) and item.get("checkpoint_source_hash_matches", True)
        reports.append(item)
checks["all_new_html_static_checks_pass"] = bool(reports) and all(r["passed"] for r in reports)
wheel = next((ROOT / "dist").glob("agentdojo_lab-*.whl"))
with zipfile.ZipFile(wheel) as package:
    checks["wheel_lineage_module_matches_frozen_source"] = package.read("agentdojo_lab/lineage.py") == (ROOT / "src/agentdojo_lab/lineage.py").read_bytes()
    checks["wheel_template_matches_frozen_source"] = package.read("agentdojo_lab/templates/run_report.html") == (ROOT / "src/agentdojo_lab/templates/run_report.html").read_bytes()
record = {
    "passed": all(checks.values()), "checks": checks,
    "frozen_source_file_count": len(preflight["source_sha256"]),
    "protected_file_count": len(protected),
    "html": reports,
    "wheel": {"path": str(wheel.relative_to(ROOT)), "sha256": digest(wheel)},
    "test_report": "pytest-before.stdout.log", "tests_passed": 607, "test_seconds": 11.68,
    "browser_visual_qa_performed": False,
    "scope": "Static HTML parsing, embedded data equality, JavaScript syntax, tested pure cross-session event-link adapter, package content, and frozen input checks; no browser rendering or visual QA",
}
with (HERE / "quality.json").open("x") as stream:
    stream.write(json.dumps(record, indent=2) + "\n")
print(json.dumps({k:v for k,v in record.items() if k != "html"}, indent=2))
raise SystemExit(0 if record["passed"] else 1)
