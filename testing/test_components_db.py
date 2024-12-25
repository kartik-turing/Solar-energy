import pytest

from geli.aurora_components_db import (
    AuroraBatteryDatabase,
    AuroraInverterDatabase,
    AuroraModuleDatabase,
)

modules_table = list([
    {
        "name": "Q.PEAK DUO BLK ML-G10+ 400",
        "mod_length": 1.879,
        "mod_width": 1.045,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 2,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
    },
    {
        "name": "Q.PEAK DUO BLK ML-G10+ 405",
        "mod_length": 1.879,
        "mod_width": 1.045,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 2,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
    },
    {
        "name": "Q.PEAK DUO BLK ML-G10+ 410",
        "mod_length": 1.879,
        "mod_width": 1.045,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 2,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
    },
    {
        "name": "Q.TRON BLK M-G2+ 425",
        "mod_length": 1.722,
        "mod_width": 1.134,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 1,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
    },
    {
        "name": "REC400NP3 Black",
        "mod_length": 1.900,
        "mod_width": 1.040,
        "cec_bifacial_transmission_factor": 0,
        "cec_bifaciality": 0,
        "cec_bifacial_ground_clearance_height": 1,
        "cec_standoff": 6,
        "cec_height": 0,
        "cec_transient_thermal_model_unit_mass": 11.092,
    },
])


@pytest.mark.parametrize("module", modules_table)
def test_module_assigned_parameters(module):
    module_rds = AuroraModuleDatabase(module["name"], 0)
    assert (
        module_rds.module_name == module["name"]
        and module_rds.mod_length == module["mod_length"]
        and module_rds.mod_width == module["mod_width"]
        and module_rds.cec_bifacial_transmission_factor
        == module["cec_bifacial_transmission_factor"]
        and module_rds.cec_bifaciality == module["cec_bifaciality"]
        and module_rds.cec_standoff == module["cec_standoff"]
        and module_rds.cec_height == module["cec_height"]
        and module_rds.cec_transient_thermal_model_unit_mass
        == module["cec_transient_thermal_model_unit_mass"]
        and module_rds.cec_bifacial_ground_clearance_height
        == module["cec_bifacial_ground_clearance_height"]
    )


inverters_table = list([
    {
        "name": "Q.VOLT H7.6SX",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.491,
    },
    {
        "name": "IQ8PLUS-72-2-US",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.046,
    },
    {
        "name": "IQ8A-72-2-US",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.491,
    },
    {
        "name": "IQ8A-72-M-US",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.491,
    },
    {
        "name": "Powerwall 3 (integrated inverter)",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.491,
    },
    {
        "name": "IQ8M-72-2-US",
        "inv_tdc_cec_db": [[1500, 50, -0.02, 53, -0.47]],
        "inv_snl_eff_cec": 97.491,
    },
])


@pytest.mark.parametrize("inverter", inverters_table)
def test_inverter_assigned_parameters(inverter):
    inverter_rds = AuroraInverterDatabase(inverter["name"], 0)
    assert (
        inverter_rds.inverter_name == inverter["name"]
        and inverter_rds.inv_tdc_cec_db == inverter["inv_tdc_cec_db"]
        and inverter_rds.inv_snl_eff_cec == inverter["inv_snl_eff_cec"]
    )


