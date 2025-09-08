"""Tests for the FastAPI application."""

from fastapi.testclient import TestClient

from bag.api.main import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Test the root endpoint returns expected data."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Bricks and Graphs API"


def test_status_endpoint() -> None:
    """Test the status endpoint returns healthy status."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "python_version" in data


def test_openapi_docs() -> None:
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200
