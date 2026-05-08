from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_health_endpoint_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0",
    }