batteries_table = {
    "Microinverters/Dc Optimizers": {
        "Storage Inverter": {
            "Powerwall 3": (
                1,
                97,
                97,
                97.3,
                1,
                13.389300000000002,
                4.8103023169805521,
                4.9590000000000005,
                5.1122942758068293,
                4.9590000000000005,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                46.075692691384596,
                48.968335975161196,
                50,
                0,
                90,
                1,
            ),
            "ENCHARGE-10-1P-NA": (
                1,
                96,
                96,
                99,
                1,
                10.100700000000002,
                3.7138223236649983,
                3.8478857142857148,
                3.9867885913272536,
                3.8478857142857148,
                0,
                29,
                43,
                0.75755250000000018,
                144.2957142857143,
                35.573010763074691,
                38.187630185126949,
                50,
                0,
                90,
                1,
            ),
        },
        "Q.VOLT H7.6SX": {
            "Q.SAVE D10.0SX": (
                1,
                96,
                96,
                99,
                1,
                8.9262000000000015,
                7.2437898240000003,
                7.5456144000000007,
                7.8600150000000006,
                7.5456144000000007,
                0,
                29,
                38,
                0.6694650000000002,
                127.51714285714287,
                69.384960000000007,
                75.287499999999994,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D15.0SX": (
                1,
                96,
                96,
                99,
                1,
                13.389300000000002,
                7.2437898239999994,
                7.5456143999999998,
                7.8600149999999998,
                7.5456143999999998,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                69.384959999999992,
                75.287499999999994,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D20.0SX": (
                1,
                96,
                96,
                99,
                1,
                18.087299999999999,
                7.3391028479999987,
                7.6448987999999991,
                7.9634362499999991,
                7.6448987999999991,
                0,
                29,
                77,
                1.3565474999999998,
                258.38999999999999,
                70.297919999999976,
                76.278124999999989,
                50,
                0,
                90,
                1,
            ),
        },
        "Q.VOLT H3.8SX": {
            "Q.SAVE D10.0SX": (
                1,
                96,
                96,
                99,
                1,
                8.9262000000000015,
                3.6333204480000005,
                3.7847088000000007,
                3.9424050000000008,
                3.7847088000000007,
                0,
                29,
                38,
                0.6694650000000002,
                127.51714285714287,
                34.801920000000003,
                37.762500000000003,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D15.0SX": (
                1,
                96,
                96,
                99,
                1,
                13.389300000000002,
                3.6333204480000005,
                3.7847088000000007,
                3.9424050000000008,
                3.7847088000000007,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                34.801920000000003,
                37.762500000000003,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D20.0SX": (
                1,
                96,
                96,
                99,
                1,
                18.087299999999999,
                3.6811272959999997,
                3.8345075999999998,
                3.9942787499999999,
                3.8345075999999998,
                0,
                29,
                77,
                1.3565474999999998,
                258.38999999999999,
                35.259839999999997,
                38.259374999999999,
                50,
                0,
                90,
                1.0,
            ),
        },
    },
    "Inverters": {
        "Storage Inverter": {
            "Powerwall 3": (
                1,
                97,
                97,
                97.3,
                0,
                13.389300000000002,
                4.8103023169805521,
                4.9590000000000005,
                5.1122942758068293,
                4.9590000000000005,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                46.075692691384596,
                48.968335975161196,
                50,
                0,
                90,
                1,
            )
        },
        "Q.VOLT H7.6SX": {
            "Q.SAVE D10.0SX": (
                1,
                96,
                96,
                99,
                0,
                8.9262000000000015,
                7.2827192087460455,
                7.5456144000000007,
                7.8179997115789925,
                7.5456144000000007,
                0,
                29,
                38,
                0.6694650000000002,
                127.51714285714287,
                69.7578468270694,
                74.885054708611037,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D15.0SX": (
                1,
                96,
                96,
                99,
                0,
                13.389300000000002,
                7.2827192087460446,
                7.5456143999999998,
                7.8179997115789917,
                7.5456143999999998,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                69.757846827069386,
                74.885054708611037,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D20.0SX": (
                1,
                96,
                96,
                99,
                0,
                18.087299999999999,
                7.3785444614927025,
                7.6448987999999991,
                7.9208681288366085,
                7.6448987999999991,
                0,
                29,
                77,
                1.3565474999999998,
                258.38999999999999,
                70.675713232688722,
                75.870384375829587,
                50,
                0,
                90,
                1,
            ),
        },
        "Q.VOLT H3.8SX": {
            "Q.SAVE D10.0SX": (
                1,
                96,
                96,
                99,
                0,
                8.9262000000000015,
                3.6528465431880801,
                3.7847088000000007,
                3.9213310856184855,
                3.7847088000000007,
                0,
                29,
                38,
                0.6694650000000002,
                127.51714285714287,
                34.801920000000003,
                37.762500000000003,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D15.0SX": (
                1,
                96,
                96,
                99,
                0,
                13.389300000000002,
                3.6528465431880801,
                3.7847088000000007,
                3.9213310856184855,
                3.7847088000000007,
                0,
                29,
                57,
                1.0041975,
                191.27571428571432,
                34.988951563104216,
                37.560642582552546,
                50,
                0,
                90,
                1,
            ),
            "Q.SAVE D20.0SX": (
                1,
                96,
                96,
                99,
                0,
                18.087299999999999,
                3.7009103134931856,
                3.8345075999999998,
                3.9729275472713592,
                3.8345075999999998,
                0,
                29,
                77,
                1.3565474999999998,
                258.38999999999999,
                35.449332504723998,
                38.054861563901909,
                50,
                0,
                90,
                1,
            ),
        },
    },
}


@pytest.mark.parametrize("battery_key", batteries_table.keys())
def test_battery_assigned_parameters(battery_key):
    for storage_inv_name, battery_dict in batteries_table[battery_key].items():
        for battery_name, battery in battery_dict.items():
            inverter_type = (
                "microinverters"
                if battery_key == "Microinverters/Dc Optimizers"
                else "inverters"
            )
            battery_rds = AuroraBatteryDatabase(
                battery_name,
                1,
                "",
                inverter_type,
                {"name": storage_inv_name},
                "",
                1,
            )
            assert (
                battery_rds.en_batt == battery[0]
                and battery_rds.batt_ac_dc_efficiency == battery[1]
                and battery_rds.batt_dc_ac_efficiency == battery[2]
                and battery_rds.batt_dc_dc_efficiency == battery[3]
                and battery_rds.batt_ac_or_dc == battery[4]
                and battery_rds.batt_computed_bank_capacity == battery[5]
                and battery_rds.batt_power_charge_max_kwdc == battery[6]
                and battery_rds.batt_power_charge_max_kwac == battery[7]
                and battery_rds.batt_power_discharge_max_kwdc == battery[8]
                and battery_rds.batt_power_discharge_max_kwac == battery[9]
                and battery_rds.batt_meter_position == battery[10]
                and battery_rds.batt_computed_series == battery[11]
                and battery_rds.batt_computed_strings == battery[12]
                and battery_rds.batt_surface_area == battery[13]
                and battery_rds.batt_mass == battery[14]
                and battery_rds.batt_current_charge_max == battery[15]
                and battery_rds.batt_current_discharge_max == battery[16]
                and battery_rds.batt_replacement_capacity == battery[17]
                and battery_rds.batt_replacement_option == battery[18]
                and battery_rds.batt_inverter_efficiency_cutoff == battery[19]
                and battery_rds.batt_current_choice == battery[20]
            )
