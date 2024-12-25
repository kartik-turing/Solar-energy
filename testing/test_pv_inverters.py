import pytest

from geli.pysam_inverters import PySAM_Inverters

module_id = "fb249b44-ac5c-4da5-9a86-cb0ac8fb8bf5"
module_quantity = 1  # this is incorrect, since bill of materials shows it as 2
module_name = "Q.VOLT H7.6SX"

skip_reason = "PySAM_Inverters failed to instantiate"

pysam_inverters = None
try:
    pysam_inverters = PySAM_Inverters(module_name, module_quantity)
except Exception as exception:
    print("INSTANTIATION FAILURE: CANNOT INSTANTIATE PySAM_Inverters OBJECT")
    print(exception)


def test_instantiation():
    assert pysam_inverters is not None


@pytest.mark.skipif(pysam_inverters is None, reason=skip_reason)
def test_pysam_modules_specsheet_url():
    assert (
        pysam_inverters.get_mod_specsheet_url()
        == "https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Inverters.csv"
    )


@pytest.mark.skipif(pysam_inverters is None, reason=skip_reason)
def test_pysam_modules_specsheet():
    import pandas

    assert isinstance(
        pysam_inverters.get_pysam_module_specsheet(),
        type(pandas.DataFrame()),
    )


@pytest.mark.skipif(pysam_inverters is None, reason=skip_reason)
def test_get_module():
    assert pysam_inverters.get_module() is not None
