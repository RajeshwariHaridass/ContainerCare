"""
metrics.py
----------
Collects and computes CPU and memory usage statistics from Docker containers.
Uses non-streaming stats from the Docker SDK and handles stopped containers
and API unavailability gracefully.
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_cpu_percent(stats: Optional[Dict[str, Any]]) -> float:
    """
    Calculates the CPU usage percentage from a Docker stats dictionary.

    Formula (matches standard Docker CLI calculation):
        cpu_delta = cpu_stats.cpu_usage.total_usage - precpu_stats.cpu_usage.total_usage
        system_delta = cpu_stats.system_cpu_usage - precpu_stats.system_cpu_usage
        online_cpus = cpu_stats.online_cpus (or count of percpu_usage, default 1)
        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0

    Args:
        stats: Dictionary returned by Docker stats API.

    Returns:
        float: CPU usage percentage rounded to 2 decimal places (0.0 if unavailable).
    """
    if not stats or not isinstance(stats, dict):
        return 0.0

    try:
        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})

        cpu_usage = cpu_stats.get("cpu_usage", {})
        precpu_usage = precpu_stats.get("cpu_usage", {})

        total_usage = cpu_usage.get("total_usage", 0)
        precpu_total_usage = precpu_usage.get("total_usage", 0)
        cpu_delta = float(total_usage - precpu_total_usage)

        system_usage = cpu_stats.get("system_cpu_usage", 0)
        precpu_system_usage = precpu_stats.get("system_cpu_usage", 0)
        system_delta = float(system_usage - precpu_system_usage)

        # Determine the number of CPUs allocated/available
        online_cpus = cpu_stats.get("online_cpus")
        if not online_cpus:
            percpu = cpu_usage.get("percpu_usage")
            online_cpus = len(percpu) if isinstance(percpu, list) and percpu else 1

        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_percent = (cpu_delta / system_delta) * float(online_cpus) * 100.0
            return round(cpu_percent, 2)
    except (TypeError, KeyError, ZeroDivisionError, AttributeError) as exc:
        logger.debug("Error calculating CPU percent: %s", exc)

    return 0.0


def calculate_memory_percent(stats: Optional[Dict[str, Any]]) -> float:
    """
    Calculates the memory usage percentage based on container memory usage and limit.

    Formula:
        memory_percent = (usage / limit) * 100.0

    Args:
        stats: Dictionary returned by Docker stats API.

    Returns:
        float: Memory usage percentage rounded to 2 decimal places (0.0 if unavailable).
    """
    if not stats or not isinstance(stats, dict):
        return 0.0

    try:
        memory_stats = stats.get("memory_stats", {})
        usage = memory_stats.get("usage", 0)
        limit = memory_stats.get("limit", 0)

        if limit and limit > 0 and usage > 0:
            percent = (float(usage) / float(limit)) * 100.0
            return round(percent, 2)
    except (TypeError, KeyError, ZeroDivisionError, AttributeError) as exc:
        logger.debug("Error calculating memory percent: %s", exc)

    return 0.0


def get_container_stats(container: Any) -> Dict[str, float]:
    """
    Fetches non-streaming stats from a Docker container and computes CPU and memory percentages.
    If the container is stopped or if stats retrieval fails, returns 0.0 for both metrics.

    Args:
        container: Docker container object or mock.

    Returns:
        dict: {"cpu": float, "memory": float} with values rounded to 2 decimal places.
    """
    # Check container status; stopped containers must return 0.0 for cpu and memory
    status = getattr(container, "status", None)
    if not status:
        attrs = getattr(container, "attrs", {})
        if isinstance(attrs, dict):
            status = attrs.get("State", {}).get("Status", "unknown")

    if str(status).strip().lower() != "running":
        return {"cpu": 0.0, "memory": 0.0}

    try:
        # Request a single, non-streaming snapshot of container stats
        stats_payload = container.stats(stream=False)
        cpu = calculate_cpu_percent(stats_payload)
        memory = calculate_memory_percent(stats_payload)
        return {
            "cpu": cpu,
            "memory": memory
        }
    except Exception as exc:
        # Container may have stopped during call, or API timed out
        logger.warning(
            "Could not retrieve stats for container %s: %s",
            getattr(container, "name", "unknown"),
            exc
        )
        return {"cpu": 0.0, "memory": 0.0}
