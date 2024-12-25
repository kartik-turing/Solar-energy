import pytest

from geli.pysam_modules import PySAM_Modules

module_id = "a2c87d21-f101-4405-91e8-f61994d1ac1e"
module_quantity = 13
module_name = "Q.PEAK DUO BLK ML-G10+ 405"

skip_reason = "PySAM_Modules failed to instantiate"

pysam_modules = None
try:
    pysam_modules = PySAM_Modules(module_name, module_quantity)
except Exception as exception:
    print("INSTANTIATION FAILURE: CANNOT INSTANTIATE PySAM_Modules OBJECT")
    print(exception)


def test_modules_instantiation():
    assert pysam_modules is not None


def test_pysam_modules_specsheet_url():
    assert (
        pysam_modules.get_mod_specsheet_url()
        == "https://raw.githubusercontent.com/NREL/SAM/master/deploy/libraries/CEC%20Modules.csv"
    )


@pytest.mark.skipif(pysam_modules is None, reason=skip_reason)
def test_pysam_modules_specsheet():
    import pandas

    assert isinstance(
        pysam_modules.get_pysam_module_specsheet(), type(pandas.DataFrame())
    )


@pytest.mark.skipif(pysam_modules is None, reason=skip_reason)
def test_get_module():
    assert pysam_modules.get_module() is not None
