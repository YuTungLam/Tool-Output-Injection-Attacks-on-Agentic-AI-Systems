"""Sandboxed tool-output injection research harness."""

__version__ = "0.3.0"

from .domain import Condition, Task
from .experiment import ExperimentConfig, ExperimentResult, run_experiment

__all__ = [
    "Condition",
    "ExperimentConfig",
    "ExperimentResult",
    "Task",
    "run_experiment",
]
