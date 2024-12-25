import ast
import logging
import os

import pandas
import requests

component_types = {
    "modules": "module",
    "inverters": "inverter",
    "batteries": "battery",
}


class AuroraModulesBase:
    def set_mod_specsheet_url(self, url, mod):
        if mod == "modules":
            default_url = "https://raw.githubusercontent.com/NREL/SAM/master/deploy/libraries/CEC%20Modules.csv"
        elif mod == "inverters":
            default_url = "https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Inverters.csv"
        else:
            raise ValueError(
                "Missing argument for 'mod'. Please specify if mod is"
                " 'module'/'inverter'"
            )

        return_url = default_url if url is None else url
        return return_url

    def get_mod_specsheet_url(self):
        return self._mod_url

    def set_pysam_module_specsheet(self):
        return pandas.read_csv(self.get_mod_specsheet_url(), index_col=0)

    def get_pysam_module_specsheet(self):
        return self._pysam_mod_specsheet

    def check_if_module_in_pysam_library(self, module_name, module_type):
        specs = self.get_pysam_module_specsheet()
        if module_name == "Q.TRON BLK M-G2+ 425":
            mod_filter = (
                specs.index.str.startswith("Hanwha")
                & specs.index.str.contains("Q.TRON BLK M-G2")
                & specs.index.str.endswith("425")
            )
        elif module_name == "Powerwall 3 (integrated inverter)":
            mod_filter = (
                specs.index.str.startswith("Tesla Inc")
                & specs.index.str.contains("1538000-xx-y")
                & specs.index.str.endswith("[240V]")
            )
        else:
            mod_filter = specs.index.str.contains(module_name)
        assert (
            sum(mod_filter) == 1
        ), f"{module_name} not found in module spec sheet url"
        try:
            self._module = self.get_pysam_module_specsheet()[mod_filter]
        except Exception as e:
            raise AttributeError(
                f"{module_type} is no longer found in library. See if the name"
                " has changed."
            )

    def get_component_params(self, component_id):
        base_url = "http://k8s-simulati-simservi-5e2b61cbe1-30747f80881ab8fe.elb.us-west-2.amazonaws.com:8080/simulation/resi/v1"
        token = os.getenv("access_token")
        if not token or "mock" in token:
            data = {
                "client_id": "6nobto8ah2cbol2os8h8tioi9v",
                "client_secret": "ngetrede3r0davdcimmu0316uq7p81ue3bie3io6pmc7pt2tgk6",
                "grant_type": "client_credentials",
                "scope": "simulations/simulations",
            }

            token_url = "https://simulations.auth.us-west-2.amazoncognito.com/oauth2/token"
            response = requests.post(token_url, data=data)
            response = response.json()
            token = response["access_token"]
            os.environ["access_token"] = token

        if "Module" in self.__class__.__name__:
            component_name = "modules"
            response_key = "ModuleComponentResponse"

        elif "Inverter" in self.__class__.__name__:
            component_name = "inverters"
            response_key = "InverterComponentResponse"

        elif (
            "Battery" in self.__class__.__name__
            or "Batteries" in self.__class__.__name__
        ):
            component_name = "batteries"
            response_key = "BatteryComponentResponse"
        self.api_url = f"{base_url}/{component_name}/{component_id}"

        try:
            response = requests.get(self.api_url, headers={"Authorization":f"Bearer {token}"})
            if response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                result = response_data["content"][response_key]
                del result["id"]
                return result
            else:
                error_message = (
                    "Failed to get data from API. Status code:"
                    f" {response.status_code}"
                )
                logging.error(error_message)
                raise Exception(error_message)
        except requests.RequestException as e:
            if "value is not a valid enumeration member" in str(e):
                raise AttributeError(
                    f"Unknown {component_name} Name: '{component_id}'"
                )
            logging.error(f"Request failed: {e}")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def get_module(self):
        return self._module


class AuroraModuleDatabase(AuroraModulesBase):
    def __init__(self, module_name, quantity):
        # Photovoltaic module model specifier, Options: 0=spe,1=cec,2=6par_user,3=snl,4=sd11-iec61853,5=PVYield
        # ASSUMPTION: module model is assumed to be CEC
        self.module_model = 1
        self.module_name = module_name
        self.mod_qty = quantity
        self.set_component_parameters()

    def set_component_parameters(self):
        module_data = self.get_component_params(self.module_name)
        if not module_data:
            raise ValueError(f"Module with Id '{self.module_name}' not found")
        self.__dict__.update(module_data)


class AuroraInverterDatabase(AuroraModulesBase):
    def __init__(self, inverter_name, quantity):
        # Photovoltaic module model specifier, Options: 0=spe,1=cec,2=6par_user,3=snl,4=sd11-iec61853,5=PVYield
        # ASSUMPTION: Inverter model is assumed to be CEC
        self.module_model = 1
        self.inverter_name = inverter_name
        self.mod_qty = quantity
        self.set_component_parameters()

    def set_component_parameters(self):

        inverter_data = self.get_component_params(self.inverter_name)
        if not inverter_data:
            raise ValueError(
                f"Inverter with Id '{self.inverter_name}' not found"
            )
        inverter_data["inv_tdc_cec_db"] = ast.literal_eval(
            inverter_data["inv_tdc_cec_db"]
        )
        self.__dict__.update(inverter_data)


