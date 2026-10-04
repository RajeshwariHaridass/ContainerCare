"""
container_info.py
-----------------
Extracts metadata (ID, name, status, restart count) from Docker container objects.
Handles missing or malformed attributes safely.
"""

from typing import Any, Dict


def get_container_id(container: Any) -> str:
    """
    Extracts the container ID, preferring the 12-character short ID.

    Args:
        container: Docker container object or mock.

    Returns:
        str: Container ID or 'unknown' if not found.
    """
    try:
        short_id = getattr(container, "short_id", None)
        if short_id:
            return str(short_id)

        full_id = getattr(container, "id", None)
        if full_id:
            return str(full_id)[:12]

        attrs = getattr(container, "attrs", None)
        if isinstance(attrs, dict) and "Id" in attrs:
            return str(attrs["Id"])[:12]
    except (AttributeError, TypeError):
        pass

    return "unknown"


def get_container_name(container: Any) -> str:
    """
    Extracts the container name, stripping any leading slash.

    Args:
        container: Docker container object or mock.

    Returns:
        str: Container name or 'unknown' if not found.
    """
    try:
        name = getattr(container, "name", None)
        if name:
            return str(name).lstrip("/")

        attrs = getattr(container, "attrs", None)
        if isinstance(attrs, dict) and "Name" in attrs:
            return str(attrs["Name"]).lstrip("/")
    except (AttributeError, TypeError):
        pass

    return "unknown"


def get_container_status(container: Any) -> str:
    """
    Extracts the container execution status (e.g., 'running', 'exited', 'paused').

    Args:
        container: Docker container object or mock.

    Returns:
        str: Lowercase container status or 'unknown'.
    """
    try:
        status = getattr(container, "status", None)
        if status:
            return str(status).strip().lower()

        attrs = getattr(container, "attrs", None)
        if isinstance(attrs, dict):
            state = attrs.get("State", {})
            if isinstance(state, dict) and "Status" in state:
                return str(state["Status"]).strip().lower()
            if "Status" in attrs:
                return str(attrs["Status"]).strip().lower()
    except (AttributeError, TypeError):
        pass

    return "unknown"


def get_container_restart_count(container: Any) -> int:
    """
    Extracts the restart count from Docker container inspection information.

    Args:
        container: Docker container object or mock.

    Returns:
        int: Number of times container has restarted (default 0).
    """
    try:
        attrs = getattr(container, "attrs", None)
        if isinstance(attrs, dict):
            if "RestartCount" in attrs and attrs["RestartCount"] is not None:
                return int(attrs["RestartCount"])

            state = attrs.get("State", {})
            if isinstance(state, dict) and "RestartCount" in state and state["RestartCount"] is not None:
                return int(state["RestartCount"])

        # Check direct attribute if present in custom or mock objects
        restarts = getattr(container, "restart_count", None)
        if restarts is not None:
            return int(restarts)
    except (AttributeError, TypeError, ValueError):
        pass

    return 0


def extract_container_info(container: Any) -> Dict[str, Any]:
    """
    Consolidates basic container metadata into a dictionary.

    Args:
        container: Docker container object or mock.

    Returns:
        dict: Dictionary containing 'id', 'name', 'status', and 'restarts'.
    """
    return {
        "id": get_container_id(container),
        "name": get_container_name(container),
        "status": get_container_status(container),
        "restarts": get_container_restart_count(container),
    }
