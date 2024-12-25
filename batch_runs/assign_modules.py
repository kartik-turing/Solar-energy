import os

import pandas
import pytest

from geli.api_models import PVSimInputII
from geli.aurora_solar_sim_api import AuroraSolarSim_API
from geli.pysam_pvsim import PySAM_PVSim

AXIA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"
ENFIN_TENANT_ID = "3707373c-739c-485c-8f21-ee03dda36cef"

AXIA_DESIGN_IDS = list()
ENFIN_DESIGN_IDS = list()

with open("batch_runs/AXIA_design_ids.csv", "r") as f:
    for line in f.read().splitlines():
        if line.startswith("design"):
            continue
        AXIA_DESIGN_IDS.append(line.split(",")[0])

with open("batch_runs/ENFIN_design_ids.csv", "r") as f:
    for line in f.read().splitlines():
        if line.startswith("design"):
            continue
        ENFIN_DESIGN_IDS.append(line.split(",")[0])

@pytest.mark.parametrize("ids", AXIA_DESIGN_IDS)
def test_AXIA_assignment(ids):
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


@pytest.mark.parametrize("ids", ENFIN_DESIGN_IDS)
def test_ENFIN_assignment(ids):
    pvsim = PySAM_PVSim.testing_constructor(
        designVendorName="ENFIN",
        designID=ids,
        tenantID=ENFIN_TENANT_ID,
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
