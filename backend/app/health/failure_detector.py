"""
failure_detector.py
-------------------
Identifies individual container problems (stopped container, high CPU,
high memory, excessive restarts) based on metrics and configured thresholds.
"""

from typing import Dict, Any, List, TypedDict
from .thresholds import HealthThresholds, DEFAULT_THRESHOLDS


class DetectedIssue(TypedDict):
    """
    Structured representation of an issue detected in a container.

    Attributes:
        metric (str): The metric or attribute name causing the issue (e.g., 'cpu', 'memory', 'restarts', 'status').
        severity (str): The severity level ('WARNING', 'CRITICAL', or 'FAILED').
        reason (str): Human-readable explanation of the issue.
    """
    metric: str
    severity: str
    reason: str


def detect_failures(
    metrics: Dict[str, Any],
    thresholds: HealthThresholds = DEFAULT_THRESHOLDS
) -> List[DetectedIssue]:
    """
    Analyzes raw container metrics dictionary and returns a list of detected failures/issues.

    Args:
        metrics (dict): Container metrics containing 'name', 'status', 'cpu', 'memory', 'restarts'.
        thresholds (HealthThresholds): Configurable threshold object.

    Returns:
        List[DetectedIssue]: List of detected issues with metric, severity, and human-readable reason.
    """
    issues: List[DetectedIssue] = []

    # 1. Detect Container Status Failure
    status = str(metrics.get("status", "")).strip().lower()
    if status != "running":
        issues.append({
            "metric": "status",
            "severity": "FAILED",
            "reason": f"Container is not running (status: {metrics.get('status', 'unknown')})"
        })
        # If the container is not running, no further metric checks needed
        return issues

    # 2. Detect CPU Usage Issues
    cpu = float(metrics.get("cpu", 0))
    if cpu > thresholds.cpu_critical:
        issues.append({
            "metric": "cpu",
            "severity": "CRITICAL",
            "reason": "High CPU usage"
        })
    elif cpu >= thresholds.cpu_warning:
        issues.append({
            "metric": "cpu",
            "severity": "WARNING",
            "reason": "High CPU usage"
        })

    # 3. Detect Memory Usage Issues
    memory = float(metrics.get("memory", 0))
    if memory > thresholds.memory_critical:
        issues.append({
            "metric": "memory",
            "severity": "CRITICAL",
            "reason": "High memory usage"
        })
    elif memory >= thresholds.memory_warning:
        issues.append({
            "metric": "memory",
            "severity": "WARNING",
            "reason": "High memory usage"
        })

    # 4. Detect Excessive Restarts
    restarts = int(metrics.get("restarts", 0))
    if restarts >= thresholds.restarts_critical:
        issues.append({
            "metric": "restarts",
            "severity": "CRITICAL",
            "reason": "Multiple container restarts"
        })
    elif restarts >= thresholds.restarts_warning:
        issues.append({
            "metric": "restarts",
            "severity": "WARNING",
            "reason": "Container restarts detected"
        })

    return issues
