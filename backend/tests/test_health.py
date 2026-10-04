"""
test_health.py
--------------
Unit tests for ContainerCare health checking and failure detection logic.
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so modules can be imported directly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.health.health_checker import check_container_health
from app.health.failure_detector import detect_failures
from app.health.thresholds import HealthThresholds


class TestContainerHealth(unittest.TestCase):
    """Test cases for container health evaluation."""

    def test_case_a_healthy_container(self):
        """A. Healthy container: CPU=30, Memory=40, Restarts=0, Status=running -> HEALTHY"""
        metrics = {
            "name": "healthy-app",
            "status": "running",
            "cpu": 30,
            "memory": 40,
            "restarts": 0
        }
        result = check_container_health(metrics)
        self.assertEqual(result["health"], "HEALTHY")
        self.assertEqual(result["reasons"], [])

    def test_case_b_warning_container(self):
        """B. Warning container: CPU=75, Memory=60, Restarts=0, Status=running -> WARNING"""
        metrics = {
            "name": "warning-app",
            "status": "running",
            "cpu": 75,
            "memory": 60,
            "restarts": 0
        }
        result = check_container_health(metrics)
        self.assertEqual(result["health"], "WARNING")
        self.assertIn("High CPU usage", result["reasons"])

    def test_case_c_critical_container(self):
        """C. Critical container: CPU=92, Memory=87, Restarts=3, Status=running -> CRITICAL"""
        metrics = {
            "name": "critical-app",
            "status": "running",
            "cpu": 92,
            "memory": 87,
            "restarts": 3
        }
        result = check_container_health(metrics)
        self.assertEqual(result["health"], "CRITICAL")
        self.assertEqual(len(result["reasons"]), 3)
        self.assertIn("High CPU usage", result["reasons"])
        self.assertIn("High memory usage", result["reasons"])
        self.assertIn("Multiple container restarts", result["reasons"])

    def test_case_d_failed_container(self):
        """D. Failed container: CPU=0, Memory=0, Restarts=0, Status=stopped -> FAILED"""
        metrics = {
            "name": "stopped-app",
            "status": "stopped",
            "cpu": 0,
            "memory": 0,
            "restarts": 0
        }
        result = check_container_health(metrics)
        self.assertEqual(result["health"], "FAILED")
        self.assertTrue(any("not running" in r for r in result["reasons"]))

    def test_case_e_critical_single_metric(self):
        """E. Critical because of only one metric: CPU=90, Memory=40, Restarts=0, Status=running -> CRITICAL"""
        metrics = {
            "name": "single-metric-critical-app",
            "status": "running",
            "cpu": 90,
            "memory": 40,
            "restarts": 0
        }
        result = check_container_health(metrics)
        self.assertEqual(result["health"], "CRITICAL")
        self.assertEqual(result["reasons"], ["High CPU usage"])

    def test_failure_detector_directly(self):
        """Verify that failure_detector returns structured issue metadata."""
        metrics = {
            "name": "test-service",
            "status": "running",
            "cpu": 80,
            "memory": 90,
            "restarts": 1
        }
        issues = detect_failures(metrics)
        self.assertEqual(len(issues), 3)
        severities = [issue["severity"] for issue in issues]
        self.assertIn("WARNING", severities)
        self.assertIn("CRITICAL", severities)

    def test_custom_thresholds(self):
        """Verify that health_checker respects custom threshold configurations."""
        custom_thresholds = HealthThresholds(
            cpu_warning=50.0,
            cpu_critical=60.0
        )
        metrics = {
            "name": "custom-app",
            "status": "running",
            "cpu": 65,
            "memory": 10,
            "restarts": 0
        }
        result = check_container_health(metrics, thresholds=custom_thresholds)
        self.assertEqual(result["health"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
