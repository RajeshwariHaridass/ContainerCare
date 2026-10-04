"""
test_docker_monitor.py
-----------------------
Unit tests for Member 1: Docker Monitoring & Data Collection module.
Uses unittest.mock to test client connection, container inspection,
and metrics computation without requiring a live Docker daemon.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import docker.errors
from app.docker_monitor.docker_client import (
    get_docker_client,
    get_containers,
    DockerConnectionError,
)
from app.docker_monitor.container_info import (
    get_container_id,
    get_container_name,
    get_container_status,
    get_container_restart_count,
    extract_container_info,
)
from app.docker_monitor.metrics import (
    calculate_cpu_percent,
    calculate_memory_percent,
    get_container_stats,
)
from app.docker_monitor import get_container_metrics
from app.health import check_container_health


class TestDockerClient(unittest.TestCase):
    """Unit tests for Docker client connection and container retrieval."""

    @patch("docker.from_env")
    def test_get_docker_client_success(self, mock_from_env):
        mock_cli = MagicMock()
        mock_cli.ping.return_value = True
        mock_from_env.return_value = mock_cli

        client = get_docker_client()
        self.assertEqual(client, mock_cli)
        mock_cli.ping.assert_called_once()

    @patch("docker.from_env")
    def test_get_docker_client_failure(self, mock_from_env):
        mock_from_env.side_effect = docker.errors.DockerException("Daemon down")

        with self.assertRaises(DockerConnectionError) as ctx:
            get_docker_client()
        self.assertIn("Please ensure Docker Desktop is running", str(ctx.exception))

    def test_get_containers(self):
        mock_cli = MagicMock()
        mock_c1 = MagicMock(name="c1")
        mock_c2 = MagicMock(name="c2")
        mock_cli.containers.list.return_value = [mock_c1, mock_c2]

        containers = get_containers(client=mock_cli, all_containers=True)
        self.assertEqual(len(containers), 2)
        mock_cli.containers.list.assert_called_once_with(all=True)

    def test_get_containers_api_error(self):
        mock_cli = MagicMock()
        mock_cli.containers.list.side_effect = docker.errors.APIError("API error")

        with self.assertRaises(DockerConnectionError):
            get_containers(client=mock_cli, all_containers=True)


class TestContainerInfo(unittest.TestCase):
    """Unit tests for container metadata extraction."""

    def test_get_container_id(self):
        # Case 1: short_id available
        c1 = MagicMock()
        c1.short_id = "abc123def456"
        self.assertEqual(get_container_id(c1), "abc123def456")

        # Case 2: full id fallback (should truncate to 12 chars)
        c2 = MagicMock(spec=["id"])
        c2.id = "1234567890abcdef1234"
        self.assertEqual(get_container_id(c2), "1234567890ab")

        # Case 3: attrs fallback
        c3 = MagicMock(spec=["attrs"])
        c3.attrs = {"Id": "fedcba0987654321"}
        self.assertEqual(get_container_id(c3), "fedcba098765")

        # Case 4: completely missing attributes
        c4 = MagicMock(spec=[])
        self.assertEqual(get_container_id(c4), "unknown")

    def test_get_container_name(self):
        # Case 1: name with leading slash
        c1 = MagicMock()
        c1.name = "/my-web-service"
        self.assertEqual(get_container_name(c1), "my-web-service")

        # Case 2: name from attrs
        c2 = MagicMock(spec=["attrs"])
        c2.attrs = {"Name": "/api-service"}
        self.assertEqual(get_container_name(c2), "api-service")

        # Case 3: missing name
        c3 = MagicMock(spec=[])
        self.assertEqual(get_container_name(c3), "unknown")

    def test_get_container_status(self):
        # Case 1: direct status
        c1 = MagicMock()
        c1.status = "RUNNING"
        self.assertEqual(get_container_status(c1), "running")

        # Case 2: status from attrs['State']['Status']
        c2 = MagicMock(spec=["attrs"])
        c2.attrs = {"State": {"Status": "exited"}}
        self.assertEqual(get_container_status(c2), "exited")

        # Case 3: missing status
        c3 = MagicMock(spec=[])
        self.assertEqual(get_container_status(c3), "unknown")

    def test_get_container_restart_count(self):
        # Case 1: from top-level attrs RestartCount
        c1 = MagicMock()
        c1.attrs = {"RestartCount": 4}
        self.assertEqual(get_container_restart_count(c1), 4)

        # Case 2: from State['RestartCount']
        c2 = MagicMock(spec=["attrs"])
        c2.attrs = {"State": {"RestartCount": 2}}
        self.assertEqual(get_container_restart_count(c2), 2)

        # Case 3: missing restart count defaults to 0
        c3 = MagicMock(spec=[])
        self.assertEqual(get_container_restart_count(c3), 0)

    def test_extract_container_info(self):
        c = MagicMock()
        c.short_id = "test1234"
        c.name = "test-container"
        c.status = "running"
        c.attrs = {"RestartCount": 1}

        info = extract_container_info(c)
        self.assertEqual(info, {
            "id": "test1234",
            "name": "test-container",
            "status": "running",
            "restarts": 1
        })


class TestMetricsCalculation(unittest.TestCase):
    """Unit tests for CPU & memory calculations and stats collection."""

    def test_calculate_cpu_percent(self):
        # Sample Docker stats snapshot
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 200000000},
                "system_cpu_usage": 1000000000,
                "online_cpus": 2
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 100000000},
                "system_cpu_usage": 500000000
            }
        }
        # cpu_delta = 100,000,000; system_delta = 500,000,000
        # (100000000 / 500000000) * 2 * 100 = 0.2 * 2 * 100 = 40.0%
        cpu_pct = calculate_cpu_percent(stats)
        self.assertEqual(cpu_pct, 40.0)

    def test_calculate_cpu_percent_zero_delta(self):
        # No system delta (e.g. frozen or first sample)
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 100},
                "system_cpu_usage": 1000,
                "online_cpus": 1
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 100},
                "system_cpu_usage": 1000
            }
        }
        self.assertEqual(calculate_cpu_percent(stats), 0.0)

    def test_calculate_cpu_percent_empty_or_invalid(self):
        self.assertEqual(calculate_cpu_percent(None), 0.0)
        self.assertEqual(calculate_cpu_percent({}), 0.0)

    def test_calculate_memory_percent(self):
        stats = {
            "memory_stats": {
                "usage": 536870912,        # 512 MB
                "limit": 1073741824        # 1024 MB
            }
        }
        mem_pct = calculate_memory_percent(stats)
        self.assertEqual(mem_pct, 50.0)

    def test_calculate_memory_percent_zero_limit_or_missing(self):
        self.assertEqual(calculate_memory_percent({"memory_stats": {"usage": 100, "limit": 0}}), 0.0)
        self.assertEqual(calculate_memory_percent({}), 0.0)
        self.assertEqual(calculate_memory_percent(None), 0.0)

    def test_get_container_stats_stopped_container(self):
        stopped_c = MagicMock()
        stopped_c.status = "exited"

        stats = get_container_stats(stopped_c)
        self.assertEqual(stats, {"cpu": 0.0, "memory": 0.0})
        # container.stats() should not be called for stopped containers
        stopped_c.stats.assert_not_called()

    def test_get_container_stats_running_container(self):
        running_c = MagicMock()
        running_c.status = "running"
        running_c.stats.return_value = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 150000000},
                "system_cpu_usage": 2000000000,
                "online_cpus": 1
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 50000000},
                "system_cpu_usage": 1000000000
            },
            "memory_stats": {
                "usage": 250000000,
                "limit": 1000000000
            }
        }

        stats = get_container_stats(running_c)
        running_c.stats.assert_called_once_with(stream=False)
        self.assertEqual(stats["cpu"], 10.0)
        self.assertEqual(stats["memory"], 25.0)

    def test_get_container_stats_exception_handled(self):
        running_c = MagicMock()
        running_c.status = "running"
        running_c.stats.side_effect = docker.errors.NotFound("Container was stopped")

        stats = get_container_stats(running_c)
        self.assertEqual(stats, {"cpu": 0.0, "memory": 0.0})


class TestGetContainerMetricsIntegration(unittest.TestCase):
    """Test get_container_metrics output and compatibility with Member 2."""

    def test_get_container_metrics_compatibility_with_member2(self):
        mock_cli = MagicMock()

        # Mock Container 1: Running web app
        c1 = MagicMock()
        c1.short_id = "c1_id123"
        c1.name = "web-app"
        c1.status = "running"
        c1.attrs = {"RestartCount": 0}
        c1.stats.return_value = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 355000000},
                "system_cpu_usage": 2000000000,
                "online_cpus": 2
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 0},
                "system_cpu_usage": 2000000000
            },
            "memory_stats": {
                "usage": 450,
                "limit": 1000
            }
        }

        # Mock Container 2: Exited database
        c2 = MagicMock()
        c2.short_id = "c2_id456"
        c2.name = "database"
        c2.status = "exited"
        c2.attrs = {"RestartCount": 2}

        mock_cli.containers.list.return_value = [c1, c2]

        metrics_list = get_container_metrics(all_containers=True, client=mock_cli)

        self.assertEqual(len(metrics_list), 2)

        # Validate required keys
        required_keys = {"id", "name", "status", "cpu", "memory", "restarts"}
        for item in metrics_list:
            self.assertTrue(required_keys.issubset(item.keys()))

        # Feed directly to Member 2's check_container_health without error
        report_c1 = check_container_health(metrics_list[0])
        self.assertEqual(report_c1["name"], "web-app")
        self.assertIn(report_c1["health"], ["HEALTHY", "WARNING", "CRITICAL"])

        report_c2 = check_container_health(metrics_list[1])
        self.assertEqual(report_c2["name"], "database")
        self.assertEqual(report_c2["health"], "FAILED")


if __name__ == "__main__":
    unittest.main()
