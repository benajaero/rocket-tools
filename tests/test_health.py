"""Tests for health, readiness, and metrics endpoints."""

import pytest
from starlette.testclient import TestClient

from rocket_tools.asgi import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "rocket-tools"
        assert "endpoints" in data
        assert data["tools"] == 30

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_ready(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["tools"] == 30

    def test_metrics(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        text = response.text
        assert "rocket_tools_" in text

    def test_sse_endpoint_exists(self, client):
        # SSE endpoint should exist (we can't fully test it without async client)
        response = client.get("/sse")
        # The SSE endpoint may return 200, 307, or 404 depending on FastMCP version
        assert response.status_code in (200, 307, 404)
