"""Main FastAPI application for bricks-and-graphs."""

# mypy: ignore-errors

import sys
from datetime import UTC, datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from bag import __version__


class StatusResponse(BaseModel):
    """Response model for the status endpoint."""

    status: str
    version: str
    timestamp: datetime
    python_version: str


# Create FastAPI app
app = FastAPI(
    title="Bricks and Graphs API",
    description="An agentic framework API for multi-block agent decision graphs",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Get the current status of the API service.

    Returns:
        StatusResponse: Current service status information
    """
    return StatusResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(UTC),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker and load balancers."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with basic API information.

    Returns:
        Dict with API information
    """
    return {
        "name": "Bricks and Graphs API",
        "version": __version__,
        "docs": "/docs",
        "status": "/status",
    }


def main() -> None:
    """Main entry point for running the FastAPI server."""
    uvicorn.run(
        "bag.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
