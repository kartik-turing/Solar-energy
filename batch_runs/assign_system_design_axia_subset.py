import os

import pandas
import pytest

from geli.api_models import PVSimInputII
from geli.aurora_solar_sim_api import AuroraSolarSim_API
from geli.pysam_pvsim import PySAM_PVSim

AXIA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"

AXIA_DESIGN_IDS = list()

with open("batch_runs/async_api_first_iteration.csv", "r") as f:
    for line in f.read().splitlines():
        if line.startswith("design"):
            continue
        design_id = line.split(",")[0]
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
        test_without_subarrays=False,
        test_without_modules=False,
        test_without_batteries=True,
    )
    pvsim.create_module_dict()
    pvsim.set_module_assignment_status(status=-1)
    pvsim.assign_modules()
    pvsim.create_system_design_dict()
    pvsim.set_system_design_assignment_status(status=-1)
    pvsim.assign_system_design()
    assert pvsim.get_system_design_assignment_status() == 1
