from geli.aurora_components_db import AuroraModuleDatabase


class PySAM_Modules(AuroraModuleDatabase):
    def __init__(self, module_name, module_quantity, specsheet_url=None):
        self._mod_url = self.set_mod_specsheet_url(
            url=specsheet_url, mod="modules"
        )
        self._pysam_mod_specsheet = self.set_pysam_module_specsheet()

        # check to remove aliases
        if "Q.PEAK DUO BLK ML-G10+ 400W" in module_name:
            module_name = module_name.replace("W", "")

        super().__init__(module_name, module_quantity)

        self.check_if_module_in_pysam_library(module_name, "Module")
        self.set_module_parameters()

    def set_module_parameters(self):
        my_mod = self.get_module()
        # Cell temperature model selection, Options: 0=noct,1=mc
        self.cec_temp_corr_mode = 0
        self.cec_a_ref = float(my_mod.a_ref.iloc[0])
        self.cec_adjust = float(my_mod.Adjust.iloc[0])
        self.cec_alpha_sc = float(my_mod.alpha_sc.iloc[0])
        self.cec_area = float(my_mod.A_c.iloc[0])

        self.cec_beta_oc = float(my_mod.beta_oc.iloc[0])
        self.cec_gamma_r = float(my_mod.gamma_r.iloc[0])
        self.cec_i_l_ref = float(my_mod.I_L_ref.iloc[0])
        self.cec_i_mp_ref = float(my_mod.I_mp_ref.iloc[0])
        self.cec_i_o_ref = float(my_mod.I_o_ref.iloc[0])
        self.cec_i_sc_ref = float(my_mod.I_sc_ref.iloc[0])
        self.cec_is_bifacial = int(my_mod.Bifacial.iloc[0])
        self.cec_n_s = float(my_mod.N_s.iloc[0])
        self.cec_r_s = float(my_mod.R_s.iloc[0])
        self.cec_r_sh_ref = float(my_mod.R_sh_ref.iloc[0])
        self.cec_t_noct = float(my_mod.T_NOCT.iloc[0])
        self.cec_v_mp_ref = float(my_mod.V_mp_ref.iloc[0])
        self.cec_v_oc_ref = float(my_mod.V_oc_ref.iloc[0])
        self.cec_module_length = self.mod_length
        self.cec_module_width = self.mod_width

        self.module_aspect_ratio = (
            self.cec_module_length / self.cec_module_width
        )
