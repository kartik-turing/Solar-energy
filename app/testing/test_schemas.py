import pytest
from pydantic import ValidationError

from app.models.schemas import InverterTable, ModuleTable


def test_module_table():
    mod = ModuleTable(
        id="test",
        mod_length=0.0,
        mod_width=0.0,
        cec_bifacial_transmission_factor=0,
        cec_bifaciality=0,
        cec_bifacial_ground_clearance_height=0,
        cec_standoff=0,
        cec_height=0,
        cec_transient_thermal_model_unit_mass=0.0,
        annual_degradation=[0.0],
    )

    assert mod.id == "test"
    assert mod.mod_length == 0.0
    assert mod.mod_width == 0.0
    assert mod.cec_bifacial_transmission_factor == 0
    assert mod.cec_bifaciality == 0
    assert mod.cec_bifacial_ground_clearance_height == 0
    assert mod.cec_standoff == 0
    assert mod.cec_height == 0
    assert mod.cec_transient_thermal_model_unit_mass == 0.0
    assert mod.annual_degradation == [0.0]


def test_module_table_failure():
    with pytest.raises(ValidationError):
        ModuleTable(
            id=[],
            mod_length=0.0,
            mod_width=0.0,
            cec_bifacial_transmission_factor=0,
            cec_bifaciality=0,
            cec_bifacial_ground_clearance_height=0,
            cec_standoff=0,
            cec_height=0,
            cec_transient_thermal_model_unit_mass=0.0,
        )


def test_inverter_table():
    inverter = InverterTable(
        id="test_inverter", inv_tdc_cec_db="", inv_snl_eff_cec=0.0
    )

    assert inverter.id == "test_inverter"
    assert inverter.inv_tdc_cec_db == ""
    assert inverter.inv_snl_eff_cec == 0.0


def test_inverter_table_failure():
    with pytest.raises(ValidationError):
        InverterTable(
            id="test_inverter", inv_tdc_cec_db=[], inv_snl_eff_cec=0.0
        )
