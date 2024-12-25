import json

import pytest
import requests
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.models import PVSimInput
from app.api.routes.simulation_job_management import router, run_simulation_detailed

access_token = "mock"
client = TestClient(router)
client_main = TestClient(app)

api_endpoint_detailed = "/simulation/resi/v1/simulationjob/detailed"


@pytest.fixture
def mock_auth_function(mocker):
    mocker.patch("app.auth.verify_token", return_value={"sub": "testuser"})


def test_start_simulation_detailed_success():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_start_simulation_detailed_execute_failure(mocker):
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "month",
    }
    with mocker.patch(
        "app.api.routes.simulation_job_management.PySAM_PVSim.execute",
        side_effect=AttributeError("Attribute Error in pv execute"),
    ):
        response = run_simulation_detailed(
            input_params=PVSimInput(**input_params), Authorization="mocked"
        )
        assert response.status_code == 400


def test_start_simulation_detailed_success_month():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "month",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_start_simulation_detailed_success_hour():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "hour",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_start_simulation_detailed_success_with_battery():
    input_params = {
        "designVendorName": "aurora",
        "designID": "c3d3b460-6892-42a9-88b4-8fe648c378ee",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "hour",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_start_simulation_detailed_input_designVendorName_failure():
    input_params = {
        "designVendorName": "aurora_1",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_start_simulation_detailed_input_tenantID_failure():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_start_simulation_detailed_input_designID_failure():
    input_params = {
        "designVendorName": "aurora",
        "designID": "",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


def test_start_simulation_detailed_input_simulationMode_failure():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


def test_start_simulation_detailed_input_simulationYears_failure():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 3,
        "outputResolution": "year",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_start_simulation_detailed_input_outputResolution_failure():
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


def test_start_simulation_detailed_pysam_execute_exception():
    input_params = {
        "designVendorName": "aurora",
        "designID": "87257921-37d6-4648-bfb6-9fec0583dbca",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json()["responses"]["400"]["description"] == "Bad Request"


def test_start_simulation_detailed_pysam_execute_exceptionII():
    input_params = {
        "designVendorName": "aurora",
        "designID": "25bf9591-96c5-4642-ba5f-035dd357821c",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["responses"]["400"]["content"]["detail"]
        == "Multiple MPPT input (arrays) with multiple inverters is not"
        " supported in SAM."
    )


def test_simulation_job_failure(mock_auth_function):

    mock_token = "mockedtoken"
    input_params = {
        "designVendorName": "aurora",
        "designID": "50bb22b9-e598-4dad-b311-2063e64f77fb",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    try:
        response = client.post(
            api_endpoint_detailed,
            json=input_params,
            headers={"Authorization": "Bearer mock_token"},
        )

    except HTTPException as http_err:
        assert http_err.status_code == 500

    except Exception as err:
        pytest.fail(f"Unexpected error occurred: {err}")


def test_start_simulation_detailed_exception(mock_auth_function, mocker):

    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    with mocker.patch(
        "app.api.routes.simulation_job_management.Validator.UUID_Generator",
        side_effect=AttributeError("Attribute Error"),
    ):
        try:
            response = client.post(
                api_endpoint_detailed,
                json=input_params,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        except HTTPException as http_err:
            assert http_err.status_code == 500

        except Exception as err:
            pytest.fail(f"Unexpected error occurred: {err}")


def test_start_simulation_detailed_pvsim_execute_exception(mock_auth_function):
    input_params = {
        "designVendorName": "aurora",
        "designID": "87257921-37d6-4648-bfb6-9fec0583dbca",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 400


def test_start_simulation_detailed_pvsim_execute_exceptionII(
    mock_auth_function,
):
    input_params = {
        "designVendorName": "aurora",
        "designID": "25bf9591-96c5-4642-ba5f-035dd357821c",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }

    response = client.post(
        api_endpoint_detailed,
        json=input_params,
        headers={"Authorization": f"Bearer mockedtoken"},
    )
    assert response.status_code == 400


def test_start_simulation_detailed_execute_failure(mocker):
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "month",
    }
    with mocker.patch(
        "app.api.routes.simulation_job_management.PySAM_PVSim.execute",
        side_effect=AttributeError("Attribute Error in pv execute"),
    ):
        response = run_simulation_detailed(
            input_params=PVSimInput(**input_params),
            Authorization=f"Bearer {access_token}",
        )
        assert response.status_code == 400


def test_start_simulation_detailed_exception(mock_auth_function, mocker):
    input_params = {
        "designVendorName": "aurora",
        "designID": "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
        "tenantID": "a466c0e1-30b3-4062-aeb7-3712491907c1",
        "simulationMode": "MODE_PV",
        "simulationYears": 1,
        "outputResolution": "year",
    }
    with mocker.patch(
        "app.api.routes.simulation_job_management.Validator.UUID_Generator",
        side_effect=Exception("Test exception"),
    ):
        try:
            response = client.post(
                api_endpoint_detailed,
                json=input_params,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        except HTTPException as http_err:
            assert http_err.status_code == 500

        except Exception as err:
            pytest.fail(f"Unexpected error occurred: {err}")
