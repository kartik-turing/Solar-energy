import warnings

import numpy as np


class PySAM_SystemDesign:
    def __init__(self, design_id, string_inv_qty):
        self._design_id = design_id
        self.string_inv_qty = string_inv_qty
        self._subarray_design_dict = dict()
        self._subsystem_layout_dict = dict()
        self._subsystem_shading_dict = dict()
        self._subsystem_losses_dict = dict()

    # get functions
    def get_subsystem_design_dict(self):
        return self._subarray_design_dict

    def get_subsystem_layout_dict(self):
        return self._subsystem_layout_dict

    def get_subsystem_shading_dict(self):
        return self._subsystem_shading_dict

    def get_subsystem_losses_dict(self):
        return self._subsystem_losses_dict

    # utility functions for common subsystem parameters
    def get_subarray_num_mods(self, array):
        return array["module"]["count"]

    def get_subarray_nstrings(self, idx, array, inverter_type):
        key = "strings" if inverter_type == "inverters" else "module"
        # REQUIREMENT: strings/module keyword have to be specified in the subarrays
        if key not in array:
            raise KeyError(
                f"Design Id {self._design_id} does not have the '{key}'"
                " keyword in its array(/s)"
            )

        return array[key]["count"]

    def get_subarray_tilt(self, array):
        return array["pitch"]

    def get_subarray_azimuth(self, idx, array):
        azimuth = array["azimuth"]
        # REQUIREMENT: PySAM Upper bound on azimuth is 359.9
        if azimuth > 359.9:
            warnings.warn(
                f"Correcting Azimuth: Subarray{idx} has azimuth={azimuth}."
                " PySAM supports max(azimuth)= 359.9"
            )
            with open("batchruns_warning_logs", "a") as f:
                f.write(
                    f"Correcting Azimuth: Subarray{idx} of design id"
                    f" {self._design_id} has azimuth={azimuth}. PySAM supports"
                    " max(azimuth)= 359.9\n"
                )
            azimuth = 359.9
        return azimuth

    def get_subarray_string_inverter_index(self, array, inverter_type):
        return array["string_inverter"]["index"]

    # create the subsystem dictionaries
    def create_subarray_dict(
        self,
        idx,
        array,
        enable,
        inverter_type,
        inverter_count,
        num_arrays,
        string_inv_qty,
    ):
        # LIMITATION: SAM does not support multiple MPPT input (arrays) with multple inverters
        mppt_input = idx + 1
        if idx > 0:
            enable_subarray = 1 if enable else 0
            self._subarray_design_dict[f"subarray{idx+1}_enable"] = (
                enable_subarray
            )
            if inverter_type == "inverters":
                if string_inv_qty > 1:
                    if string_inv_qty != num_arrays:
                        raise ValueError(
                            "Multiple MPPT input (arrays) with multiple"
                            " inverters is not supported in SAM."
                        )
                    else:
                        mppt_input = 1
            else:
                mppt_input = 1

        if enable:
            # number of strings
            nstrings = self.get_subarray_nstrings(
                mppt_input, array, inverter_type
            )
            # number of modules
            num_mods = self.get_subarray_num_mods(array)

            # modules per string
            modules_per_string = (
                num_mods / nstrings if inverter_type == "inverters" else 1.0
            )
            if (
                inverter_type == "inverters"
                and not modules_per_string.is_integer()
            ):
                # REQUIREMENT: for inverter_type as 'inverters' modules per string is required to be an integer
                raise ValueError(
                    f"Sub-array {idx + 1} number of modules per string is not"
                    f" even: {nstrings} strings, {num_mods} modules."
                )
            # Sub-array Tilt [degrees]
            tilt = self.get_subarray_tilt(array)
            # Sub-array terrain tilt [degrees]
            # ASSUMPTION: slope tilt is assumed to be 0
            slope_tilt = 0
            # Sub-array Azimuth [degrees]
            azimuth = self.get_subarray_azimuth(mppt_input, array)
            # Sub-array terrain azimuth [degrees]
            # ASSUMPTION: slope azm is assumed to be 0
            slope_azm = 0
            # Options: 0=fixed,1=1axis,2=2axis,3=azi,4=monthly (hard-coded)
            track_mode = 0
            # For future use with multiple inverters
            # NOT SURE IF THIS IS USED ANYWHERE?
            # string_inv_index = self.get_subarray_string_inverter_index(array)

            if not modules_per_string.is_integer():
                raise ValueError(
                    f"Number of modules per string for Sub-array{idx+1} is not"
                    f" even: {nstrings} Strings, {num_mods} modules."
                )

            # sel_subarray_design_dictf.[f"subarray{mppt_input}_enable"] = enable
            self._subarray_design_dict["inverter_count"] = inverter_count
            self._subarray_design_dict[f"subarray{idx+1}_mppt_input"] = (
                mppt_input
            )

            self._subarray_design_dict[f"subarray{idx+1}_nstrings"] = nstrings
            self._subarray_design_dict[
                f"subarray{idx+1}_modules_per_string"
            ] = modules_per_string
            self._subarray_design_dict[f"subarray{idx+1}_tilt"] = tilt
            self._subarray_design_dict[f"subarray{idx+1}_slope_tilt"] = (
                slope_tilt
            )
            self._subarray_design_dict[f"subarray{idx+1}_azimuth"] = azimuth
            self._subarray_design_dict[f"subarray{idx+1}_slope_azm"] = (
                slope_azm
            )
            self._subarray_design_dict[f"subarray{idx+1}_track_mode"] = (
                track_mode
            )

    def create_layout_dict(self, idx, array):
        mppt_input = idx + 1
        orientation = array["module"]["orientation"]
        # Options for orientation: 0=portrait,1=landscape
        mod_orientation = 1 if orientation == "landscape" else 0

        nmodx = (
            self.get_subarray_num_mods(array)
            if orientation == "landscape"
            else 1
        )
        nmody = (
            self.get_subarray_num_mods(array)
            if orientation == "portrait"
            else 1
        )

        self._subsystem_layout_dict[f"subarray{mppt_input}_mod_orient"] = (
            mod_orientation
        )
        self._subsystem_layout_dict[f"subarray{mppt_input}_nmodx"] = nmodx
        self._subsystem_layout_dict[f"subarray{mppt_input}_nmody"] = nmody

    def create_shading_dict(self, idx, array, component_type):
        # REQUIREMENT: Shading information is needed in the array
        mpp_input = idx + 1
        # Sub-array 1 shading mode (fixed tilt or 1x tracking) [0/1/2]
        # Options: 0=none,1=standard(non-linear),2=thin film(linear)
        shade_mode = 0  # (hard-coded)
        # Enable Sub-array 1 Month x Hour beam shading losses [0/1]
        shading_en_mxh = 1  # (hard-coded)
        try:
            aurora_shading = np.array([
                array["shading"]["solar_access"]["monthly"][:]
                for _ in range(24)
            ]).T
        except Exception as exception:
            raise Exception(exception, f"Shading not found in subarray {idx}")

        reduction_factor = (
            1 / 3
            if component_type in ["microinverters", "dc_optimizer"]
            else 1.0
        )
        shading_mxh = ((100 - aurora_shading) * reduction_factor).tolist()

        self._subsystem_shading_dict[f"subarray{mpp_input}_shade_mode"] = (
            shade_mode
        )
        self._subsystem_shading_dict[f"subarray{mpp_input}_shading_en_mxh"] = (
            shading_en_mxh
        )
        self._subsystem_shading_dict[f"subarray{mpp_input}_shading_mxh"] = (
            shading_mxh
        )

    def create_losses_dict(self, idx, array, component_type):
        mpp_input = idx + 1

        # ASSUMPTION: below values are assumed
        acwiring_loss = 3
        dcoptimizer_loss = 0
        transmission_loss = 0
        soiling = [2] * 12  # 2%
        rear_soiling_loss = 0  # 0%
        mismatch_loss = (
            0 if component_type in ["microinverters", "dc_optimizer"] else 2
        )
        diodeconn_loss = 0.5  # 0.5%
        dcwiring_loss = 2  # 1%
        nameplate_loss = 1.5  # 1.5 %
        electrical_mismatch = 0  # 0%
        rack_shading = 0  # 0%
        tracking_loss = 0  # 0%

        self._subsystem_losses_dict[f"subarray{mpp_input}_soiling"] = soiling
        self._subsystem_losses_dict[
            f"subarray{mpp_input}_rear_soiling_loss"
        ] = rear_soiling_loss
        # self._subsystem_losses_dict[f"subarray{mpp_input}_acwiring_loss"] = (acwiring_loss)
        # self._subsystem_losses_dict[f"subarray{mpp_input}_dcoptimizer_loss"] = (dcoptimizer_loss)
        # self._subsystem_losses_dict[f"subarray{mpp_input}_transmission_loss"] = (transmission_loss)
        self._subsystem_losses_dict[f"subarray{mpp_input}_mismatch_loss"] = (
            mismatch_loss
        )
        self._subsystem_losses_dict[f"subarray{mpp_input}_diodeconn_loss"] = (
            diodeconn_loss
        )
        self._subsystem_losses_dict[f"subarray{mpp_input}_dcwiring_loss"] = (
            dcwiring_loss
        )
        self._subsystem_losses_dict[f"subarray{mpp_input}_nameplate_loss"] = (
            dcwiring_loss
        )
        self._subsystem_losses_dict[
            f"subarray{mpp_input}_electrical_mismatch"
        ] = electrical_mismatch
        self._subsystem_losses_dict[f"subarray{mpp_input}_rack_shading"] = (
            rack_shading
        )
        self._subsystem_losses_dict[f"subarray{mpp_input}_tracking_loss"] = (
            tracking_loss
        )
