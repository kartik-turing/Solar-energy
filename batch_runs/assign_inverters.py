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

file_path_list = ["batch_runs/AXIA_design_ids.csv", "batch_runs/ENFIN_design_ids.csv"]
for filepath in file_path_list:
    if "AXIA" in filepath:
        with open(filepath, "r") as f:
            for line in f.read().splitlines():
                if line.startswith("design"):
                    continue
                design_id = line.split(",")[0]
                AXIA_DESIGN_IDS.append(design_id)
    if "ENFIN" in filepath:
        with open(filepath, "r") as f:
            for line in f.read().splitlines():
                if line.startswith("design"):
                    continue
                design_id = line.split(",")[0]
                ENFIN_DESIGN_IDS.append(design_id)




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
        test_without_modules=True,
        test_without_batteries = True,
    )
    pvsim.create_inverter_dict()
    pvsim.set_inverter_assignment_status(status=-1)
    pvsim.assign_inverters()
    assert pvsim.get_inverter_assignment_status() == 1


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
        test_without_modules=True,
        test_without_batteries = True,
    )
    pvsim.create_inverter_dict()
    pvsim.set_inverter_assignment_status(status=-1)
    pvsim.assign_inverters()
    assert pvsim.get_inverter_assignment_status() == 1
