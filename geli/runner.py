import logging

from geli.aurora_solar_sim_api import AuroraSolarSim_API
from geli.pysam_batteries import PySAM_Batteries
from geli.pysam_inverters import PySAM_Inverters
from geli.pysam_lifetime import PySAM_Lifetime
from geli.pysam_modules import PySAM_Modules
from geli.pysam_solar_resources import PySAM_Solar_Resources
from geli.pysam_system_design import PySAM_SystemDesign


class Runner:
    """Class for running a simulation"""

    def __init__(
        self,
        design_id: str,
        base_url: str,
        tenant_id: str,
        token: str,
        sam_api_key: str,
        sam_email: str,
        technology: str,
        simulationYears: int,
        annualDegradation: list,
        include_system_design: bool,
        include_modules: bool,
        include_inverters: bool,
        include_batteries: bool,
    ):
        self._include_system_design = include_system_design
        self._include_modules = include_modules
        self._include_batteries = include_batteries
        self._include_inverters = include_inverters
        # TODO: EXTENSION FEATURE: add api to access info from other vendoers
        self.aurora_api = AuroraSolarSim_API(
            base_url=base_url,
            tenant_id=tenant_id,
            token=token,
            design_id=design_id,
        )

        if technology == "solar":
            self.solar_resources = PySAM_Solar_Resources(
                sam_api_key, sam_email
            )

            self.solar_resources.get_nsrdbfetcher().fetch(
                list([self.aurora_api.get_lat_lon_tuple()])
            )
            self.solar_resources.set_resource_file_paths()

        if self._include_modules:
	        self.modules = PySAM_Modules(
	                    self.aurora_api.get_module_name(),
	                    self.aurora_api.get_module_quantity(),
	                )

        if self._include_inverters:
	        self.inverters = PySAM_Inverters(
	                    self.aurora_api.get_inverter_name(),
	                    self.aurora_api.get_string_inv_quantity(),
	                )

        if self._include_batteries:
	        self.battery = PySAM_Batteries(
	                    self.aurora_api.get_batteries_id(),
	                    self.aurora_api.get_batteries_quantity(),
	                    self.aurora_api.get_batteries_name(),
	                    self.aurora_api.get_inverter_name(),
	                    self.aurora_api.get_inverter_type(),
	                    self.aurora_api.get_storage_inverters_dict(),
	                    self.aurora_api.get_dc_optimizers_quantity(),
	                    self.aurora_api.get_num_arrays(),
	                )
	
        

        if self._include_system_design:
            # LIMITATION: PySAM cannot handle more than 4 arrays
            if self.aurora_api.get_num_arrays() > 4:
                raise ValueError("Design cannot exceed more than four arrays.")
            self.system_design = PySAM_SystemDesign(
                self.aurora_api.get_design_id(),
                self.aurora_api.get_string_inv_quantity(),
            )
            for array_num, array in enumerate(
                self.aurora_api.get_array_list()
            ):
                self.system_design.create_subarray_dict(
                    idx=array_num,
                    array=array,
                    enable=True,
                    inverter_type=self.aurora_api.get_inverter_type(),
                    inverter_count=self.aurora_api.get_inverter_count(),
                    num_arrays=self.aurora_api.get_num_arrays(),
                    string_inv_qty=self.aurora_api.get_string_inv_quantity(),
                )
                self.system_design.create_layout_dict(array_num, array)
                self.system_design.create_shading_dict(
                    array_num, array, self.aurora_api.get_component_type()
                )
                self.system_design.create_losses_dict(
                    array_num, array, self.aurora_api.get_component_type()
                )

            # disable all remaining arrays
            for idx in range(self.aurora_api.get_num_arrays(), 4):
                self.system_design.create_subarray_dict(
                    idx=idx,
                    array=None,
                    enable=False,
                    inverter_type=self.aurora_api.get_inverter_type(),
                    inverter_count=self.aurora_api.get_inverter_count(),
                    num_arrays=self.aurora_api.get_num_arrays(),
                    string_inv_qty=self.aurora_api.get_string_inv_quantity(),
                )

        # life-time
        self.lifetime = PySAM_Lifetime(simulationYears, annualDegradation)