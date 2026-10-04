"""
docker_health_demo.py
---------------------
End-to-End Integration Demo:
Connects Member 1 (Docker Monitoring & Data Collection)
with Member 2 (Health Checking & Failure Detection).

Flow:
Docker Engine -> Member 1 collects real metrics -> Member 2 analyzes metrics -> Health Result
"""

import sys
import json
from pathlib import Path

# Add backend directory to sys.path so modules can be imported directly
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from app.docker_monitor import get_container_metrics, DockerConnectionError
    from app.health import check_container_health
except ImportError as exc:
    print(f"[Error] Failed to import ContainerCare modules: {exc}")
    sys.exit(1)


def run_integration_demo():
    print("=" * 70)
    print("   ContainerCare - Docker Health & Monitoring Integration Demo   ")
    print("=" * 70)
    print("Flow: Docker Engine -> Member 1 (Metrics) -> Member 2 (Health Decision)\n")

    # Step 1 & 2: Connect to Docker & Collect Real Metrics (Member 1)
    print("[1] Connecting to Docker Engine and collecting real metrics...")
    try:
        container_metrics = get_container_metrics(all_containers=True)
    except DockerConnectionError as err:
        print(f"\n[Docker Error] {err}")
        print("Please verify that Docker Desktop is installed and running, then try again.")
        return
    except Exception as err:
        print(f"\n[Unexpected Error] An error occurred while contacting Docker: {err}")
        return

    # Check if any containers were found
    if not container_metrics:
        print("\n[Notice] No Docker containers found on your local Docker daemon.")
        print("Tip: Run a container (e.g. 'docker run -d --name nginx-test -p 8080:80 nginx') and rerun this demo.")
        return

    print(f"-> Successfully collected real metrics for {len(container_metrics)} container(s).\n")

    # Step 3 & 4: Print Raw Member 1 Metrics
    print("[2] Raw Member 1 Container Metrics Output:")
    print("-" * 70)
    print(json.dumps(container_metrics, indent=2))
    print("-" * 70)

    # Step 5 & 6: Pass each dictionary to Member 2 and print health report
    print("\n[3] Member 2 Health & Failure Evaluation:")
    print("=" * 70)

    for metrics in container_metrics:
        # Pass Member 1 dictionary directly to Member 2
        health_report = check_container_health(metrics)

        name = metrics.get("name", "unknown")
        cid = metrics.get("id", "unknown")
        status = metrics.get("status", "unknown")
        cpu = metrics.get("cpu", 0.0)
        memory = metrics.get("memory", 0.0)
        restarts = metrics.get("restarts", 0)
        health = health_report.get("health", "UNKNOWN")
        reasons = health_report.get("reasons", [])

        # Visual indicator tag
        tag = f"[{health}]"

        print(f"Container: {name} (ID: {cid})")
        print(f"  Docker Status: {status} | CPU: {cpu:.2f}% | Memory: {memory:.2f}% | Restarts: {restarts}")
        print(f"  Health Check:  {tag:<10}")
        if reasons:
            print(f"  Alert Reasons: {', '.join(reasons)}")
        else:
            print("  Alert Reasons: None (Normal operation)")
        print("-" * 70)

    print("\nIntegration execution completed successfully.")


if __name__ == "__main__":
    run_integration_demo()
