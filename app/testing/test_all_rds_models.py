import pytest
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError, create_model
from pytest_mock import mocker
from sqlalchemy import select, update
from sqlalchemy.orm import Query

from app.models.models import (
    Battery,
    BatteryTable,
    Inverter,
    InverterTable,
    Module,
    ModuleTable,
)

module = None
inverter = None
battery_system = None
battery_cell = None


class TestTable(BaseModel):
    id: str


@pytest.fixture
def mock_session(mocker):
    return mocker.patch("app.models.models.session", autospec=True)


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.models.models.logger")


@pytest.fixture
def mock_select(mocker):
    return mocker.patch("sqlalchemy.select")


@pytest.fixture
def mock_update(mocker):
    return mocker.patch("sqlalchemy.update")


modules_dict = {
    "id": "test_module_table_new",
    "mod_length": 0.0,
    "mod_width": 0.0,
    "cec_bifacial_transmission_factor": 0,
    "cec_bifaciality": 0,
    "cec_bifacial_ground_clearance_height": 0,
    "cec_standoff": 0,
    "cec_height": 0,
    "cec_transient_thermal_model_unit_mass": 0,
    "annual_degradation": [
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
        0.55,
    ],
}

battery_dict = {
    "en_batt": 0,
    "batt_ac_dc_efficiency": 0,
    "batt_dc_ac_efficiency": 0,
    "batt_dc_dc_efficiency": 0,
    "batt_ac_or_dc": 0,
    "batt_computed_bank_capacity": 0,
    "batt_power_charge_max_kwdc": 0,
    "batt_power_charge_max_kwac": 0,
    "batt_power_discharge_max_kwdc": 0,
    "batt_power_discharge_max_kwac": 0,
    "batt_meter_position": 0,
    "batt_computed_series": 0,
    "batt_computed_strings": 0,
    "batt_surface_area": 0,
    "batt_mass": 0,
    "batt_current_charge_max": 0,
    "batt_current_discharge_max": 0,
    "batt_replacement_capacity": 0,
    "batt_replacement_option": 0,
    "batt_inverter_efficiency_cutoff": 0,
    "batt_current_choice": 0,
    "batt_chem": 0,
    "batt_lifetime_matrix": [[0, 0]],
    "batt_calendar_choice": [0],
    "batt_calendar_q0": [0],
    "batt_calendar_a": [0],
    "batt_calendar_b": 0,
    "batt_calendar_c": 0,
    "batt_voltage_matrix": [[0]],
    "batt_Vfull": 0,
    "batt_Vexp": [0],
    "batt_Vnom_default": [0],
    "batt_Vnom": [0],
    "batt_Vcut": 0,
    "batt_Qfull_flow": 0,
    "batt_Qfull": 0,
    "batt_Qnom": 0,
    "batt_Qexp": 0,
    "batt_C_rate": 0,
    "batt_life_model": 0,
    "batt_initial_SOC": 0,
    "batt_maximum_SOC": 0,
    "batt_minimum_SOC": [0],
    "batt_minimum_outage_SOC": [0],
    "batt_minimum_modetime": 0,
    "batt_resistance": 0,
    "batt_h_to_ambient": [0],
    "batt_Cp": 0,
    "batt_room_temperature_celsius": [0, 0],
    "cap_vs_temp": [[0, 0]],
    "batt_calendar_lifetime_matrix": [[0, 0]],
    "batt_voltage_choice": 0,
    "id": "test-battery-new",
}

inverters_dict = {
    "id": "test_inverter_table_new",
    "inv_tdc_cec_db": "test_cec_db",
    "inv_snl_eff_cec": 0,
}


def test_get_all_success(mock_session, mock_logger, mock_select):
    mock_select.return_value = select(Module)
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        "module_param1",
        "module_param2",
    ]
    results = Module.get_all()

    assert results == ["module_param1", "module_param2"]
    mock_logger.log_info.assert_called_once_with(
        "Get Module Query executed successfully"
    )


def test_get_component_success(mock_logger):
    results = Inverter.get_component("Q.VOLT H7.6SX")
    del results.__dict__["_sa_instance_state"]
    assert results.__dict__ == {
        "inv_snl_eff_cec": 97.491,
        "id": "Q.VOLT H7.6SX",
        "inv_tdc_cec_db": "[[1500, 50, -0.02, 53, -0.47]]",
    }
    mock_logger.log_info.assert_called_once_with(
        "Get Q.VOLT H7.6SX Query executed successfully"
    )


def test_get_component_module_success(mock_logger):
    results = Module.get_component("Q.PEAK DUO BLK ML-G10+ 400")
    del results.__dict__["_sa_instance_state"]

    assert jsonable_encoder(results.__dict__) == {
        "mod_length": 1.879,
        "mod_width": 1.045,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 2,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
        "id": "Q.PEAK DUO BLK ML-G10+ 400",
        "annual_degradation": [
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
            0.55,
        ],
    }
    mock_logger.log_info.assert_called_once_with(
        "Get Q.PEAK DUO BLK ML-G10+ 400 Query executed successfully"
    )


def test_add_module(mock_session, mock_logger):
    module = ModuleTable(**modules_dict)
    Module.addModule(module)
    mock_logger.log_info.assert_called_with(
        "Write test_module_table_new Query executed successfully"
    )
    module.id = "test_module_table"
    Module.addModule(module)
    mock_logger.log_info.assert_called_with(
        "Write test_module_table Query executed successfully"
    )


def test_add_inverter(mock_session, mock_logger):
    inverter = InverterTable(**inverters_dict)
    Inverter.addInverter(inverter)
    mock_logger.log_info.assert_called_with(
        "Write test_inverter_table_new Query executed successfully"
    )
    inverter.id = "test_inverter_table"
    Inverter.addInverter(inverter)
    mock_logger.log_info.assert_called_with(
        "Update test_inverter_table Query executed successfully"
    )


def test_add_battery(mock_session, mock_logger):
    battery = BatteryTable(**battery_dict)
    Battery.addBattery(battery)
    mock_logger.log_info.assert_called_with(
        "Write test-battery-new Query executed successfully"
    )
    battery.id = "test-battery"
    Battery.addBattery(battery)
    mock_logger.log_info.assert_called_with(
        "Write test-battery Query executed successfully"
    )


def test_update_component_success(mock_logger, mock_update):
    mock_update.return_value = update(Module)
    data_dict = {"id": "new module"}
    Model = create_model(
        "DynamicModel", **{k: (str, v) for k, v in data_dict.items()}
    )
    data_dict_model = Model(**data_dict)
    Module.update(data_dict_model, "new module")
    mock_logger.log_info.assert_called_once_with(
        "Update new module Query executed successfully"
    )


def test_update_component_battery_success(mock_session, mock_logger):
    mock_execute = mock_session.execute
    data_dict_model = TestTable(id="test_id")

    Battery.update(data_dict_model, "test_id")
    mock_execute.assert_called_once()
    mock_logger.log_info.assert_called_once_with(
        "Update test_id Query executed successfully"
    )


def test_update_component_exception(mock_session, mock_logger):
    mock_execute = mock_session.execute
    mock_execute.side_effect = Exception("Database error")

    data_dict_model = TestTable(
        id="id",
    )

    with pytest.raises(Exception) as exc:
        Battery.update(data_dict_model, "id")

    mock_logger.log_error.assert_called_once_with(
        f"Error in Update id: Database error"
    )
