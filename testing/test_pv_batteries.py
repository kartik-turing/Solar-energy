import pytest

from geli.pysam_batteries import PySAM_Batteries
from geli.runner import Runner

runner_axia = Runner(
    design_id="2bf548f4-b6ff-4b91-8fa1-74cc33d4d474",
    base_url="https://api.aurorasolar.com",
    tenant_id="a466c0e1-30b3-4062-aeb7-3712491907c1",
    token="rk_prod_b293db1019e44f33ce389c9f",
    sam_api_key="6KZH3sWJYqNraJmwfEoka2oBtcAbXPo8JKfXrUwh",
    sam_email="jackson.herron@qcells.com",
    technology="solar",
    simulationYears=1,
    annualDegradation=list([0.55 / 100]),
    include_system_design=True,
    include_modules=True,
    include_batteries=True,
    include_inverters=True,
)

runner_enfin = Runner(
    design_id="c16cada1-df7e-4c9b-b876-c9cbc5db9d1e",
    base_url="https://api.aurorasolar.com",
    tenant_id="3707373c-739c-485c-8f21-ee03dda36cef",
    token="rk_prod_73546d8cd47b650481b8eeef",
    sam_api_key="6KZH3sWJYqNraJmwfEoka2oBtcAbXPo8JKfXrUwh",
    sam_email="jackson.herron@qcells.com",
    technology="solar",
    simulationYears=1,
    annualDegradation=list([0.55 / 100]),
    include_system_design=True,
    include_modules=True,
    include_batteries=True,
    include_inverters=True,
)

enfin_design_ids = list([
    "c16cada1-df7e-4c9b-b876-c9cbc5db9d1e",
    "26a61768-b82d-442e-ad6d-7f5931c8909f",
    "c3df837a-f299-44a5-acc4-33d33cb83752",
    "accc6945-6ee1-4c78-bfaa-675406c3ed8e",
    "0a5cc9ce-ba44-43aa-b195-29b9ae0fbc51",
    "db9055c3-82a9-4a04-aca2-7e2594f029bf",
    "568ce939-7e09-4167-9daf-2667f87d6a00",
])

designs_without_batteries = list([
    "c16cada1-df7e-4c9b-b876-c9cbc5db9d1e",
    "26a61768-b82d-442e-ad6d-7f5931c8909f",
    "c3df837a-f299-44a5-acc4-33d33cb83752",
    "accc6945-6ee1-4c78-bfaa-675406c3ed8e",
    "f6f6d736-f7fb-4ffb-a3e2-e279e7263757",
    "f554642d-d7ea-4ad0-87de-9221244adf3e",
    "1de37db5-456d-4f47-9be2-55cac6a18f8a",
    "25bf9591-96c5-4642-ba5f-035dd357821c",
    "b524257d-ef29-468f-9f01-18d73fe1c69e",
    "ecac942a-1636-4ac4-8061-e99bfec67087",
    "26fcbcd0-3be2-4d5d-a2e3-69f30619a181",
    "8fce7746-e089-41ff-9f77-9567da4369c7",
    "9898255d-acd7-40c0-9fe4-ad6839467e8e",
    "44667b7e-f555-40ca-98f5-05c31966ed23",
    "2bf6db10-4b75-4d0c-beb0-809443beafe8",
])

designs_with_dc_optimizers = list([
    "fac30f9c-c9e4-4143-aa25-938e5e1b86bc",
    "164456d4-19d7-4eba-b8e8-59a48be2f499",
])

# below design also has inverter_type = "inverters" which is expected to
# be dc coupled but powerwall 3 integrated inverter is expected to be
# ac coupled - not sure which is the overarching behaviour to be used.
# Currently treating inverter_type = "inverters" as the overarching
# behaviour.
designs_with_powerwall3_integrated_inverter = list([
    "0a5cc9ce-ba44-43aa-b195-29b9ae0fbc51",
])

designs_with_encharge10_battery = list([
    "61493b87-ddfb-4f14-abd5-65c9df63bd92",
])

designs_with_microinverter = list([
    "db9055c3-82a9-4a04-aca2-7e2594f029bf",
    "568ce939-7e09-4167-9daf-2667f87d6a00",
    "91a956b0-7d0e-4f7e-abab-a903c8663f4e",
    "8c1a3c30-af3d-468c-a37a-a8aecd03df2c",
    "a42c7d2c-d2ba-4e5f-961b-d0ba405bdafa",
])

designs_with_inverters = list([
    "28c4be9a-d545-47e7-b717-3eb26ff21647",
    "a31e147c-9600-4a0e-972d-aa4a842fd4b1",
    "19284338-e057-42be-8c17-11d0baaafc6f",
    "c3d3b460-6892-42a9-88b4-8fe648c378ee",
    "2bf548f4-b6ff-4b91-8fa1-74cc33d4d474",
    "ba4bfbce-48d6-43f5-a524-12af33e5c4d0",
])

ac_enabled_designs = (
    designs_with_dc_optimizers
    # + designs_with_powerwall3_integrated_inverter
    + designs_with_encharge10_battery
    + designs_with_microinverter
)

dc_enabled_designs = (
    designs_with_inverters + designs_with_powerwall3_integrated_inverter
)

all_design_types = (
    designs_without_batteries + ac_enabled_designs + dc_enabled_designs
)


def instantiate_battery(runner):
    return PySAM_Batteries(
        runner.aurora_api.get_batteries_id(),
        runner.aurora_api.get_batteries_quantity(),
        runner.aurora_api.get_batteries_name(),
        runner.aurora_api.get_inverter_name(),
        runner.aurora_api.get_inverter_type(),
        runner.aurora_api.get_storage_inverters_dict(),
        runner.aurora_api.get_dc_optimizers_quantity(),
        runner.aurora_api.get_num_arrays(),
    )


@pytest.mark.parametrize("design_id", all_design_types)
def test_instantiation(design_id):
    """Test instantiation."""
    runner = runner_enfin if design_id in enfin_design_ids else runner_axia
    pysam_batteries = None
    runner.aurora_api.update(design_id)
    pysam_batteries = instantiate_battery(runner)
    assert pysam_batteries is not None


@pytest.mark.parametrize("design_id", ac_enabled_designs)
def test_ac_enabled(design_id):
    """Test if configuration is AC/DC coupled."""
    runner = runner_enfin if design_id in enfin_design_ids else runner_axia
    pysam_batteries = None
    runner.aurora_api.update(design_id)
    pysam_batteries = instantiate_battery(runner)
    # value should be 1
    assert pysam_batteries.batt_ac_or_dc == 1


@pytest.mark.parametrize("design_id", dc_enabled_designs)
def test_dc_enabled(design_id):
    """Test if configuration is AC/DC coupled."""
    runner = runner_enfin if design_id in enfin_design_ids else runner_axia
    pysam_batteries = None
    runner.aurora_api.update(design_id)
    pysam_batteries = instantiate_battery(runner)
    # value should be 0 except when num_arrays > 1
    value = 1 if runner.aurora_api.get_num_arrays() > 1 else 0
    assert pysam_batteries.batt_ac_or_dc == value
