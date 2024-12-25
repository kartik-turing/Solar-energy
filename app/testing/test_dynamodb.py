import pytest

from app.api.models import PVSimInput
from app.models.dynamodb_orms import JobDetailsTable


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.models.dynamodb_orms.logger")


def test_table_setup_override(mocker, mock_logger):
    mock_create = mocker.patch.object(JobDetailsTable, "create_table")
    mock_create.return_value = None
    JobDetailsTable.create_new_table()
    mock_logger.info.assert_called_once()


def test_drop_table(mocker, mock_logger):
    mock_delete = mocker.patch.object(JobDetailsTable, "delete_table")
    mock_delete.return_value = True
    JobDetailsTable.drop_table()
    mock_logger.info.assert_called_once()


def test_get_all_items(mocker, mock_logger):
    mock_get_all = mocker.patch.object(JobDetailsTable, "scan")

    class Test:
        def __init__(self):
            self.simulationJobId = "id"
            self.Value = "Value"

    mock_get_all.return_value = {Test(): Test()}
    JobDetailsTable.get_all_items()
    assert mock_logger.info.called_once()


def test_get_item_by_id(mocker, mock_logger):
    class Item:
        def __init__(self):
            self.attribute_values = None

    mock_get = mocker.patch.object(JobDetailsTable, "get")
    mock_get.return_value = Item()
    JobDetailsTable.get_item_by_id("id")
    mock_logger.info.assert_called_once()


def test_write_data(mocker, mock_logger):
    api_input = PVSimInput(
        designVendorName="test-name",
        designID="test_design",
        tenantID="test_tenant",
        simulationMode="pv",
        outputResolution="hour",
        simulationYears=1,
    )
    simulation_params = {
        "start_time": 0.0,
        "endtime": 0.0,
        "estimatedSimulationTime": 0.0,
        "actualSimulatioTime": 0.0,
    }
    job_response = {
        "description": "Successful Response",
        "content": {"simulationJobId": "job_id"},
    }
    mock_save = mocker.patch.object(JobDetailsTable, "save")
    mock_save.return_value = "saved_success"
    JobDetailsTable.write_data(
        job_response=job_response,
        simulation_params=simulation_params,
        api_input=api_input,
    )
    mock_logger.info.assert_called_once_with(
        f"Item with JobId job_id added successfully"
    )
