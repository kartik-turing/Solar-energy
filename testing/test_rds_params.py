import importlib
import os

import pytest

known_inverters = list([
    "Q.VOLT H7.6SX",
    "Powerwall 3 (integrated inverter)",
    "IQ8PLUS-72-2-US",
    "IQ8M-72-2-US",
    "IQ8A-72-2-US",
    "IQ8A-72-M-US",
])


@pytest.mark.parametrize("inverter", known_inverters)
def test_inverter_assigned_parameters(inverter):
    os.environ["custom"] = "in-memory"
    from geli.pysam_inverters import PySAM_Inverters

    inverter_in_memory = PySAM_Inverters(inverter, 0)

    os.environ["custom"] = "rds"
    importlib.reload(importlib.import_module("geli.pysam_inverters"))

    from geli.pysam_inverters import PySAM_Inverters

    inverter_rds = PySAM_Inverters(inverter, 0)

    assert (
        inverter_in_memory.inv_tdc_cec_db == inverter_rds.inv_tdc_cec_db
        and inverter_in_memory.inv_snl_eff_cec == inverter_rds.inv_snl_eff_cec
        and inverter_in_memory.inverter_name == inverter_rds.inverter_name
    )


known_modules = list([
    "Q.PEAK DUO BLK ML-G10+ 400",
    "Q.PEAK DUO BLK ML-G10+ 405",
    "Q.PEAK DUO BLK ML-G10+ 410",
    "Q.TRON BLK M-G2+ 425",
    "REC400NP3 Black",
])


@pytest.mark.parametrize("module", known_modules)
def test_module_assigned_parameters(module):
    os.environ["custom"] = "in-memory"
    from geli.pysam_modules import PySAM_Modules

    module_in_memory = PySAM_Modules(module, 0)

    os.environ["custom"] = "rds"
    importlib.reload(importlib.import_module("geli.pysam_modules"))

    from geli.pysam_modules import PySAM_Modules

    module_rds = PySAM_Modules(module, 0)

    assert (
        module_in_memory.mod_length == module_rds.mod_length
        and module_in_memory.mod_width == module_rds.mod_width
        and module_in_memory.cec_bifacial_transmission_factor
        == module_rds.cec_bifacial_transmission_factor
        and module_in_memory.cec_bifaciality == module_rds.cec_bifaciality
        and module_in_memory.cec_standoff == module_rds.cec_standoff
        and module_in_memory.cec_height == module_rds.cec_height
        and module_in_memory.cec_transient_thermal_model_unit_mass
        == module_rds.cec_transient_thermal_model_unit_mass
        and module_in_memory.cec_bifacial_ground_clearance_height
        == module_rds.cec_bifacial_ground_clearance_height
    )


known_batteries = [
    ["microinverters", "Storage Inverter", "Powerwall 3"],
    ["microinverters", "Storage Inverter", "ENCHARGE-10-1P-NA"],
    ["microinverters", "Q.VOLT H7.6SX", "Q.SAVE D10.0SX"],
    ["microinverters", "Q.VOLT H7.6SX", "Q.SAVE D15.0SX"],
    ["microinverters", "Q.VOLT H7.6SX", "Q.SAVE D20.0SX"],
    ["microinverters", "Q.VOLT H3.8SX", "Q.SAVE D10.0SX"],
    ["microinverters", "Q.VOLT H3.8SX", "Q.SAVE D15.0SX"],
    ["microinverters", "Q.VOLT H3.8SX", "Q.SAVE D20.0SX"],
    ["inverters", "Storage Inverter", "Powerwall 3"],
    ["inverters", "Q.VOLT H7.6SX", "ENCHARGE-10-1P-NA"],
    ["inverters", "Q.VOLT H7.6SX", "Q.SAVE D10.0SX"],
    ["inverters", "Q.VOLT H7.6SX", "Q.SAVE D15.0SX"],
    ["inverters", "Q.VOLT H7.6SX", "Q.SAVE D20.0SX"],
    ["inverters", "Q.VOLT H3.8SX", "Q.SAVE D10.0SX"],
    ["inverters", "Q.VOLT H3.8SX", "Q.SAVE D15.0SX"],
    ["inverters", "Q.VOLT H3.8SX", "Q.SAVE D20.0SX"],
]


