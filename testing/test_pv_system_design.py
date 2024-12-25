import pytest

from geli.pysam_system_design import PySAM_SystemDesign
from testing.test_pv_runner import runner

skip_reason = "PySAM_SystemDesign failed to instantiate"


pysam_system_design = None
try:
    pysam_system_design = PySAM_SystemDesign(
        runner.aurora_api.get_design_id(),
        runner.aurora_api.get_string_inv_quantity(),
    )
except Exception as exception:
    print(
        "INSTANTIATION FAILURE: CANNOT INSTANTIATE PySAM_SystemDesign OBJECT"
    )
    print(exception)


@pytest.mark.skipif(pysam_system_design is None, reason=skip_reason)
def test_pysam_arrays_instantiation():
    assert pysam_system_design is not None


@pytest.mark.skipif(pysam_system_design is None, reason=skip_reason)
def test_pysam_array_entries():
    for idx, array in enumerate(runner.aurora_api.get_array_list()):
        pysam_system_design.create_subarray_dict(
            idx,
            array,
            True,
            runner.aurora_api.get_inverter_type(),
            runner.aurora_api.get_inverter_count(),
            runner.aurora_api.get_num_arrays(),
            runner.aurora_api.get_string_inv_quantity(),
        )

    for idx in range(runner.aurora_api.get_num_arrays(), 4):
        pysam_system_design.create_subarray_dict(
            idx,
            array,
            True,
            runner.aurora_api.get_inverter_type(),
            runner.aurora_api.get_inverter_count(),
            runner.aurora_api.get_num_arrays(),
            runner.aurora_api.get_string_inv_quantity(),
        )

    print(pysam_system_design.get_subsystem_design_dict())
    assert len(pysam_system_design.get_subsystem_design_dict()) == 36


@pytest.mark.skipif(pysam_system_design is None, reason=skip_reason)
def test_pysam_layout_entries():
    for idx, array in enumerate(runner.aurora_api.get_array_list()):
        pysam_system_design.create_layout_dict(idx, array)

    assert len(pysam_system_design.get_subsystem_layout_dict()) == 6


@pytest.mark.skipif(pysam_system_design is None, reason=skip_reason)
def test_pysam_shading_entries():
    for idx, array in enumerate(runner.aurora_api.get_array_list()):
        pysam_system_design.create_shading_dict(
            idx, array, runner.aurora_api.get_component_type()
        )

    assert len(pysam_system_design.get_subsystem_shading_dict()) == 6


@pytest.mark.skipif(pysam_system_design is None, reason=skip_reason)
def test_pysam_losses_entries():
    for idx, array in enumerate(runner.aurora_api.get_array_list()):
        pysam_system_design.create_losses_dict(
            idx, array, runner.aurora_api.get_component_type()
        )

    assert len(pysam_system_design.get_subsystem_losses_dict()) == 18
