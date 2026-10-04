"""
ContainerCare Health Package
----------------------------
Provides health checking and failure detection capabilities for container metrics.
"""

from app.health.thresholds import HealthThresholds, DEFAULT_THRESHOLDS
from app.health.failure_detector import detect_failures, DetectedIssue
from app.health.health_checker import check_container_health

__all__ = [
    "HealthThresholds",
    "DEFAULT_THRESHOLDS",
    "detect_failures",
    "DetectedIssue",
    "check_container_health",
]
