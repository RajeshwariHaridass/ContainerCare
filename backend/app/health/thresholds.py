"""
thresholds.py
-------------
Defines configurable threshold values for CPU usage, memory usage,
and container restart counts used in ContainerCare health checking.
"""

from dataclasses import dataclass


@dataclass
class HealthThresholds:
    """
    Holds configurable threshold values for evaluating container health.

    Attributes:
        cpu_warning (float): CPU percentage threshold for WARNING (inclusive lower bound).
        cpu_critical (float): CPU percentage threshold above which status is CRITICAL.
        memory_warning (float): Memory percentage threshold for WARNING (inclusive lower bound).
        memory_critical (float): Memory percentage threshold above which status is CRITICAL.
        restarts_warning (int): Restart count threshold for WARNING (inclusive lower bound).
        restarts_critical (int): Restart count threshold for CRITICAL (inclusive lower bound).
    """
    cpu_warning: float = 70.0
    cpu_critical: float = 85.0
    memory_warning: float = 70.0
    memory_critical: float = 85.0
    restarts_warning: int = 1
    restarts_critical: int = 3


# Default thresholds instance used as standard across the health module
DEFAULT_THRESHOLDS = HealthThresholds()