@pytest.mark.parametrize("battery", known_batteries)
def test_battery_assigned_parameters(battery):
    os.environ["custom"] = "in-memory"
    from geli.pysam_batteries import PySAM_Batteries

    module_in_memory = PySAM_Batteries(
        module_id="test",
        module_quantity=1,
        module_name=battery[2],
        inverter_name=battery[1],
        inverter_type=battery[0],
        storage_inverter={"name": battery[1]},
        dc_optimizer="",
        num_arrays=0,
    )

    os.environ["custom"] = "rds"
    importlib.reload(importlib.import_module("geli.pysam_batteries"))

    from geli.pysam_batteries import PySAM_Batteries

    module_rds = PySAM_Batteries(
        module_id="test",
        module_quantity=1,
        module_name=battery[2],
        inverter_name=battery[1],
        inverter_type=battery[0],
        storage_inverter={"name": battery[1]},
        dc_optimizer="",
        num_arrays=0,
    )

    # module_in_memory.en_batt == module_rds.en_batt
    assert (
        module_in_memory.batt_ac_dc_efficiency
        == int(module_rds.batt_ac_dc_efficiency)
        and module_in_memory.batt_dc_ac_efficiency
        == module_rds.batt_dc_ac_efficiency
        and module_in_memory.batt_dc_dc_efficiency
        == module_rds.batt_dc_dc_efficiency
        and module_in_memory.batt_ac_or_dc == module_rds.batt_ac_or_dc
        and module_in_memory.batt_computed_bank_capacity
        == module_rds.batt_computed_bank_capacity
        and module_in_memory.batt_power_charge_max_kwdc
        == module_rds.batt_power_charge_max_kwdc
        and module_in_memory.batt_power_charge_max_kwac
        == module_rds.batt_power_charge_max_kwac
        and module_in_memory.batt_power_discharge_max_kwdc
        == module_rds.batt_power_discharge_max_kwdc
        and module_in_memory.batt_power_discharge_max_kwac
        == module_rds.batt_power_discharge_max_kwac
        and module_in_memory.batt_meter_position
        == module_rds.batt_meter_position
        and module_in_memory.batt_computed_series
        == module_rds.batt_computed_series
        and module_in_memory.batt_computed_strings
        == module_rds.batt_computed_strings
        and module_in_memory.batt_surface_area == module_rds.batt_surface_area
        and module_in_memory.batt_mass == module_rds.batt_mass
        and module_in_memory.batt_current_charge_max
        == module_rds.batt_current_charge_max
        and module_in_memory.batt_current_discharge_max
        == module_rds.batt_current_discharge_max
        and module_in_memory.batt_replacement_capacity
        == module_rds.batt_replacement_capacity
        and module_in_memory.batt_replacement_option
        == module_rds.batt_replacement_option
        and module_in_memory.batt_inverter_efficiency_cutoff
        == module_rds.batt_inverter_efficiency_cutoff
        and module_in_memory.batt_current_choice
        == module_rds.batt_current_choice
        and module_in_memory.batt_chem == module_rds.batt_chem
        and module_in_memory.batt_lifetime_matrix
        == module_rds.batt_lifetime_matrix
        and module_in_memory.batt_calendar_choice
        == module_rds.batt_calendar_choice
        and module_in_memory.batt_calendar_q0 == module_rds.batt_calendar_q0
        and module_in_memory.batt_calendar_a == module_rds.batt_calendar_a
        and module_in_memory.batt_calendar_b == module_rds.batt_calendar_b
        and module_in_memory.batt_calendar_c == module_rds.batt_calendar_c
        and module_in_memory.batt_voltage_matrix
        == module_rds.batt_voltage_matrix
        and module_in_memory.batt_Vfull == module_rds.batt_Vfull
        and module_in_memory.batt_Vexp == module_rds.batt_Vexp
        and module_in_memory.batt_Vnom_default == module_rds.batt_Vnom_default
        and module_in_memory.batt_Vnom == module_rds.batt_Vnom
        and module_in_memory.batt_Vcut == module_rds.batt_Vcut
        and module_in_memory.batt_Qfull_flow == module_rds.batt_Qfull_flow
        and module_in_memory.batt_Qfull == module_rds.batt_Qfull
        and module_in_memory.batt_Qnom == module_rds.batt_Qnom
        and module_in_memory.batt_Qexp == module_rds.batt_Qexp
        and module_in_memory.batt_C_rate == module_rds.batt_C_rate
        and module_in_memory.batt_life_model == module_rds.batt_life_model
        and module_in_memory.batt_initial_SOC == module_rds.batt_initial_SOC
        and module_in_memory.batt_maximum_SOC == module_rds.batt_maximum_SOC
        and module_in_memory.batt_minimum_SOC == module_rds.batt_minimum_SOC
        and module_in_memory.batt_minimum_outage_SOC
        == module_rds.batt_minimum_outage_SOC
        and module_in_memory.batt_minimum_modetime
        == module_rds.batt_minimum_modetime
        and module_in_memory.batt_resistance == module_rds.batt_resistance
        and module_in_memory.batt_h_to_ambient == module_rds.batt_h_to_ambient
        and module_in_memory.batt_Cp == module_rds.batt_Cp
        and module_in_memory.batt_room_temperature_celsius
        == module_rds.batt_room_temperature_celsius
        and module_in_memory.cap_vs_temp == module_rds.cap_vs_temp
        and module_in_memory.batt_calendar_lifetime_matrix
        == module_rds.batt_calendar_lifetime_matrix
        and module_in_memory.batt_voltage_choice
        == module_rds.batt_voltage_choice
        and module_in_memory.batt_dispatch_choice
        == module_rds.batt_dispatch_choice
        and module_in_memory.batt_dispatch_auto_btm_can_discharge_to_grid
        == module_rds.batt_dispatch_auto_btm_can_discharge_to_grid
        and module_in_memory.batt_dispatch_auto_can_gridcharge
        == module_rds.batt_dispatch_auto_can_gridcharge
        and module_in_memory.batt_dispatch_charge_only_system_exceeds_load
        == module_rds.batt_dispatch_charge_only_system_exceeds_load
        and module_in_memory.batt_dispatch_discharge_only_load_exceeds_system
        == module_rds.batt_dispatch_discharge_only_load_exceeds_system
        and module_in_memory.batt_cycle_cost_choice
        == module_rds.batt_cycle_cost_choice
        and module_in_memory.batt_cycle_cost == module_rds.batt_cycle_cost
    )
