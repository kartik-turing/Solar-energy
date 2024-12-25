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
        AXIA_DESIGN_IDS.append(line.split(",")[0])


@pytest.mark.parametrize("ids", AXIA_DESIGN_IDS)
def test_aurora_solar_api_axia(ids):
    api = AuroraSolarSim_API(
        PVSimInputII.AURORA_BASE_URL,
        AXIA_TENANT_ID,
        PVSimInputII.AURORA_TOKENS["AXIA"],
        ids,
    )
