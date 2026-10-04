"""
routes.py
---------
FastAPI router defining endpoints for ContainerCare:
- GET /api/containers: Returns combined metrics and health data for all containers.
- GET /api/health: Confirms the ContainerCare API is operational.
"""

from typing import List
import logging
from fastapi import APIRouter, HTTPException, status

from app.docker_monitor import get_container_metrics, DockerConnectionError
from app.health import check_container_health
from .schemas import ContainerResponse, ApiHealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ContainerCare"])


@router.get(
    "/health",
    response_model=ApiHealthResponse,
    summary="API Health Check",
    description="Returns a simple status confirmation that the ContainerCare API service is running.",
)
def api_health() -> ApiHealthResponse:
    return ApiHealthResponse(
        status="ok",
        service="ContainerCare API"
    )


@router.get(
    "/containers",
    response_model=List[ContainerResponse],
    summary="List Containers with Health & Metrics",
    description=(
        "Retrieves all containers from the Docker daemon via Member 1, "
        "evaluates each container's health via Member 2, and returns a consolidated dataset."
    ),
    responses={
        503: {
            "description": "Docker Daemon Unavailable",
            "content": {
                "application/json": {
                    "example": {"detail": "Unable to connect to Docker Engine. Please ensure Docker Desktop is running."}
                }
            }
        }
    }
)
def list_containers() -> List[ContainerResponse]:
    try:
        container_metrics = get_container_metrics(all_containers=True)
    except DockerConnectionError as err:
        logger.error("Docker daemon connection failed: %s", err)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to Docker Engine. Please ensure Docker Desktop is running."
        ) from err
    except Exception as exc:
        logger.exception("Unexpected error while querying containers: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while monitoring containers: {exc}"
        ) from exc

    results: List[ContainerResponse] = []
    for metrics in container_metrics:
        # Pass Member 1 metrics directly to Member 2 health checker
        health_report = check_container_health(metrics)

        results.append(
            ContainerResponse(
                id=metrics.get("id", "unknown"),
                name=metrics.get("name", "unknown"),
                status=metrics.get("status", "unknown"),
                cpu=metrics.get("cpu", 0.0),
                memory=metrics.get("memory", 0.0),
                restarts=metrics.get("restarts", 0),
                health=health_report.get("health", "UNKNOWN"),
                reasons=health_report.get("reasons", []),
            )
        )

    return results
