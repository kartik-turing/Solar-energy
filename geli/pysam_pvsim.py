import json
import pathlib
from typing import Union

import pandas
import PySAM.Grid as Grid
import PySAM.HostDeveloper as HostDeveloper
import PySAM.Pvsamv1 as Pvsamv1
import PySAM.ResourceTools as tools
import PySAM.Utilityrate5 as Utilityrate5
import requests
from geli.runner import Runner


class PySAM_PVSim:
    _include_utility_rates = True
    _include_system_design = True
    _include_modules = True
    _include_batteries = True
    _include_inverters = True
    _include_subarrays = True

    @classmethod
    def testing_constructor(
        cls,
        designVendorName,
        designID,
        tenantID,
        simulationMode,
        simulationYears,
        outputResolution,
        test_without_utility_rates,
        test_without_system_design,
        test_without_modules,
        test_without_inverters,
        test_without_batteries,
    ):
        # fmt: off
        cls._include_modules = False if test_without_modules else True
        cls._include_inverters = False if test_without_inverters else True
        cls._include_batteries = False if test_without_batteries else True
        cls._include_utility_rates = (
            False if test_without_utility_rates else True
        )
        cls._include_system_design = (
            False if test_without_system_design else True
        )

        pvsim = PySAM_PVSim(
            designVendorName,
            designID,
            tenantID,
            simulationMode,
            simulationYears,
            outputResolution,
        )
        return pvsim

    def __init__(
        self,
        designVendorName: str,
        designID: str,
        tenantID: str,
        simulationMode: str,
        simulationYears: int,
        outputResolution: str,
        annualDegradation: Union[list, None] = None,
    ):
        # create pysam objects
        self.pv = Pvsamv1.new()
        self.grid = Grid.from_existing(self.pv)
        self.utility = Utilityrate5.from_existing(self.grid)
        self.financial = HostDeveloper.from_existing(self.utility)
        base_url = "https://api.aurorasolar.com"
        AURORA_TOKEN = "rk_prod_b293db1019e44f33ce389c9f"

        self.runner = Runner(
            design_id=designID,
            base_url=base_url,
            tenant_id=tenantID,
            token=AURORA_TOKEN,
            sam_api_key="6KZH3sWJYqNraJmwfEoka2oBtcAbXPo8JKfXrUwh",
            sam_email="jackson.herron@qcells.com",
            # EXTENSION FEATURE: The supported technology can be extended to those other than Solar PV
            technology="solar",
            simulationYears=simulationYears,
            # ASSUMPTION: Annual_degradation is taken to be 0.55% for all simulation years & module types
            #             unless the module-specific annualDegradation argument is explicitly specified
            #             from the simulationJobAPI
            annualDegradation=(
                [0.55 / 100] * simulationYears
                if annualDegradation is None
                else annualDegradation
            ),
            include_system_design=self._include_system_design,
            include_modules=self._include_modules,
            include_inverters=self._include_inverters,
            include_batteries=self._include_batteries,
        )
        # set design Id attribute to log failures in log_{self.designID}
        self.designID = designID

        # set albedo for all months in the year
        # ASSUMPTION: Albedo is assumed to be uniform across all months and equal to 20%
        self.set_annual_albedo(0.2)

        # set hourly energy load
        self.load = self.runner.aurora_api.get_consumption_profile()[
            "hourly_energy"
        ]
        # set price signal
        # ASSUMPTION: The PPA Price Input is assumed to be fixed at 0.15 $/kWh
        self.ppa_price_input = [0.15]  # PPA Price Input [$/kWh]
        self.ppa_multiplier_model = (
            0  # PPA multiplier model [0/1], Options: 0=diurnal,1=timestep
        )
        # ASSUMPTION: The PPA Escalation rate is assumed to be fixed at 1% per annum
        self.ppa_escalation = 1  # PPA escalation rate [%/year]

        # ASSUMPTION: The Dispatch TOD factors are assumed
        # turned off black formatting for below list (do not remove the line below)
        # fmt: off
        self.dispatch_tod_factors = [1, 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1]  # TOD factors for periods 1-9

        # ASSUMPTION: The Weekday dispatch schedule parameters are assumed
        # turned off black formatting for below list (do not remove the line below)
        # fmt: off
        self.dispatch_sched_weekday =   [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],   # Diurnal weekday TOD periods [1..9]
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # ASSUMPTION: The Weekend dispatch schedule parameters are assumed
        # turned off black formatting for below list (do not remove the line below)
        # fmt: off
        self.dispatch_sched_weekend =   [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],   # Diurnal weekend TOD periods [1..9]
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # export compensation rate for NEM 3.0
        if self._include_utility_rates:
            address = self.runner.aurora_api.get_address()
            utility_name = self.runner.aurora_api.get_utility_name()
            # ASSUMPTION: The export compensation rate is available in Current Working Directory and named "CA_ecr_prices.csv"
            export_compensation_rate = pandas.read_csv("CA_ecr_prices.csv")[
                "pge_ecr"
            ].values.tolist()
            # Electricity rates
            # ASSUMPTION: The utility rates are assumed to be provided by PG&E
            openEI_utility_mapping = dict({
                "Pacific Gas & Electric Co": "Pacific Gas & Electric Co"
                # Aurora : Open EI
            })

            utility_name = "Pacific Gas & Electric Co"

            openEI_utility = openEI_utility_mapping[utility_name]

            # Retrieve tariffs for utility
            # ASSUMPTION: Utility rates are sought for a fixed geographical location
            lat = 37.845403
            lon = -122.255993

            openEI_utility_rate_filename = (
                f'data/openEI_utility_rates/{lat}_{lon}_{openEI_utility.replace(" ", "")}.json'
            )

            # ASSUMPTION: Utility rate file is saved in the data subdirectory; downloaded if otherwise
            if pathlib.Path(f"{openEI_utility_rate_filename}").is_file():
                with open(f"{openEI_utility_rate_filename}") as f:
                    response = json.load(f)
            else:
                limit = "500"
                url = f"{OPENEI_BASE_URL}/utility_rates?version=7&sector=Residential&api_key={OPENEI_API_KEY}&lat={lat}&lon={lon}&ratesforutility={openEI_utility}&limit={limit}"
                response = requests.get(url).json()
                with open(
                    f"{openEI_utility_rate_filename}", "w", encoding="utf-8"
                ) as f:
                    json.dump(response, f, ensure_ascii=False, indent=4)

            utility_rates = response["items"]

            ur_df = pandas.DataFrame(utility_rates)
            # Search for tariff based on known ID
            search_term = "E-ELEC"

            filtered_ur_df = ur_df[
                ur_df["name"].str.contains(search_term)
            ].sort_values("startdate", ascending=False)
            selected_rate = filtered_ur_df.iloc[0]

            # --- Additional details ---
            # ASSUMPTION: ur_metering_option, ur_en_ts_sell_rate, ur_ts_sell_rate are assumed as below
            ur_metering_option = 3  # Metering options [0=net energy metering,1=net energy metering with $ credits,2=net billing,3=net billing with carryover to next month,4=buy all - sell all]
            ur_en_ts_sell_rate = 1  # Enable time step sell rates [0/1], Options: 0=disable,1=enable
            ur_ts_sell_rate = (
                export_compensation_rate  # Time step sell rates [$/kWh]
            )

            # --- Retrieve the full tariff details ----
            # ASSUMPTION: Utility tariff rate file is saved in the data subdirectory; downloaded if otherwise
            openEI_detailed_rate_filename = (
                f'data/openEI_utility_rates/{lat}_{lon}_{openEI_utility.replace(" ", "")}_detailedrate.json'
            )

            if pathlib.Path(f"{openEI_detailed_rate_filename}").is_file():
                with open(f"{openEI_detailed_rate_filename}") as f:
                    detailed_rate_response = json.load(f)
            else:
                detailed_rate_url = f"{OPENEI_BASE_URL}/utility_rates?version=7&detail=full&api_key={OPENEI_API_KEY}&getpage={selected_rate['label']}"
                detailed_rate_response = requests.get(detailed_rate_url).json()
                with open(
                    f"{openEI_detailed_rate_filename}", "w", encoding="utf-8"
                ) as f:
                    json.dump(
                        detailed_rate_response, f, ensure_ascii=False, indent=4
                    )

            detailed_rate = detailed_rate_response["items"][0]

            # --- Parse to SAM input job using helper tool ---
            electricity_rate = tools.URDBv7_to_ElectricityRates(detailed_rate)

            electricity_rate.update({
                "ur_metering_option": ur_metering_option,
                "ur_en_ts_sell_rate": ur_en_ts_sell_rate,
                "ur_ts_sell_rate": ur_ts_sell_rate,
            })

            # --- Assign Electricity rates ----
            self.pv.ElectricityRates.assign(electricity_rate)
            # ASSUMPTION: Degradation is assumed to be 0
            self.utility.value("degradation", [0])

        # create resource dictionaries
        self.create_resource_dictionaries()

        # set pre-assignment status flag
        self.set_all_assignment_statuses(status=-1)

        # assign resources
        self.assign_resources()

    def execute(self):
        try:
            self.pv.execute()
        except Exception as exception:
            error_message = f"{exception}".splitlines()[:2]
            error_message[1] = error_message[1].lstrip()
            assert False, " ".join(error_message)

        # list of days in every month
        # needed in case dc_degradation based degradation is to be
        # incorporated in the code
        if self.runner.lifetime.get_system_use_lifetime_output():
            self._ndays_per_month = list()
            for month in range(1, 13):
                if month == 2:
                    self._ndays_per_month.append(28)
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    self._ndays_per_month.append(31)
                if month in [4, 6, 9, 11]:
                    self._ndays_per_month.append(30)
                self._create_monthly_n_days_list()

        self.utility.execute()

    def get_energy_generation_for_a_month(self, month: int, year: int):
        assert month in range(1, 13), f"Invalid month {month}"
        if self.runner.lifetime.get_system_use_lifetime_output():
            start = (year - 1) * 8760 + 24 * sum(
                self._ndays_per_month[: month - 1]
            )
            end = start + 24 * self._ndays_per_month[month - 1]
            monthly_energy = sum(self.pv.Outputs.gen[start:end])
        else:
            monthly_energy = self.pv.Outputs.monthly_energy[month - 1]
            monthly_energy *= self.runner.lifetime.get_yearly_ac_degradation()[
                year - 1
            ]

        return monthly_energy

    def get_energy_generation_for_all_months_in_a_year(self, year: int):
        assert (
            year > 0 and year <= self.runner.lifetime.get_analysis_period()
        ), (
            f"Invalid year {year}. year must be in range [1,"
            f" {self.runner.lifetime.get_analysis_period()}]"
        )
        return [
            self.get_energy_generation_for_a_month(month + 1, year)
            for month in range(12)
        ]

    def get_energy_generation_for_all_months_in_all_years(self):
        energylist = list()
        for year in range(self.runner.lifetime.get_analysis_period()):
            energylist += self.get_energy_generation_for_all_months_in_a_year(year+1)
        return energylist

    def get_energy_generation_for_a_year(self, year: int):
        assert (
            year > 0 and year <= self.runner.lifetime.get_analysis_period()
        ), (
            f"Invalid year {year}. year must be in range [1,"
            f" {self.runner.lifetime.get_analysis_period()}]"
        )
        return sum(self.get_energy_generation_for_all_months_in_a_year(year))

    def get_energy_generation_for_all_years(self):
        return [
            self.get_energy_generation_for_a_year(year + 1)
            for year in range(self.runner.lifetime.get_analysis_period())
        ]

    # albedo information
    def set_annual_albedo(self, albedo):
        self._albedo = list([albedo for _ in range(12)])

    def get_albedo(self):
        return self._albedo

    # create resource dictionaries
    def create_resource_dictionaries(self):
        self.create_solar_resource_dict()
        self.create_module_dict()
        self.create_inverter_dict()
        self.create_system_design_dict()
        self.create_layout_dict()
        self.create_shading_dict()
        self.create_losses_dict()
        self.create_battery_system_dict()
        self.create_battery_cell_dict()
        self.create_battery_dispatch_dict()
        self.create_lifetime_dict()
        self.create_load_dict()
        self.create_price_signal_dict()

    def create_solar_resource_dict(self):
        lat_lon = self.runner.aurora_api.get_lat_lon_tuple()
        solar_resource_file_path = (
            self.runner.solar_resources.get_resource_file_paths()[lat_lon]
        )
        self._solar_resource_dict = {
            "SolarResource": {
                "solar_resource_file": solar_resource_file_path,
                "albedo": self.get_albedo(),
            }
        }

    def create_module_dict(self):
        try:
            self._module_dict = {
                "Layout": {
                    "module_aspect_ratio": (
                        self.runner.modules.module_aspect_ratio
                    )
                },
                "CECPerformanceModelWithModuleDatabase": {
                    "cec_temp_corr_mode": (
                        self.runner.modules.cec_temp_corr_mode
                    ),
                    "cec_a_ref": self.runner.modules.cec_a_ref,
                    "cec_adjust": self.runner.modules.cec_adjust,
                    "cec_alpha_sc": self.runner.modules.cec_alpha_sc,
                    "cec_area": self.runner.modules.cec_area,
                    "cec_beta_oc": self.runner.modules.cec_beta_oc,
                    "cec_gamma_r": self.runner.modules.cec_gamma_r,
                    "cec_i_l_ref": self.runner.modules.cec_i_l_ref,
                    "cec_i_mp_ref": self.runner.modules.cec_i_mp_ref,
                    "cec_i_o_ref": self.runner.modules.cec_i_o_ref,
                    "cec_i_sc_ref": self.runner.modules.cec_i_sc_ref,
                    "cec_is_bifacial": self.runner.modules.cec_is_bifacial,
                    "cec_n_s": self.runner.modules.cec_n_s,
                    "cec_r_s": self.runner.modules.cec_r_s,
                    "cec_r_sh_ref": self.runner.modules.cec_r_sh_ref,
                    "cec_t_noct": self.runner.modules.cec_t_noct,
                    "cec_v_mp_ref": self.runner.modules.cec_v_mp_ref,
                    "cec_v_oc_ref": self.runner.modules.cec_v_oc_ref,
                    "cec_bifacial_transmission_factor": (
                        self.runner.modules.cec_bifacial_transmission_factor
                    ),
                    "cec_bifaciality": self.runner.modules.cec_bifaciality,
                    "cec_bifacial_ground_clearance_height": (
                        self.runner.modules.cec_bifacial_ground_clearance_height
                    ),
                    "cec_standoff": self.runner.modules.cec_standoff,
                    "cec_height": self.runner.modules.cec_height,
                    "cec_transient_thermal_model_unit_mass": (
                        self.runner.modules.cec_transient_thermal_model_unit_mass
                    ),
                    "cec_module_length": self.runner.modules.cec_module_length,
                    "cec_module_width": self.runner.modules.cec_module_width,
                },
                "Module": {"module_model": self.runner.modules.module_model},
            }
        except Exception as exception:
            msg = f"Failed to create_module_dict. Error: {exception}"
            raise RuntimeError(msg)

    def create_inverter_dict(self):
        inv_num_mppt = self.runner.inverters.get_num_mppt_inv(
            inv_type=self.runner.aurora_api.get_inverter_type(),
            num_arrays=self.runner.aurora_api.get_num_arrays(),
        )

        self._inverter_dict = {
            "Inverter": {
                "inv_snl_paco": self.runner.inverters.inv_snl_paco,
                "mppt_low_inverter": self.runner.inverters.mppt_low_inverter,
                "mppt_hi_inverter": self.runner.inverters.mppt_hi_inverter,
                "inverter_model": self.runner.inverters.inverter_model,
                "inv_snl_eff_cec": self.runner.inverters.inv_snl_eff_cec,
                "inv_num_mppt": inv_num_mppt,
            },
            "InverterCECDatabase": {
                "inv_snl_c0": self.runner.inverters.inv_snl_c0,
                "inv_snl_c1": self.runner.inverters.inv_snl_c1,
                "inv_snl_c2": self.runner.inverters.inv_snl_c2,
                "inv_snl_c3": self.runner.inverters.inv_snl_c3,
                "inv_snl_paco": self.runner.inverters.inv_snl_paco,
                "inv_snl_pdco": self.runner.inverters.inv_snl_pdco,
                "inv_snl_pnt": self.runner.inverters.inv_snl_pnt,
                "inv_snl_pso": self.runner.inverters.inv_snl_pso,
                "inv_snl_vdcmax": self.runner.inverters.inv_snl_vdcmax,
                "inv_snl_vdco": self.runner.inverters.inv_snl_vdco,
                "inv_tdc_cec_db": self.runner.inverters.inv_tdc_cec_db,
            },
        }

    def create_system_design_dict(self):
        inverter_count = self.runner.aurora_api.get_inverter_count()
        num_modules = self.runner.modules.mod_qty
        stc_rated_power = self.runner.modules.get_module().STC.iloc[0]
        self.system_capacity = stc_rated_power * num_modules

        self._system_design_dict = dict()

        self._system_design_dict["SystemDesign"] = (
            dict({
                "inverter_count": inverter_count,
                "system_capacity": self.system_capacity,
            })
            | self.runner.system_design.get_subsystem_design_dict()
        )

    def create_layout_dict(self):
        self._layout_dict = dict()
        self._layout_dict["Layout"] = (
            self.runner.system_design.get_subsystem_layout_dict()
        )

    def create_shading_dict(self):
        self._shading_dict = dict()
        self._shading_dict["Shading"] = (
            self.runner.system_design.get_subsystem_shading_dict()
        )

    def create_losses_dict(self):
        # ASSUMPTION: assumed loss values for the ac wiring, dc optimizer and transmission
        acwiring_loss = 3  # 3%
        dcoptimizer_loss = 0  # 0%
        transmission_loss = 0  # 0%

        self._losses_dict = dict()
        self._losses_dict["Losses"] = (
            dict({
                "acwiring_loss": acwiring_loss,
                "dcoptimizer_loss": dcoptimizer_loss,
                "transmission_loss": transmission_loss,
            })
            | self.runner.system_design.get_subsystem_losses_dict()
        )

    # fmt: off
    def create_battery_system_dict(self):
        self._battery_system_dict = dict()
        enable_battery = dict({"en_batt": self.runner.battery.en_batt})

        parameters_dict = dict()
        if self.runner.battery.en_batt:
            parameters_dict = dict({
                "batt_ac_dc_efficiency": (
                    self.runner.battery.batt_ac_dc_efficiency
                ),
                "batt_dc_ac_efficiency": (
                    self.runner.battery.batt_dc_ac_efficiency
                ),
                "batt_dc_dc_efficiency": (
                    self.runner.battery.batt_dc_dc_efficiency
                ),
                "batt_ac_or_dc": self.runner.battery.batt_ac_or_dc,
                "batt_computed_bank_capacity": (
                    self.runner.battery.batt_computed_bank_capacity
                ),
                "batt_power_charge_max_kwdc": (
                    self.runner.battery.batt_power_charge_max_kwdc
                ),
                "batt_power_charge_max_kwac": (
                    self.runner.battery.batt_power_charge_max_kwac
                ),
                "batt_power_discharge_max_kwdc": (
                    self.runner.battery.batt_power_discharge_max_kwdc
                ),
                "batt_power_discharge_max_kwac": (
                    self.runner.battery.batt_power_discharge_max_kwac
                ),
                "batt_meter_position": self.runner.battery.batt_meter_position,
                "batt_computed_series": (
                    self.runner.battery.batt_computed_series
                ),
                "batt_computed_strings": (
                    self.runner.battery.batt_computed_strings
                ),
                "batt_surface_area": self.runner.battery.batt_surface_area,
                "batt_mass": self.runner.battery.batt_mass,
                "batt_current_charge_max": (
                    self.runner.battery.batt_current_charge_max
                ),
                "batt_current_discharge_max": (
                    self.runner.battery.batt_current_discharge_max
                ),
                "batt_replacement_capacity": (
                    self.runner.battery.batt_replacement_capacity
                ),
                "batt_replacement_option": (
                    self.runner.battery.batt_replacement_option
                ),
                "batt_inverter_efficiency_cutoff": (
                    self.runner.battery.batt_inverter_efficiency_cutoff
                ),
                "batt_current_choice": self.runner.battery.batt_current_choice,
            })

        self._battery_system_dict["BatterySystem"] = (
            enable_battery | parameters_dict
        )

    def create_battery_cell_dict(self):
        self._battery_cell_dict = dict()
        if self.runner.battery.en_batt:
            self._battery_cell_dict["BatteryCell"] = dict({
                "batt_chem": self.runner.battery.batt_chem,
                "batt_lifetime_matrix": (
                    self.runner.battery.batt_lifetime_matrix
                ),
                "batt_calendar_choice": (
                    self.runner.battery.batt_calendar_choice
                ),
                "batt_calendar_q0": self.runner.battery.batt_calendar_q0,
                "batt_calendar_a": self.runner.battery.batt_calendar_a,
                "batt_calendar_b": self.runner.battery.batt_calendar_b,
                "batt_calendar_c": self.runner.battery.batt_calendar_c,
                "batt_voltage_matrix": self.runner.battery.batt_voltage_matrix,
                "batt_Vfull": self.runner.battery.batt_Vfull,
                "batt_Vexp": self.runner.battery.batt_Vexp,
                "batt_Vnom_default": self.runner.battery.batt_Vnom_default,
                "batt_Vnom": self.runner.battery.batt_Vnom,
                "batt_Vcut": self.runner.battery.batt_Vcut,
                "batt_Qfull_flow": self.runner.battery.batt_Qfull_flow,
                "batt_Qfull": self.runner.battery.batt_Qfull,
                "batt_Qnom": self.runner.battery.batt_Qnom,
                "batt_Qexp": self.runner.battery.batt_Qexp,
                "batt_C_rate": self.runner.battery.batt_C_rate,
                "batt_life_model": self.runner.battery.batt_life_model,
                "batt_initial_SOC": self.runner.battery.batt_initial_SOC,
                "batt_maximum_SOC": self.runner.battery.batt_maximum_SOC,
                "batt_minimum_SOC": self.runner.battery.batt_minimum_SOC,
                "batt_minimum_outage_SOC": (
                    self.runner.battery.batt_minimum_outage_SOC
                ),
                "batt_minimum_modetime": (
                    self.runner.battery.batt_minimum_modetime
                ),
                "batt_resistance": self.runner.battery.batt_resistance,
                "batt_h_to_ambient": self.runner.battery.batt_h_to_ambient,
                "batt_Cp": self.runner.battery.batt_Cp,
                "batt_room_temperature_celsius": (
                    self.runner.battery.batt_room_temperature_celsius
                ),
                "cap_vs_temp": self.runner.battery.cap_vs_temp,
                "batt_calendar_lifetime_matrix": (
                    self.runner.battery.batt_calendar_lifetime_matrix
                ),
                "batt_voltage_choice": self.runner.battery.batt_voltage_choice,
            })

    def create_battery_dispatch_dict(self):
        self._battery_dispatch_dict = dict()
        if self.runner.battery.en_batt:
            self._battery_dispatch_dict["BatteryDispatch"] = dict({
                "batt_dispatch_choice": (
                    self.runner.battery.batt_dispatch_choice
                ),
                "batt_dispatch_auto_btm_can_discharge_to_grid": (
                    self.runner.battery.batt_dispatch_auto_btm_can_discharge_to_grid
                ),
                "batt_dispatch_auto_can_gridcharge": (
                    self.runner.battery.batt_dispatch_auto_can_gridcharge
                ),
                "batt_dispatch_charge_only_system_exceeds_load": (
                    self.runner.battery.batt_dispatch_charge_only_system_exceeds_load
                ),
                "batt_dispatch_discharge_only_load_exceeds_system": (
                    self.runner.battery.batt_dispatch_discharge_only_load_exceeds_system
                ),
                # 'batt_dispatch_load_forecast_choice': self.runner.battery.batt_dispatch_load_forecast_choice,
                # 'batt_dispatch_wf_forecast_choice': self.runner.battery.batt_dispatch_wf_forecast_choice,
                "batt_cycle_cost_choice": (
                    self.runner.battery.batt_cycle_cost_choice
                ),
                "batt_cycle_cost": self.runner.battery.batt_cycle_cost,
            })

    # fmt: on
    def create_lifetime_dict(self):
        self._lifetime_dict = dict()
        self._lifetime_dict["Lifetime"] = dict({
            "analysis_period": self.runner.lifetime.get_analysis_period(),
            # The degradation is applied following option 1 mentioned in
            # https://growingenergylabs.atlassian.net/browse/ES3P-275?focusedCommentId=111568,
            # i.e., using AC degradation which applies specified degradation values on
            # simulation results obtained for year 1, as opposed to PySAM's strategy of applying
            # degradation factors to input parameters and running simulationYears number of
            # simulations. For the enabling the latter strategy the parameter
            # system_use_lifetime_ouput is required to be 1 and the dc_degradation parameter
            # needs to be an appropriate list of values. For the former it is sufficient
            # to set system_use_lifetime_output = 0 which makes the dc_degradation input irrelevant
            "system_use_lifetime_output": (
                self.runner.lifetime.get_system_use_lifetime_output()
            ),
            "dc_degradation": self.runner.lifetime.get_yearly_dc_degradation(),
        })

    def create_load_dict(self):
        self._load_dict = dict()
        self._load_dict["Load"] = dict({"load": self.load})

    def create_price_signal_dict(self):
        self._price_signal_dict = dict()
        self._price_signal_dict["PriceSignal"] = dict({
            "ppa_price_input": self.ppa_price_input,
            "ppa_multiplier_model": self.ppa_multiplier_model,
            "ppa_escalation": self.ppa_escalation,
            "dispatch_tod_factors": self.dispatch_tod_factors,
            "dispatch_sched_weekday": self.dispatch_sched_weekday,
            "dispatch_sched_weekend": self.dispatch_sched_weekend,
        })

    # get resource dictionaries
    def get_solar_resource_dict(self):
        return self._solar_resource_dict

    def get_module_dict(self):
        return self._module_dict

    def get_inverter_dict(self):
        return self._inverter_dict

    def get_system_design_dict(self):
        return self._system_design_dict

    def get_layout_dict(self):
        return self._layout_dict

    def get_shading_dict(self):
        return self._shading_dict

    def get_losses_dict(self):
        return self._losses_dict

    def get_battery_system_dict(self):
        return self._battery_system_dict

    def get_battery_cell_dict(self):
        return self._battery_cell_dict

    def get_battery_dispatch_dict(self):
        return self._battery_dispatch_dict

    def get_lifetime_dict(self):
        return self._lifetime_dict

    def get_load_dict(self):
        return self._load_dict

    def get_price_signal_dict(self):
        return self._price_signal_dict

    # set resource assignment statuses
    def set_all_assignment_statuses(self, status):
        self.set_solar_resource_assignment_status(status)
        self.set_module_assignment_status(status)
        self.set_inverter_assignment_status(status)
        self.set_system_design_assignment_status(status)
        self.set_layout_assignment_status(status)
        self.set_shading_assignment_status(status)
        self.set_losses_assignment_status(status)
        self.set_battery_system_assignment_status(status)
        self.set_battery_cell_assignment_status(status)
        self.set_battery_dispatch_assignment_status(status)
        self.set_lifetime_assignment_status(status)
        self.set_load_assignment_status(status)
        self.set_price_signal_status(status)

    def set_solar_resource_assignment_status(self, status):
        self._solar_ressource_assignment_status = status

    def set_module_assignment_status(self, status):
        self._module_assignment_status = status

    def set_inverter_assignment_status(self, status):
        self._inverter_assignment_status = status

    def set_system_design_assignment_status(self, status):
        self._system_design_assignment_status = status

    def set_layout_assignment_status(self, status):
        self._layout_assignment_status = status

    def set_shading_assignment_status(self, status):
        self._shading_assignment_status = status

    def set_losses_assignment_status(self, status):
        self._losses_assignment_status = status

    def set_battery_system_assignment_status(self, status):
        self._battery_system_assignment_status = status

    def set_battery_cell_assignment_status(self, status):
        self._battery_cell_assignment_status = status

    def set_battery_dispatch_assignment_status(self, status):
        self._battery_dispatch_assignment_status = status

    def set_lifetime_assignment_status(self, status):
        self._lifetime_assignment_status = status

    def set_load_assignment_status(self, status):
        self._load_assignment_status = status

    def set_price_signal_status(self, status):
        self._price_signal_assignment_status = status

    # get resource assignment statuses
    def get_solar_resource_assignment_status(self):
        return self._solar_ressource_assignment_status

    def get_module_assignment_status(self):
        return self._module_assignment_status

    def get_inverter_assignment_status(self):
        return self._inverter_assignment_status

    def get_system_design_assignment_status(self):
        return self._system_design_assignment_status

    def get_layout_assignment_status(self):
        return self._layout_assignment_status

    def get_shading_assignment_status(self):
        return self._shading_assignment_status

    def get_losses_assignment_status(self):
        return self._losses_assignment_status

    def get_battery_system_assignment_status(self):
        return self._battery_system_assignment_status

    def get_battery_cell_assignment_status(self):
        return self._battery_cell_assignment_status

    def get_battery_dispatch_assignment_status(self):
        return self._battery_dispatch_assignment_status

    def get_lifetime_assignment_status(self):
        return self._lifetime_assignment_status

    def get_load_assignment_status(self):
        return self._load_assignment_status

    def get_price_signal_assignment_status(self):
        return self._price_signal_assignment_status

    # assign resources
    def assign_resources(self):
        self.assign_solar_resource()
        self.assign_modules()
        self.assign_inverters()
        self.assign_system_design()
        self.assign_layout()
        self.assign_shading()
        self.assign_losses()
        self.assign_battery_system()
        self.assign_battery_cell()
        self.assign_battery_dispatch()
        self.assign_lifetime()
        self.assign_load()
        self.assign_price_signal()

    def assign_solar_resource(self):
        self.pv.assign(self.get_solar_resource_dict())
        self.set_solar_resource_assignment_status(status=1)

    def assign_modules(self):
        try:
            self.pv.assign(self.get_module_dict())
        except Exception as exception:
            msg = f"Failed to assign_modules. Error: {exception}"
            raise RuntimeError(msg)
        self.set_module_assignment_status(status=1)

    def assign_inverters(self):
        self.pv.assign(self.get_inverter_dict())
        self.set_inverter_assignment_status(status=1)

    def assign_system_design(self):
        self.pv.assign(self.get_system_design_dict())
        self.set_system_design_assignment_status(status=1)

    def assign_layout(self):
        self.pv.assign(self.get_layout_dict())
        self.set_layout_assignment_status(status=1)

    def assign_shading(self):
        self.pv.assign(self.get_shading_dict())
        self.set_shading_assignment_status(status=1)

    def assign_losses(self):
        self.pv.assign(self.get_losses_dict())
        self.set_losses_assignment_status(status=1)

    def assign_battery_system(self):
        self.pv.assign(self.get_battery_system_dict())
        self.set_battery_system_assignment_status(status=1)

    def assign_battery_cell(self):
        self.pv.assign(self.get_battery_cell_dict())
        self.set_battery_cell_assignment_status(status=1)

    def assign_battery_dispatch(self):
        self.pv.assign(self.get_battery_dispatch_dict())
        self.set_battery_dispatch_assignment_status(status=1)

    def assign_lifetime(self):
        self.pv.assign(self.get_lifetime_dict())
        self.set_lifetime_assignment_status(status=1)

    def assign_load(self):
        self.pv.assign(self.get_load_dict())
        self.set_load_assignment_status(status=1)

    def assign_price_signal(self):
        self.pv.assign(self.get_price_signal_dict())
        self.set_price_signal_status(status=1)