class AuroraBatteryDatabase(AuroraModulesBase):
    def __init__(
        self,
        battery_name,
        quantity,
        inverter_name,
        inverter_type,
        storage_inv,
        dc_optimizer,
        num_arrays,
    ):
        # ASSUMPTION: If storage_inverter is not there in the design, add 'Q.VOLT H7.6SX' as the default storage_inverter
        # ASSIGN STORAGE INVERTER by Check if battery is in Q.Save Series or Encharge
        # If no storage inverter assigned, default to Q.VOLT H7.6SX # & (battery_name not in ('ENCHARGE-10-1P-NA', 'Powerwall 3'))
        if storage_inv == None:
            # print("WARNING: No storage inverter assigned, defaulting to Q.VOLT H7.6SX")
            # with open("batchruns_warning_logs", "a") as f:
            #    f.write(f"WARNING: No storage inverter assigned, defaulting to Q.VOLT H7.6SX.\n")
            storage_inv = {
                "id": "fb249b44-ac5c-4da5-9a86-cb0ac8fb8bf5",
                "name": "Q.VOLT H7.6SX",
                "rated_power": 7608.0,
                "manufacturer": "Qcells",
            }
        # LIMITATION: Q.SAVE battery must be coupled with Q.VOLT inverter
        if (
            battery_name
            in ("Q.SAVE D15.0SX", "Q.SAVE D10.0SX", "Q.SAVE D20.0SX")
        ) and storage_inv["name"] not in ("Q.VOLT H3.8SX", "Q.VOLT H7.6SX"):
            raise ValueError(
                'Storage Inverter for Q.SAVE products must be one of "Q.VOLT'
                ' H3.8SX", "Q.VOLT H7.6SX"'
            )
        if battery_name:
            self.set_component_parameters(
                battery_name,
                quantity,
                inverter_name,
                inverter_type,
                storage_inv,
                dc_optimizer,
                num_arrays,
            )
        else:
            self.en_batt = 0

    def process_tables_response(self, battery_json, quantity):
        batt_qty_params = [
            "batt_computed_bank_capacity",
            "batt_power_charge_max_kwdc",
            "batt_power_charge_max_kwac",
            "batt_power_discharge_max_kwdc",
            "batt_power_discharge_max_kwac",
            "batt_computed_strings",
            "batt_surface_area",
            "batt_mass",
            "batt_current_charge_max",
            "batt_current_discharge_max",
        ]
        for param in batt_qty_params:
            factored_value = battery_json[param] * quantity
            battery_json[param] = factored_value

    def set_component_parameters(
        self,
        battery_name,
        quantity,
        inverter_name,
        inverter_type,
        storage_inv,
        dc_optimizer,
        num_arrays,
    ):
        config_inverter = ""
        # ASSUMPTION: If there are dc_optimizers or inverter_name = "Powerwall 3 (integrated inverter)" or num_arrays > 1, the battery is treated as AC Coupled
        # ASSUMPTION: For cases with AC coupled batteries, parameters are assigned as if the inverter type is 'microinverter'.
        if (
            inverter_type == "microinverters"
            or (dc_optimizer)
            or (battery_name == "ENCHARGE-10-1P-NA")
            or inverter_name == "Powerwall 3 (integrated inverter)"
            or num_arrays > 1
        ):
            config_inverter = "Microinverters/Dc Optimizers"
        elif inverter_type == "inverters":
            config_inverter = "Inverters"

        storage_inverter_name = (
            storage_inv["name"]
            if storage_inv["name"] in ["Q.VOLT H3.8SX", "Q.VOLT H7.6SX"]
            else ""
        )
        ac_or_dc_coupled = (
            "AC" if config_inverter == "Microinverters/Dc Optimizers" else "DC"
        )
        if battery_name:
            battery_id = (
                f"{ac_or_dc_coupled}_{storage_inverter_name}_{battery_name}"
                if storage_inverter_name
                and battery_name not in ["Powerwall 3", "ENCHARGE-10-1P-NA"]
                else f"{ac_or_dc_coupled}_{battery_name}"
            )

            battery_data = self.get_component_params(battery_id)

            if not battery_data:
                raise ValueError(f"Battery with Id '{battery_id}' not found")

            self.process_tables_response(battery_data, quantity)
            self.__dict__.update(battery_data)
        else:
            self.en_batt = 0

        self.batt_dispatch_choice = (
            5  # Battery dispatch algorithm [0/1/2/3/4/5]
        )
        # Options: 0=PeakShaving,1=InputGridTarget,2=InputBatteryPower,3=ManualDispatch,4=RetailRateDispatch,5=SelfConsumption
        self.batt_dispatch_auto_btm_can_discharge_to_grid = (
            1  # Behind the meter battery can discharge to grid? [0/1]
        )
        self.batt_dispatch_auto_can_gridcharge = (
            1  # Grid charging allowed for automated dispatch? [0/1]
        )
        self.batt_dispatch_charge_only_system_exceeds_load = 0  # Battery can charge from system only when system output exceeds load [0/1]
        self.batt_dispatch_discharge_only_load_exceeds_system = 0  # Battery can discharge battery only when load exceeds system output [0/1]
        self.batt_cycle_cost_choice = 5  # Use SAM cost model for degradaton penalty or input custom via batt_cycle_cost [0/1], Options: 0=UseCostModel,1=InputCost
        self.batt_cycle_cost = [
            0.1
        ]  # Input battery cycle degradaton penalty per year [$/cycle-kWh]
