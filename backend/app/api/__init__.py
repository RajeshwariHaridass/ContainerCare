"""
ContainerCare API Package
-------------------------
FastAPI HTTP layer exposing Docker monitoring and health evaluation endpoints.
"""

from .routes import router

__all__ = ["router"]
