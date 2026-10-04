"""
health_checker.py
-----------------
Evaluates container metrics using failure detection logic to determine
the overall container health status (HEALTHY, WARNING, CRITICAL, or FAILED).
"""

from typing import Dict, Any, List
from .thresholds import HealthThresholds, DEFAULT_THRESHOLDS
from .failure_detector import detect_failures


def check_container_health(
    metrics: Dict[str, Any],
    thresholds: HealthThresholds = DEFAULT_THRESHOLDS
) -> Dict[str, Any]:
    """
    Determines overall container health status and aggregates failure reasons.

    Classification Rules:
    - FAILED: If container status is not 'running'.
    - CRITICAL: If CPU, memory, or restart count reaches critical level.
    - WARNING: If there are warning-level issues but no critical issues.
    - HEALTHY: If no issues are detected.

    Args:
        metrics (dict): Dictionary containing container performance metrics.
            Example input:
            {
                "name": "web-app",
                "status": "running",
                "cpu": 92,
                "memory": 87,
                "restarts": 3
            }
        thresholds (HealthThresholds, optional): Threshold configuration. Defaults to DEFAULT_THRESHOLDS.

    Returns:
        dict: Summary of overall health status and reasons.
            Example output:
            {
                "name": "web-app",
                "health": "CRITICAL",
                "reasons": [
                    "High CPU usage",
                    "High memory usage",
                    "Multiple container restarts"
                ]
            }
    """
    container_name = metrics.get("name", "unknown")
    issues = detect_failures(metrics, thresholds)

    # 1. No issues -> HEALTHY
    if not issues:
        return {
            "name": container_name,
            "health": "HEALTHY",
            "reasons": []
        }

    # Extract human-readable reasons from detected issues
    reasons: List[str] = [issue["reason"] for issue in issues]

    # 2. Status not running -> FAILED
    if any(issue["severity"] == "FAILED" for issue in issues):
        return {
            "name": container_name,
            "health": "FAILED",
            "reasons": reasons
        }

    # 3. Any CRITICAL metric -> CRITICAL
    if any(issue["severity"] == "CRITICAL" for issue in issues):
        return {
            "name": container_name,
            "health": "CRITICAL",
            "reasons": reasons
        }

    # 4. Any WARNING metric -> WARNING
    return {
        "name": container_name,
        "health": "WARNING",
        "reasons": reasons
    }
