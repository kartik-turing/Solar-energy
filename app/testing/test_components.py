import os

import pytest
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.api.main import app2
from app.api.routes import components_management
from app.models.models import Battery, Inverter, Module
from app.models.schemas import BatteryTable, InverterTable, ModuleTable

load_dotenv("app/config/.env")
client = TestClient(app2)
api_base_url = os.getenv("SERVER_URL")


@pytest.fixture
def mock_session(mocker):
    return mocker.patch("app.models.models.session", autospec=True)


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.models.models.Logging", autospec=True)


inverters_dict = {
    "id": "test_inverter_table",
    "inv_tdc_cec_db": "test_cec_db",
    "inv_snl_eff_cec": 0,
}
modules_dict = {
    "id": "test_module_table",
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
    "id": "test-battery",
}


def assertions_module(response):
    assert (
        "mod_length" in response
        and "cec_bifacial_transmission_factor" in response
        and "cec_bifacial_ground_clearance_height" in response
        and "cec_height" in response
        and "cec_bifaciality" in response
        and "mod_width" in response
        and "id" in response
        and "cec_standoff" in response
        and "cec_transient_thermal_model_unit_mass" in response
    )


def assertions_inverter(response):
    assert (
        "id" in response
        and "inv_tdc_cec_db" in response
        and "inv_snl_eff_cec" in response
    )


def assertions_battery(response):
    assert (
        "id" in response
        and "en_batt" in response
        and "batt_ac_dc_efficiency" in response
        and "batt_dc_ac_efficiency" in response
        and "batt_dc_dc_efficiency" in response
        and "batt_ac_or_dc" in response
        and "batt_computed_bank_capacity" in response
        and "batt_power_charge_max_kwdc" in response
        and "batt_power_charge_max_kwac" in response
        and "batt_power_discharge_max_kwdc" in response
        and "batt_power_discharge_max_kwac" in response
        and "batt_meter_position" in response
        and "batt_computed_series" in response
        and "batt_computed_strings" in response
        and "batt_surface_area" in response
        and "batt_mass" in response
        and "batt_current_charge_max" in response
        and "batt_current_discharge_max" in response
        and "batt_replacement_capacity" in response
        and "batt_replacement_option" in response
        and "batt_inverter_efficiency_cutoff" in response
        and "batt_current_choice" in response
    )


def raise_exception():
    raise Exception("Error in components apis")


def raise_ValueError():
    raise ValueError("Error in input validation")


@pytest.fixture
def mock_verify_token(mocker):
    mocker.patch("app.auth.verify_token", return_value={"sub": "testuser"})


mock_token = "mockedtoken"


