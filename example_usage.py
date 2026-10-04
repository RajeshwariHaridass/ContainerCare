"""
example_usage.py
----------------
Demonstrates how Member 1 or Member 3 can integrate and call Member 2's
health checking module using mock container metrics dictionaries.
"""

import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.health import check_container_health, detect_failures

if __name__ == "__main__":
    # Sample mock container metrics as provided by Member 1
    mock_containers = [
        {
            "name": "web-frontend",
            "status": "running",
            "cpu": 35.5,
            "memory": 45.0,
            "restarts": 0
        },
        {
            "name": "api-gateway",
            "status": "running",
            "cpu": 78.0,
            "memory": 65.0,
            "restarts": 1
        },
        {
            "name": "database-cluster",
            "status": "running",
            "cpu": 92.0,
            "memory": 87.0,
            "restarts": 3
        },
        {
            "name": "payment-service",
            "status": "stopped",
            "cpu": 0.0,
            "memory": 0.0,
            "restarts": 0
        }
    ]

    print("=== ContainerCare Health Check Summary ===\n")
    for container in mock_containers:
        health_report = check_container_health(container)
        print(f"Container: {health_report['name']}")
        print(f"  Status:  {health_report['health']}")
        if health_report["reasons"]:
            print(f"  Reasons: {', '.join(health_report['reasons'])}")
        else:
            print("  Reasons: None (Operating normally)")
        print("-" * 40)
