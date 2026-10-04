"""
main.py
-------
FastAPI application entry point for ContainerCare.
Configures CORS middleware and registers API routes.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure the backend directory is in sys.path when executed directly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.api import router

app = FastAPI(
    title="ContainerCare API",
    version="1.0.0",
    description="ContainerCare – Docker Container Health Monitor REST API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS so future frontend (Vite/React/Next.js/vanilla) can access the API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api
app.include_router(router)


@app.get("/", tags=["Root"])
def root_redirect():
    """
    Root endpoint directing clients to health check, container monitoring, and documentation.
    """
    return {
        "service": "ContainerCare API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "containers": "/api/containers"
        }
    }


def start_server():
    """Starts the Uvicorn ASGI server."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start_server()
