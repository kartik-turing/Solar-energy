import json
import os

import pytest
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.api.main import app, app2, validation_exception_handler

endpoint = "simulation/resi/v1/simulationjob"
input_params = {
    "designVendorName": "aurora",
    "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
    "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
    "simulationMode": "MODE_PV",
    "simulationYears": 1,
    "outputResolution": "year",
}


@pytest.fixture
def test_client():
    return TestClient(app)


def test_token_missing(test_client, mocker):
    mocker.patch.dict(os.environ, {"YOUR_ENV": "outside-testing"})
    response = test_client.post(
        endpoint, json=input_params, headers={"token": ""}
    )
    assert response.json() == {
        "responses": {
            "401": {
                "description": "Authorization Error",
                "content": {
                    "detail": "Token missing",
                },
            }
        }
    }


def test_invalid_token(test_client, mocker):
    mocker.patch.dict(os.environ, {"YOUR_ENV": "outside-testing"})
    response = test_client.post(
        endpoint,
        json=input_params,
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "responses": {
            "401": {
                "description": "Authorization Error",
                "content": {
                    "detail": "Invalid Token",
                },
            }
        }
    }


def test_exception_handling(test_client, mocker):
    mocker.patch.dict(os.environ, {"YOUR_ENV": "outside-testing"})
    mock_authorize = mocker.patch("app.api.main.authorize")
    mock_authorize.side_effect = Exception("Some unexpected exception")

    response = test_client.post(
        endpoint,
        json=input_params,
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "responses": {
            "401": {
                "description": "Authorization Error",
                "content": {
                    "detail": "Invalid Token",
                },
            }
        }
    }


class MockValidationExc:
    def __init__(self):
        self.error = []
        self.error.append({
            "loc": "location",
            "type": "value_error.jsondecode",
            "ctx": {"doc": "value"},
        })

    def errors(self):
        return self.error


@pytest.mark.asyncio
async def test_validation_exception_handler(mocker, test_client):
    exc_instance = MockValidationExc()
    response = await validation_exception_handler(
        Request(scope={"type": "http"}), exc_instance
    )
    assert response.status_code == 422
