"""
docker_client.py
----------------
Manages connections to the local Docker Engine using the official Docker Python SDK.
Provides reusable functions to connect and list running/stopped containers safely.
"""

from typing import List, Optional
import docker
from docker.models.containers import Container
from docker.errors import DockerException, APIError


class DockerConnectionError(Exception):
    """Raised when connecting to the local Docker Engine fails."""
    pass


def get_docker_client() -> docker.DockerClient:
    """
    Connects to the local Docker Engine using environment configuration.

    Returns:
        docker.DockerClient: An active Docker client instance.

    Raises:
        DockerConnectionError: If Docker Desktop is not running or unreachable.
    """
    try:
        client = docker.from_env()
        # Verify daemon connectivity
        client.ping()
        return client
    except DockerException as exc:
        raise DockerConnectionError(
            "Unable to connect to Docker Engine. Please ensure Docker Desktop is running."
        ) from exc
    except Exception as exc:
        raise DockerConnectionError(
            f"Unexpected error while connecting to Docker: {exc}"
        ) from exc


def get_containers(
    client: Optional[docker.DockerClient] = None,
    all_containers: bool = True
) -> List[Container]:
    """
    Retrieves containers from the Docker daemon.

    Args:
        client (docker.DockerClient, optional): Docker client instance.
            If None, attempts to connect using get_docker_client().
        all_containers (bool): If True, returns both running and stopped containers.
            If False, returns only running containers.

    Returns:
        List[Container]: List of Docker Container objects.

    Raises:
        DockerConnectionError: If unable to reach the Docker daemon.
    """
    if client is None:
        client = get_docker_client()

    try:
        return client.containers.list(all=all_containers)
    except APIError as exc:
        raise DockerConnectionError(
            f"Docker API error while listing containers: {exc.explanation or exc}"
        ) from exc
    except DockerException as exc:
        raise DockerConnectionError(
            "Lost connection to Docker while listing containers."
        ) from exc


if __name__ == "__main__":
    print("Testing Docker client connection...")
    try:
        cli = get_docker_client()
        containers = get_containers(client=cli, all_containers=True)
        print(f"Successfully connected to Docker! Found {len(containers)} container(s).")
        for c in containers:
            print(f"- {c.short_id} | {c.name} | {c.status}")
    except DockerConnectionError as err:
        print(f"[Error] {err}")