def test_patch_module_by_id(mock_verify_token):
    module_id = "Q.PEAK DUO BLK ML-G10+ 410"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    params = {}
    response = client.patch(
        api_endpoint,
        json=params,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 200
    assertions_module(
        response=response.json()["content"]["ModuleComponentResponse"]
    )


def test_get_modules(mock_verify_token):
    api_endpoint = f"/simulation/resi/v1/modules"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 200
    assertions_module(
        response=response.json()["content"]["items"][
            "ModuleComponentResponse"
        ][0]
    )


def test_get_modules_empty_result(mock_verify_token):
    Module.get_all = lambda: []
    api_endpoint = f"/simulation/resi/v1/modules"
    response = client.get(
        api_endpoint, headers={"Authorization": f"Bearer mocked"}
    )
    assert response.status_code == 404
    assert response.json()["responses"]["404"]["detail"] == "Modules Not found"


def test_get_modules_exception(mock_verify_token):
    Module.get_all = lambda: raise_exception()
    api_endpoint = f"/simulation/resi/v1/modules"
    response = client.get(
        api_endpoint, headers={"Authorization": f"Bearer mocked"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_add_module(mock_verify_token):
    mock_token = "mockedtoken"
    api_endpoint = f"/simulation/resi/v1/modules"
    response = client.put(
        api_endpoint,
        json=modules_dict,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 200
    assertions_module(
        response=response.json()["content"]["ModuleComponentResponse"]
    )


def test_add_module_exception(mock_verify_token):
    api_endpoint = "/simulation/resi/v1/modules"
    module = ModuleTable(**modules_dict)
    Module.addModule = lambda module: raise_exception()
    response = client.put(
        api_endpoint,
        json=modules_dict,
        headers={"Authorization": f"Bearer mock_token"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_get_module_by_id(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "Q.PEAK DUO BLK ML-G10+ 400"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Successful Response"


def test_get_module_by_id_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "Q.PEAK DUO BLK ML-G10+ 400"

    Module.get_component = lambda module_id: []
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Module {module_id} Not found"
    )


def test_get_module_by_id_exception(mock_verify_token):
    module_id = "Q.PEAK DUO BLK ML-G10+ 400"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    Module.get_component = lambda module_id: raise_exception()
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer mock_token"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_patch_module_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    Module.get_component = lambda module_id: []
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Module {module_id} Not found"
    )


def test_patch_module_validation_error(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "test_module_table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    Module.update = lambda modules_dict, module_id: raise_ValueError()
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 422
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_delete_module_by_id(mock_verify_token):
    module_id = "test_module_table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Successful Response"


def test_delete_module_by_id_Not_found(mock_verify_token):
    module_id = "moduleid"
    Module.delete = lambda module_id: []
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Module {module_id} Not found"
    )


def test_delete_module_by_id_exception(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "moduleid"
    Module.delete = lambda module_id: raise_exception()
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_patch_inverter_by_id(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "Q.VOLT H7.6SX"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    params = {}
    response = client.patch(
        api_endpoint,
        json=params,
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    assertions_inverter(
        response=response.json()["content"]["ModuleComponentResponse"]
    )


def test_get_inverters(mock_verify_token):

    mock_token = "mockedtoken"
    api_endpoint = f"/simulation/resi/v1/inverters"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 200
    assertions_inverter(
        response=response.json()["content"]["items"][
            "InverterComponentResponse"
        ][0]
    )


def test_get_inverters_empty_data(mock_verify_token, mocker):
    with mocker.patch(
        "app.api.routes.components_management.Inverter.get_all",
        return_value=[],
    ):
        response = components_management.get_inverters(Authorization="mock")
        assert response.status_code == 404


def test_get_inverters_exception(mock_verify_token, mocker):
    with mocker.patch(
        "app.api.routes.components_management.Inverter.get_all",
        side_effect=Exception("Test exception"),
    ):
        try:
            components_management.get_inverters(Authorization="mock")
        except HTTPException as http_err:
            assert http_err.status_code == 500


def test_add_inverter(mock_verify_token):
    api_url = f"/simulation/resi/v1/inverters"
    response = client.put(
        api_url,
        json=inverters_dict,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 200
    assertions_inverter(
        response=response.json()["content"]["InverterComponentResponse"]
    )


def test_add_inverter_exception(mock_verify_token, mocker):
    with mocker.patch(
        "app.api.routes.components_management.jsonable_encoder",
        side_effect=Exception("Test exception"),
    ):
        try:
            components_management.add_inverter(
                inverter_data=InverterTable(**inverters_dict),
                Authorization="mock",
            )
        except HTTPException as http_err:
            assert http_err.status_code == 500


def test_add_battery_exception(mock_verify_token, mocker):
    with mocker.patch(
        "app.api.routes.components_management.jsonable_encoder",
        side_effect=Exception("Test exception"),
    ):
        try:
            components_management.add_battery(
                battery_data=BatteryTable(**battery_dict), Authorization="mock"
            )
        except HTTPException as http_err:
            assert http_err.status_code == 500


def test_get_inverter_by_id(mock_verify_token):
    inverter_id = "Q.VOLT H7.6SX"
    api_url = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.get(
        api_url,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Successful Response"


def test_get_inverter_by_id_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "Q.PEAK DUO BLK ML-G10+ 400"

    Inverter.get_component = lambda inverter_id: []
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Inverter {inverter_id} Not found"
    )


def test_get_inverter_by_id_exception(mock_verify_token):
    inverter_id = "Q.PEAK DUO BLK ML-G10+ 400"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    Inverter.get_component = lambda inverter_id: raise_exception()
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer mock_token"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_patch_inverter_by_id(mock_verify_token):
    inverter_id = "IQ8PLUS-72-2-US"
    api_url = f"/simulation/resi/v1/inverters/{inverter_id}"
    params = {
        "inv_tdc_cec_db": "[[1500, 50, -0.02, 53, -0.47]]",
        "inv_snl_eff_cec": 97.046,
    }
    response = client.patch(
        api_url,
        json=params,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 200
    assertions_inverter(
        response=response.json()["content"]["InverterComponentResponse"]
    )


def test_patch_module_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    module_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    Module.get_component = lambda module_id: []
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Module {module_id} Not found"
    )


def test_patch_module_validation_error(mock_verify_token, mocker):
    mock_token = "mockedtoken"
    module_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    mocker.patch(
        "app.api.routes.components_management.Module.get_component",
        side_effect=ValueError("ValueError"),
    )
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 422
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_patch_module_exception(mock_verify_token, mocker):
    mock_token = "mockedtoken"
    module_id = "test_module_table"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"
    mocker.patch(
        "app.api.routes.components_management.Module.get_component",
        side_effect=Exception("Exception"),
    )
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_patch_inverter_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    Inverter.get_component = lambda inverter_id: []
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Inverter {inverter_id} Not found"
    )


def test_patch_inverter_validation_error(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    Inverter.update = lambda inverters_dict, inverter_id: raise_ValueError()
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 422
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_patch_inverter_exception(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "test_inverter_table"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    Inverter.update = lambda inverters_dict, inverter_id: raise_exception()
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def delete_inverter_by_id(mock_verify_token):
    inverter_id = "delete-test-fail-id"
    api_url = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.delete(
        api_url,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Inverter {inverter_id} Not found"
    )


def test_delete_inverter_by_id_Not_found(mock_verify_token):
    inverter_id = "inverterid"
    Inverter.delete = lambda inverter_id: []
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Inverter {inverter_id} Not found"
    )


def test_delete_inverter_by_id_exception(mock_verify_token):
    mock_token = "mockedtoken"
    inverter_id = "inverterid"
    Inverter.delete = lambda inverter_id: raise_exception()
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_get_batteries(mock_verify_token):
    api_url = f"/simulation/resi/v1/batteries"
    response = client.get(
        api_url,
        headers={"Authorization": "Bearer mockedtoken"},
    )
    assert response.status_code == 200
    assertions_battery(
        response=response.json()["content"]["items"][
            "BatteryComponentResponse"
        ][0]
    )


def test_get_battery_empty_result(mock_verify_token):
    Battery.get_all = lambda: []
    api_endpoint = f"/simulation/resi/v1/batteries"
    response = client.get(
        api_endpoint, headers={"Authorization": "Bearer mocked"}
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"] == "Batteries Not found"
    )


def test_get_battery_exception(mock_verify_token):
    Battery.get_all = lambda: raise_exception()
    api_endpoint = f"/simulation/resi/v1/batteries"
    response = client.get(
        api_endpoint, headers={"Authorization": f"Bearer mocked"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_add_battery(mock_verify_token):
    mock_token = "mockedtoken"
    api_endpoint = f"/simulation/resi/v1/batteries"
    response = client.put(
        api_endpoint,
        json=battery_dict,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 200
    assertions_battery(
        response=response.json()["content"]["BatteryComponentResponse"]
    )


def test_get_battery_by_id(mock_verify_token):
    battery_id = "AC_Powerwall 3"
    api_url = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.get(
        api_url,
        headers={
            "Authorization": "Bearer mockedtoken",
        },
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Successful Response"


def test_get_battery_by_id_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    battery_id = "Q.PEAK DUO BLK ML-G10+ 400"

    Battery.get_component = lambda battery_id: []
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Battery {battery_id} Not found"
    )


def test_get_battery_by_id_exception(mock_verify_token):
    battery_id = "Q.PEAK DUO BLK ML-G10+ 400"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    Battery.get_component = lambda battery_id: raise_exception()
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer mock_token"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_patch_battery_empty_result(mock_verify_token):
    mock_token = "mockedtoken"
    battery_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    Battery.get_component = lambda battery_id: []
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 404
    assert (
        response.json()["responses"]["404"]["detail"]
        == f"Battery {battery_id} Not found"
    )


def test_patch_battery_validation_error(mock_verify_token):
    mock_token = "mockedtoken"
    battery_id = "test-table"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    Battery.update = lambda battery_dict, battery_id: raise_ValueError()
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 422
    assert (
        response.json()["responses"]["422"]["description"]
        == "Validation Error"
    )


def test_patch_battery_exception(mock_verify_token):
    mock_token = "mockedtoken"
    battery_id = "test_battery_table"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    Battery.update = lambda battery_dict, battery_id: raise_exception()
    response = client.patch(
        api_endpoint,
        json={},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_delete_battery_by_id(mock_verify_token):
    battery_id = "test-battery"
    api_url = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.delete(
        api_url,
        headers={
            "Authorization": "Bearer mockedtoken",
        },
    )
    assert response.status_code == 200


def test_delete_battery_by_id_err(mock_verify_token, mocker):
    mocker.patch(
        "app.api.routes.components_management.Battery.delete", return_value=[]
    )
    battery_id = "not-found-battery"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 404


def test_delete_battery_by_id_exception(mock_verify_token):
    mock_token = "mockedtoken"
    battery_id = "batteryid"
    Battery.delete = lambda battery_id: raise_exception()
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.delete(
        api_endpoint,
        headers={
            "Authorization": "Bearer mock_token",
        },
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_get_module_by_id_fault_tolerant(mock_verify_token):
    module_id = "test_module_id"
    api_endpoint = f"/simulation/resi/v1/modules/{module_id}"

    response = client.get(
        api_endpoint,
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 404


def test_get_inverter_by_id_fault_tolerant(mock_verify_token):
    inverter_id = "test_inverter_id"
    api_endpoint = f"/simulation/resi/v1/inverters/{inverter_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 404


def test_get_battery_by_id_fault_tolerant(mock_verify_token):
    battery_id = "test_battery_id"
    api_endpoint = f"/simulation/resi/v1/batteries/{battery_id}"
    response = client.get(
        api_endpoint,
        headers={"Authorization": f"Bearer token"},
    )

    assert response.status_code == 404
