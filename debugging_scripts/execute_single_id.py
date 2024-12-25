from geli.pysam_pvsim import PySAM_PVSim
from sys import argv

AXIA_TENANT_ID = "a466c0e1-30b3-4062-aeb7-3712491907c1"
ENFIN_TENANT_ID = "3707373c-739c-485c-8f21-ee03dda36cef"


def test():
    pvsim = PySAM_PVSim(
        designVendorName=vendorName,
        designID=ids,
        tenantID=tenantID,
        simulationMode=None,
        simulationYears=simulationYears,
        outputResolution=None,
    )
    try:
        pvsim.pv.execute()
        status = 1
    except Exception as exception:
        status = 0
        error_message = f"{exception}".splitlines()[:2]
        error_message[1] = error_message[1].lstrip()

    assert status == 1, " ".join(error_message)

    print(pvsim.pv.Outputs.monthly_energy)


if __name__ == "__main__":
    ids = argv[1]
    vendorName = argv[2]
    simulationYears = int(argv[3]) if len(argv) == 4 else 1
    tenantID = AXIA_TENANT_ID if vendorName == "AXIA" else ENFIN_TENANT_ID
    test()
