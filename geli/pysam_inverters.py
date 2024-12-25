from geli.aurora_components_db import AuroraInverterDatabase


class PySAM_Inverters(AuroraInverterDatabase):
    def __init__(
        self,
        inverter_name,
        string_inv_quantity,
        specsheet_url=None,
    ):
        self._mod_url = self.set_mod_specsheet_url(
            url=specsheet_url, mod="inverters"
        )
        self.inverter_name = inverter_name
        self._pysam_mod_specsheet = self.set_pysam_module_specsheet()
        self._string_inv_qty = string_inv_quantity

        super().__init__(inverter_name, string_inv_quantity)

        self.check_if_module_in_pysam_library(inverter_name, "Inverter")

        self.set_module_parameters()

    def get_num_mppt_inv(self, inv_type, num_arrays):
        inv_num_mppt = 1
        if inv_type == "inverters" and self._string_inv_qty <= 1:
            inv_num_mppt = num_arrays
        return inv_num_mppt

    def set_module_parameters(self):
        my_inv = self.get_module()

        self.inv_snl_c0 = float(my_inv["C0"].iloc[0])
        self.inv_snl_c1 = float(my_inv["C1"].iloc[0])
        self.inv_snl_c2 = float(my_inv["C2"].iloc[0])
        self.inv_snl_c3 = float(my_inv["C3"].iloc[0])
        self.inv_snl_paco = float(my_inv["Paco"].iloc[0])
        self.inv_snl_pdco = float(my_inv["Pdco"].iloc[0])
        self.inv_snl_pnt = float(my_inv["Pnt"].iloc[0])
        self.inv_snl_pso = float(my_inv["Pso"].iloc[0])
        self.inv_snl_vdcmax = float(my_inv["Vdcmax"].iloc[0])
        self.inv_snl_vdco = float(my_inv["Vdco"].iloc[0])
        self.mppt_low_inverter = float(my_inv["Mppt_low"].iloc[0])
        if self.inverter_name in [
            "Q.VOLT H7.6SX",
            "Powerwall 3 (integrated inverter)",
        ]:
            self.mppt_low_inverter = (
                90.0 if self.inverter_name == "Q.VOLT H7.6SX" else 60.0
            )
        self.mppt_hi_inverter = float(my_inv["Mppt_high"].iloc[0])
        self.inverter_model = 0
