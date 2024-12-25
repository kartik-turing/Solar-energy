import json

from fastapi.testclient import TestClient

from app.api.main import app
from app.api.routes.health import (
    HealthCheckRegistry,
    _healthChecks,
    custom_health_check_route,
)

client = TestClient(app)


def test_custom_health_check_route_200():
    registry = HealthCheckRegistry()
    endpoint = custom_health_check_route(registry=registry)
    response = endpoint()
    assert response.status_code == 200


def test_custom_health_check_route_500():
    def custom_check(self):
        return {"status": "HealthCheckStatusEnum.UNHEALTHY"}

    registry = HealthCheckRegistry()
    registry.check = custom_check.__get__(registry)
    endpoint = custom_health_check_route(registry=registry)
    response = endpoint()
    response_content = json.loads(response.body.decode("utf-8"))
    assert response_content == {"status": "DOWN"}


def test_healthz_api():
    response = client.get(
        "/simulation/resi/v1/healthz",
        headers={"Authorization": "Bearer "},
    )
    assert response.json()["status"] == "UP"


def test_health_check_internal_server_error(mocker):
    mock_check = mocker.patch.object(
        _healthChecks,
        "check",
        side_effect=lambda: {"status": "HealthCheckStatusEnum.UNHEALTHY"},
    )

    # Call the endpoint
    response = client.get(
        "/simulation/resi/v1/healthz", headers={"Authorization": "Bearer "}
    )

    assert response.status_code == 500
    assert response.json() == {"status": "DOWN"}
