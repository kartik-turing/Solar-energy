import os
import pathlib
import sys

import pytest

from geli.pysam_pvsim import PySAM_PVSim

AURORA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"
design_id = "2bf548f4-b6ff-4b91-8fa1-74cc33d4d474"

skip_reason = "PySAM_PVSim failed to instantiate"

# ensure weather data is downloading correctly
weather_data_csv = (
    f"{os.getcwd()}/data/PySAM Downloaded Weather"
    " Files/nsrdb_37.845403_-122.255993_psm3-tmy_60_tmy.csv"
)
weather_data_json = (
    f"{os.getcwd()}/data/PySAM Downloaded Weather"
    " Files/nsrdb_data_query_response_37.845403_-122.255993.json"
)

# need to modify below code for platform specific naming conventions
# if sys.platform == "win32":
#    pass
# elif sys.platform == "macos"

# remove weather data files
if pathlib.Path(weather_data_csv).is_file():
    os.remove(weather_data_csv)
if pathlib.Path(weather_data_csv).is_file():
    os.remove(weather_data_json)

pvsim = None

try:
    pvsim = PySAM_PVSim(
        designVendorName="AURORA",
        designID=design_id,
        tenantID=AURORA_TENANT_ID,
        simulationMode=None,
        simulationYears=3,
        outputResolution=None,
    )
except Exception as exception:
    print("INSTANTIATION FAILURE: CANNOT INSTANTIATE PySAM_PVSim OBJECT")
    print(exception)


def test_pvsim_instantiation():
    assert pvsim is not None


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_albedo_definition():
    assert len(pvsim.get_albedo()) == 12


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_solar_resource_path():
    import pathlib

    path = pvsim.runner.solar_resources.get_resource_file_paths()[
        pvsim.runner.aurora_api.get_lat_lon_tuple()
    ]
    assert pathlib.Path(path).is_file()


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_solar_resource_assignment():
    assert pvsim.get_solar_resource_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_module_assignment():
    assert pvsim.get_module_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_inverter_assignment():
    assert pvsim.get_inverter_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_system_design_assignment():
    assert pvsim.get_system_design_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_layout_assignment():
    assert pvsim.get_layout_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_shading_assignment():
    assert pvsim.get_shading_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_losses_assignment():
    assert pvsim.get_losses_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_battery_system_assignment():
    assert pvsim.get_battery_system_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_battery_cell_assignment():
    assert pvsim.get_battery_cell_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_battery_dispatch_assignment():
    assert pvsim.get_battery_dispatch_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_lifetime_applies_default_ac_degradation_with_compounding():
    pvsim.runner.lifetime.set_ac_degradation([0.55 / 100] * 3, True)
    if pvsim.runner.lifetime.simulation_uses_ac_degradation():
        assert (
            sum(pvsim.runner.lifetime.get_yearly_ac_degradation())
            - sum([1.0, 0.9945, 0.98903025])
            < 1e-3
        )
    else:
        assert (
            False
        ), "Not implemented test for simulation_uses_dc_degradation case"


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_lifetime_applies_default_ac_degradation_without_compounding():
    pvsim.runner.lifetime.set_ac_degradation([0.55 / 100] * 3)
    if pvsim.runner.lifetime.simulation_uses_ac_degradation():
        assert (
            sum(pvsim.runner.lifetime.get_yearly_ac_degradation())
            - sum([1.0, 0.9945, 0.9890])
            < 1e-3
        )
    else:
        assert (
            False
        ), "Not implemented test for simulation_uses_dc_degradation case"


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_lifetime_default_dc_degradation_if_using_ac_degradation():
    if pvsim.runner.lifetime.simulation_uses_ac_degradation():
        assert sum(pvsim.runner.lifetime.get_yearly_dc_degradation()) == 0
    else:
        assert (
            False
        ), "Not implemented test for simulation_uses_dc_degradation case"


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_lifetime_uses_ac_degradation():
    assert pvsim.runner.lifetime.get_system_use_lifetime_output() == 0


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_lifetime_assignment():
    assert pvsim.get_lifetime_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_load_assignment():
    assert pvsim.get_load_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_price_signal_assignment():
    assert pvsim.get_price_signal_assignment_status() == 1


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_execute():
    pvsim.execute()
    assert True


@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_allyears_energy_production_for_assigned_ac_degradation():
    if pvsim.runner.lifetime.simulation_uses_ac_degradation():
        testValues = [
            i * pvsim.pv.Outputs.annual_energy
            for i in pvsim.runner.lifetime.get_yearly_ac_degradation()
        ]
        assert (
            abs(
                sum(pvsim.get_energy_generation_for_all_years())
                - sum(testValues)
            )
            < 1e-3
        )
    else:
        assert (
            False
        ), "Not implemented test for simulation_uses_dc_degradation case"

@pytest.mark.skipif(pvsim is None, reason=skip_reason)
def test_pvsim_allyears_allmonths_energy_production_for_assigned_ac_degradation():
    if pvsim.runner.lifetime.simulation_uses_ac_degradation():
        pvsim.execute()
        assert (
            abs(
                sum(pvsim.get_energy_generation_for_all_years())
                - sum(pvsim.get_energy_generation_for_all_months_in_all_years())
            )
            < 1e-3
        )
    else:
        assert (
            False
        ), "Not implemented test for simulation_uses_dc_degradation case"
