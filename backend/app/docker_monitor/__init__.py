"""
ContainerCare Docker Monitor Package
-----------------------------------
Member 1: Docker Monitoring & Data Collection.
Connects to local Docker Engine, extracts container metadata,
and computes real CPU & memory performance metrics.
"""

from typing import List, Dict, Any, Optional
import json
import logging

from .docker_client import (
    get_docker_client,
    get_containers,
    DockerConnectionError,
)
from .container_info import (
    get_container_id,
    get_container_name,
    get_container_status,
    get_container_restart_count,
    extract_container_info,
)
from .metrics import (
    calculate_cpu_percent,
    calculate_memory_percent,
    get_container_stats,
)

logger = logging.getLogger(__name__)


def get_container_metrics(
    all_containers: bool = True,
    client: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Collects performance metrics and status information from local Docker containers.
    Returns dictionaries fully compatible with Member 2's health checking module.

    Args:
        all_containers (bool): If True, inspects both running and stopped containers.
        client (docker.DockerClient, optional): Reusable Docker client instance.

    Returns:
        List[Dict[str, Any]]: List of container metric dictionaries containing:
            - id: Container ID (short)
            - name: Container name
            - status: Execution state ('running', 'exited', etc.)
            - cpu: CPU usage percentage rounded to 2 decimal places (0.0 if stopped)
            - memory: Memory usage percentage rounded to 2 decimal places (0.0 if stopped)
            - restarts: Total container restart count
    """
    if client is None:
        client = get_docker_client()

    containers = get_containers(client=client, all_containers=all_containers)
    collected_metrics: List[Dict[str, Any]] = []

    for container in containers:
        try:
            info = extract_container_info(container)
            stats = get_container_stats(container)

            collected_metrics.append({
                "id": info["id"],
                "name": info["name"],
                "status": info["status"],
                "cpu": stats["cpu"],
                "memory": stats["memory"],
                "restarts": info["restarts"],
            })
        except Exception as exc:
            logger.warning(
                "Skipping container due to unexpected inspection error: %s",
                exc
            )
            continue

    return collected_metrics


__all__ = [
    "get_docker_client",
    "get_containers",
    "DockerConnectionError",
    "get_container_id",
    "get_container_name",
    "get_container_status",
    "get_container_restart_count",
    "extract_container_info",
    "calculate_cpu_percent",
    "calculate_memory_percent",
    "get_container_stats",
    "get_container_metrics",
]


if __name__ == "__main__":
    print("=== Member 1: Docker Monitoring & Data Collection ===")
    try:
        metrics = get_container_metrics(all_containers=True)
        if not metrics:
            print("No Docker containers found on the host.")
        else:
            print(f"Collected metrics for {len(metrics)} container(s):")
            print(json.dumps(metrics, indent=2))
    except DockerConnectionError as err:
        print(f"[Connection Error] {err}")
    except Exception as err:
        print(f"[Unexpected Error] {err}")
