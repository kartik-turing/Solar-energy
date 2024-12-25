from geli.aurora_components_db import AuroraBatteryDatabase


class PySAM_Batteries(AuroraBatteryDatabase):
    def __init__(
        self,
        module_id,
        module_quantity,
        module_name,
        inverter_name,
        inverter_type,
        storage_inverter,
        dc_optimizer,
        num_arrays,
    ):

        super().__init__(
            module_name,
            module_quantity,
            inverter_name,
            inverter_type,
            storage_inverter,
            dc_optimizer,
            num_arrays,
        )
