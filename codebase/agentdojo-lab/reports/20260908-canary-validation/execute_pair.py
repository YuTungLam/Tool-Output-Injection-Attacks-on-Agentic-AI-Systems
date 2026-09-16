"""Execute the two prospectively selected arms once; preserve every outcome."""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
PREFLIGHT = HERE / "preflight.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def write(name, value):
    with (HERE / name).open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def check_freeze():
    frozen = json.loads(PREFLIGHT.read_text())
    for key in ("source_sha256", "protected_sha256"):
        for relative, expected in frozen[key].items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
                raise RuntimeError("Frozen source or protected input changed: " + relative)


def main():
    check_freeze()
    native = json.loads((ROOT / "runs/20260908-canary-native-control/validation.json").read_text())
    regression = json.loads((HERE / "passive-regression.json").read_text())
    if not native["passed"] or not regression["passed"]:
        raise RuntimeError("Native controls and passive regression must pass before live trials")
    arms = [
        ("passive", "configs/groq_canary_passive.toml"),
        ("canary", "configs/groq_canary.toml"),
    ]
    if any((ROOT / f"runs/20260908-canary-task31-{arm}").exists() for arm, _ in arms):
        raise RuntimeError("A selected trial output already exists")
    write("pair-started.json", {"started_at": now(), "arm_order": [a for a, _ in arms], "planned_trials": 2})
    environment = {
        **os.environ,
        "HF_HUB_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "PYTHONUNBUFFERED": "1",
    }
    for arm, config in arms:
        check_freeze()
        command = [
            str(ROOT / ".venv/bin/dojo-lab"),
            "run",
            "--config",
            config,
            "--output",
            f"runs/20260908-canary-task31-{arm}",
            "--pacing-state",
            str(HERE / "pacing-state.json"),
        ]
        started = now()
        write(f"{arm}-started.json", {"started_at": started, "command": command})
        print(f"Starting preselected {arm} arm", flush=True)
        with (HERE / f"{arm}-console.log").open("x") as stream:
            process = subprocess.run(
                command, cwd=ROOT, env=environment, stdout=stream, stderr=subprocess.STDOUT
            )
        write(
            f"{arm}-execution.json",
            {
                "started_at": started,
                "ended_at": now(),
                "command": command,
                "exit_code": process.returncode,
                "replacement_trials": 0,
            },
        )
        print(f"Retained {arm} arm; exit code {process.returncode}", flush=True)
    write("pair-ended.json", {"ended_at": now(), "attempted_trials": 2, "replacement_trials": 0})


if __name__ == "__main__":
    main()
