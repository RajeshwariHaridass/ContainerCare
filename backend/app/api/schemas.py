"""
schemas.py
----------
Pydantic response models for ContainerCare API.
"""

from typing import List
from pydantic import BaseModel, Field


class ContainerResponse(BaseModel):
    """
    Consolidated container health and performance information.
    Combines Member 1 metrics with Member 2 health evaluations.
    """
    id: str = Field(..., description="Short container identifier")
    name: str = Field(..., description="Cleaned container name")
    status: str = Field(..., description="Docker lifecycle state (running, exited, etc.)")
    cpu: float = Field(..., description="CPU usage percentage (0.0 - 100.0)")
    memory: float = Field(..., description="Memory usage percentage (0.0 - 100.0)")
    restarts: int = Field(..., description="Total restart count")
    health: str = Field(..., description="Evaluated health status: HEALTHY, WARNING, CRITICAL, or FAILED")
    reasons: List[str] = Field(default_factory=list, description="List of alert reasons or detected failure issues")


class ApiHealthResponse(BaseModel):
    """
    Status confirmation for the ContainerCare API service.
    """
    status: str = Field(default="ok", description="API service health status")
    service: str = Field(default="ContainerCare API", description="Service name")
