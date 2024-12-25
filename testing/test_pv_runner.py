import pytest

from geli.runner import Runner

AURORA_BASE_URL = "https://api.aurorasolar.com"
AURORA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"
AURORA_TOKEN = "rk_prod_b293db1019e44f33ce389c9f"

SAM_API_KEY = "6KZH3sWJYqNraJmwfEoka2oBtcAbXPo8JKfXrUwh"
SAM_EMAIL = "jackson.herron@qcells.com"

design_id = "2bf548f4-b6ff-4b91-8fa1-74cc33d4d474"

simulationYears = 3

skip_reason = "Runner failed to instantiate"


runner = None
try:
    runner = Runner(
        design_id=design_id,
        base_url=AURORA_BASE_URL,
        tenant_id=AURORA_TENANT_ID,
        token=AURORA_TOKEN,
        sam_api_key=SAM_API_KEY,
        sam_email=SAM_EMAIL,
        technology="solar",
        simulationYears=simulationYears,
        annualDegradation=[0.55 / 100] * simulationYears,
        include_system_design=True,
        include_modules=True,
        include_batteries=True,
        include_inverters=True,
    )
except Exception as exception:
    print("INSTANTIATION FAILURE: CANNOT INSTANTIATE Runner OBJECT")
    print(exception)


def test_runner_instantiation():
    assert runner is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_aurora_get_design_summary():
    assert runner.aurora_api.get_design_summary() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_aurora_get_project_summary():
    assert runner.aurora_api.get_project_summary() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_aurora_get_latitude():
    assert runner.aurora_api.get_latitude() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_aurora_get_longitude():
    assert runner.aurora_api.get_longitude() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_nsrdb_resource_file_paths():
    assert runner.solar_resources.get_resource_file_paths() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_modules_dict():
    assert runner.aurora_api.get_modules_dict() is not None


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_module_id():
    assert (
        runner.aurora_api.get_module_id()
        == "a2c87d21-f101-4405-91e8-f61994d1ac1e"
    )


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_module_quantity():
    assert runner.aurora_api.get_module_quantity() == 13


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_batteries_dict():
    batteries_dict = runner.aurora_api.get_batteries_dict()
    assert batteries_dict["id"] == "67fceeef-3ef6-44de-8e3c-3a21ff385b25"


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_inverters_dict():
    inverters_dict = runner.aurora_api.get_inverters_dict()
    assert inverters_dict["id"] == "fb249b44-ac5c-4da5-9a86-cb0ac8fb8bf5"


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_address():
    address = runner.aurora_api.get_address()
    assert address == "5826 Colby St, Oakland, CA 94618, USA"


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_get_utility_name():
    name = runner.aurora_api.get_utility_name()
    assert name == "Pacific Gas & Electric Co"


@pytest.mark.skipif(runner is None, reason=skip_reason)
def test_runner_lifetime():
    assert runner.lifetime is not None
