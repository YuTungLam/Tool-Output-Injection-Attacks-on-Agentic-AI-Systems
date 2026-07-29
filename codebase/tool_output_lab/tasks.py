"""Load and validate synthetic task definitions."""

from __future__ import annotations

import json
from pathlib import Path

from .domain import Task


def load_tasks(path: str | Path) -> list[Task]:
    task_path = Path(path)
    with task_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, list) or not raw:
        raise ValueError("Task file must contain a non-empty JSON list")

    tasks = [Task.from_mapping(item) for item in raw]
    identifiers = [task.task_id for task in tasks]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Task IDs must be unique")
    return tasks
