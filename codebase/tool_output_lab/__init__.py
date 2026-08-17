"""Sandboxed tool-output injection research harness."""

__version__ = "0.7.0"

from .attack_spec import AttackSpec
from .domain import Condition, Task
from .experiment import ExperimentConfig, ExperimentResult, run_experiment

__all__ = [
    "AttackSpec",
    "Condition",
    "ExperimentConfig",
    "ExperimentResult",
    "Task",
    "run_experiment",
]
