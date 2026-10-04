"""
__main__.py
-----------
Direct entry point for executing Member 1 independently:
python -m app.docker_monitor
"""

import sys
import json
from pathlib import Path

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.docker_monitor import get_container_metrics, DockerConnectionError


def main() -> None:
    print("==================================================")
    print("  ContainerCare - Member 1: Docker Monitor Demo   ")
    print("==================================================")
    try:
        metrics = get_container_metrics(all_containers=True)
        if not metrics:
            print("No Docker containers found on the host.")
            return

        print(f"Successfully collected metrics from {len(metrics)} container(s):\n")
        print(json.dumps(metrics, indent=2))

        print("\nSummary Table:")
        print(f"{'ID':<14} {'NAME':<35} {'STATUS':<12} {'CPU %':<10} {'MEM %':<10} {'RESTARTS':<8}")
        print("-" * 95)
        for m in metrics:
            print(f"{m['id']:<14} {m['name']:<35} {m['status']:<12} {m['cpu']:<10.2f} {m['memory']:<10.2f} {m['restarts']:<8}")

    except DockerConnectionError as err:
        print(f"\n[Docker Connection Error] {err}")
    except Exception as err:
        print(f"\n[Unexpected Error] {err}")


if __name__ == "__main__":
    main()
