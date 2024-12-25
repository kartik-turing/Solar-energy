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
def test_aurora_solar_api_axia(ids):
    api = AuroraSolarSim_API(
        PVSimInputII.AURORA_BASE_URL,
        AXIA_TENANT_ID,
        PVSimInputII.AURORA_TOKENS["AXIA"],
        ids,
    )


@pytest.mark.parametrize("ids", ENFIN_DESIGN_IDS)
def test_aurora_solar_api_enfin(ids):
    api = AuroraSolarSim_API(
        PVSimInputII.AURORA_BASE_URL,
        ENFIN_TENANT_ID,
        PVSimInputII.AURORA_TOKENS["ENFIN"],
        ids,
    )
