"""
Unit tests for Mengajar & KIR Web Dashboard Studio endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.web.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_web_dashboard_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "MENGAJAR & KIR STUDIO" in response.text


def test_web_dashboard_status(client: TestClient) -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "nine_router" in data
    assert "active_model" in data


def test_web_dashboard_sample_input(client: TestClient) -> None:
    response = client.get("/api/sample-input")
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert len(data["content"]) > 0


def test_web_dashboard_documents(client: TestClient) -> None:
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
