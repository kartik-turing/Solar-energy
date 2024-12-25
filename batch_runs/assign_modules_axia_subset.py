import os

import pandas
import pytest

from geli.api_models import PVSimInputII
from geli.aurora_solar_sim_api import AuroraSolarSim_API
from geli.pysam_pvsim import PySAM_PVSim

AXIA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"

AXIA_DESIGN_IDS = list()
axia_ids_with_component_failure = list()

with open("component_error_log_AXIAsubset", "r") as f:
    for line in f.read().splitlines():
        axia_ids_with_component_failure.append(line.split(";")[0])

with open("batch_runs/async_api_first_iteration.csv", "r") as f:
    for line in f.read().splitlines():
        if line.startswith("design"):
            continue
        design_id = line.split(",")[0]
        if design_id not in axia_ids_with_component_failure:
            AXIA_DESIGN_IDS.append(design_id)


@pytest.mark.parametrize("ids", AXIA_DESIGN_IDS)
def test_assignment(ids):
    pvsim = PySAM_PVSim.testing_constructor(
        designVendorName="AXIA",
        designID=ids,
        tenantID=AXIA_TENANT_ID,
        siteID=None,
        simulationMode=None,
        simulationYears=None,
        outputResolution=None,
        test_without_utility_rates=True,
        test_without_subarrays=True,
    )
    pvsim.create_module_dict()
    pvsim.set_module_assignment_status(status=-1)
    pvsim.assign_modules()
    assert pvsim.get_module_assignment_status() == 1
