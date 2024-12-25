import os
import logging
import pandas as pd
import pytest
from geli.pysam_pvsim import PySAM_PVSim

AXIA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"
ENFIN_TENANT_ID = "3707373c-739c-485c-8f21-ee03dda36cef"
AXIA_DESIGN_IDS = list()
ENFIN_DESIGN_IDS = list()
axia_ids_with_component_failure = list()

with open("component_error_log_AXIAsubset", "r") as f:
    for line in f.read().splitlines():
        axia_ids_with_component_failure.append(line.split(";")[0])

file_path_list = ["AXIA_design_ids.csv"]

battery_assign_logs = "batteries_assign_logs.txt"

for filepath in file_path_list:
    with open(filepath, "r") as f:
        for line in f.read().splitlines():
            if line.startswith("design"):
                continue
            design_id = line.split(",")[0]
            if "AXIA" in filepath and design_id not in axia_ids_with_component_failure:
                AXIA_DESIGN_IDS.append(design_id)
            elif "ENFIN" in filepath and design_id not in axia_ids_with_component_failure:
                ENFIN_DESIGN_IDS.append(design_id)


@pytest.mark.parametrize("ids", AXIA_DESIGN_IDS)
def test_assignment(ids):
    log_file_path = f"log_{ids}.txt"

    #test_without_system_design=True
    pvsim = PySAM_PVSim.testing_constructor(
        designVendorName="AXIA" if ids in AXIA_DESIGN_IDS else "ENFIN",
        designID=ids,
        tenantID=AXIA_TENANT_ID if ids in AXIA_DESIGN_IDS else ENFIN_TENANT_ID,
        siteID=None,
        simulationMode=None,
        simulationYears=None,
        outputResolution=None,
        test_without_utility_rates=True,
        test_without_system_design=True,
        test_without_modules=True,
        test_without_inverters=True,
        test_without_batteries=False
    )

    pvsim.create_battery_system_dict()
    pvsim.create_battery_cell_dict()
    pvsim.create_battery_dispatch_dict()
    pvsim.set_battery_system_assignment_status(status=-1)
    pvsim.set_battery_cell_assignment_status(status=-1)
    pvsim.set_battery_dispatch_assignment_status(status=-1)

    try:
        pvsim.assign_battery_system()
        pvsim.assign_battery_cell()
        pvsim.assign_battery_dispatch()

        assert pvsim.get_battery_system_assignment_status() == 1
        assert pvsim.get_battery_cell_assignment_status() == 1
        assert pvsim.get_battery_dispatch_assignment_status() == 1
        with open("battery_assign_logs",mode='a') as f:
            f.write(f"Battery Assigned Successfully \n")

    except Exception as e:
        print(f"Error occurred: {e}")
        with open("battery_assign_logs",mode='a') as f:
            f.write(f"Battery assignment failure error: {e}")