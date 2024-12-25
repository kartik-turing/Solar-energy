import pytest
from fastapi.testclient import TestClient

from app.api.routes.job_status import router

client = TestClient(router)

header = {"Authorization": f"Bearer  "}
endpoint = "/simulation/resi/v1/jobstatus"


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch(
        "app.api.routes.job_status.logger.error", autospec=True
    )


def test_job_status_success():
    response = client.get(
        endpoint, params={"simulationJobID": "dc2e12cbf"}, headers=header
    )
    assert response.status_code == 200


def test_job_status_input_validation():
    response = client.get(
        endpoint, params={"simulationJobID": ""}, headers=header
    )
    assert response.status_code == 422


def test_job_status_id_not_found():
    response = client.get(
        endpoint, params={"simulationJobID": "123456789"}, headers=header
    )
    assert response.status_code == 404


def test_internal_server_error(mocker, mock_logger):
    with mocker.patch(
        "re.fullmatch", side_effect=Exception("Internal Server Error")
    ):
        try:
            client.get(
                endpoint, params={"simulationJobID": ""}, headers=header
            )
        except Exception:
            mock_logger.assert_called_once_with(
                "An error occured: Internal Server Error"
            )
