"""
test_api.py
-----------
Unit and integration tests for the ContainerCare FastAPI layer using TestClient.
Mocks Docker calls to test healthy, warning, critical, failed, and connection error states.
"""

import sys
import unittest
from unittest.mock import patch
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.docker_monitor import DockerConnectionError


class TestContainerCareApi(unittest.TestCase):
    """Test suite for ContainerCare REST API endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """GET / returns service info and endpoint links."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["service"], "ContainerCare API")
        self.assertIn("/api/containers", data["endpoints"]["containers"])
        self.assertIn("/api/health", data["endpoints"]["health"])

    def test_api_health_endpoint(self):
        """GET /api/health returns 200 with service confirmation."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "ContainerCare API")

    @patch("app.api.routes.get_container_metrics")
    def test_get_containers_success(self, mock_get_metrics):
        """GET /api/containers returns combined metrics and evaluated health statuses."""
        mock_get_metrics.return_value = [
            {
                "id": "c1_test1234",
                "name": "web-frontend",
                "status": "running",
                "cpu": 35.5,
                "memory": 45.0,
                "restarts": 0
            },
            {
                "id": "c2_test5678",
                "name": "database-cluster",
                "status": "running",
                "cpu": 92.0,
                "memory": 88.0,
                "restarts": 3
            },
            {
                "id": "c3_test9012",
                "name": "payment-service",
                "status": "exited",
                "cpu": 0.0,
                "memory": 0.0,
                "restarts": 0
            }
        ]

        response = self.client.get("/api/containers")
        self.assertEqual(response.status_code, 200)
        containers = response.json()
        self.assertEqual(len(containers), 3)

        # Container 1: Healthy
        c1 = containers[0]
        self.assertEqual(c1["id"], "c1_test1234")
        self.assertEqual(c1["name"], "web-frontend")
        self.assertEqual(c1["health"], "HEALTHY")
        self.assertEqual(c1["reasons"], [])

        # Container 2: Critical
        c2 = containers[1]
        self.assertEqual(c2["id"], "c2_test5678")
        self.assertEqual(c2["name"], "database-cluster")
        self.assertEqual(c2["health"], "CRITICAL")
        self.assertIn("High CPU usage", c2["reasons"])
        self.assertIn("High memory usage", c2["reasons"])
        self.assertIn("Multiple container restarts", c2["reasons"])

        # Container 3: Failed
        c3 = containers[2]
        self.assertEqual(c3["id"], "c3_test9012")
        self.assertEqual(c3["name"], "payment-service")
        self.assertEqual(c3["health"], "FAILED")
        self.assertTrue(any("not running" in r for r in c3["reasons"]))

    @patch("app.api.routes.get_container_metrics")
    def test_get_containers_empty(self, mock_get_metrics):
        """GET /api/containers returns empty list if no containers exist."""
        mock_get_metrics.return_value = []
        response = self.client.get("/api/containers")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("app.api.routes.get_container_metrics")
    def test_get_containers_docker_connection_error(self, mock_get_metrics):
        """GET /api/containers returns 503 when Docker daemon is unreachable."""
        mock_get_metrics.side_effect = DockerConnectionError("Docker daemon down")
        response = self.client.get("/api/containers")
        self.assertEqual(response.status_code, 503)
        self.assertIn("Unable to connect to Docker Engine", response.json()["detail"])

    def test_cors_headers_present(self):
        """CORS headers are returned on requests."""
        response = self.client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":
    unittest.main()
