import warnings

import requests


class AuroraSolarSim_API:
    """Container for accessing PV simulation data through the Aurora API

    Constructor Parameters:
        1.) base_url : <str>
                URL for the aurora solar web api
        2.) tenent_id: <str>
                String identifier corresponding to the Tenent id
        3.) token: <str>
                String identifier corresponding to the Aurora product key
        4.) design_id: <str>
                String identifier corrsponding to the design_id
    """

    def __init__(
        self,
        base_url=None,
        tenant_id=None,
        token=None,
        design_id=None,
    ):
        # set information (private)
        assert all([
            base_url is not None,
            tenant_id is not None,
            token is not None,
            design_id is not None,
        ]), "Missing inputs for the Base URL/Tenent ID/Token"
        self._base_url = base_url
        self._tenant_id = tenant_id
        self._token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._url_prefix = f"{base_url}/tenants/{tenant_id}"
        self.update(design_id)

    def update(self, design_id):
        self._design_id = design_id
        self.set_design_url(design_id)
        self._design_summary = self.get_design_summary_from_webserver()
        self.set_project_id()
        self.set_project_url(self.get_project_id())
        self._project_summary = self.get_project_summary_from_webserver()
        self._consumption_profile = (
            self.get_consumption_profile_from_webserver()
        )
        self._latitude = self.set_latitude()
        self._longitude = self.set_longitude()
        self._bom = self.set_bill_of_materials()

        self.create_dicts_from_bom()
        self.set_arrays_list()
        self.set_string_inv_quantity()
        self.set_num_arrays()
        self.set_inverter_type()
        self.set_storage_inverters_dict()
        self.set_dc_optimizers_quantity()

    def set_latitude(self):
        return self.get_project_summary()["latitude"]

    def get_latitude(self):
        return self._latitude

    def set_longitude(self):
        return self.get_project_summary()["longitude"]

    def get_longitude(self):
        return self._longitude

    def set_design_url(self, design_id):
        self._design_url = f"{self._url_prefix}/designs/{design_id}"

    def get_design_url(self):
        return self._design_url

    def request_info_from_webserver(self, url):
        try:
            response = requests.get(url, headers=self.get_aurora_headers())
            if response.status_code != 200:
                error_type = ""  # default error type is an empty string
                error_message = response.text.split('"message":')[1].rstrip(
                    "}]}"
                )
                if response.status_code == 404:
                    if "Consumption" in error_message:
                        error_type = "Consumption Profile"
                    # Add other checks in else/elif blocks in the future
                    raise Exception(
                        f"Aurora API {error_type} error: {error_message}"
                    )
                # Add other status code checks in elif blocks in the future
                # default handling
                else:
                    raise (
                        Exception(
                            "Aurora Design Pricing API error:"
                            f" {response.status_code} | {response.text}"
                        )
                    )
        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {e}")

        return response.json()

    def get_design_summary_from_webserver(self):
        import json

        result = self.request_info_from_webserver(
            f"{self.get_design_url()}/summary"
        )
        if type(result) == dict:
            return result["design"]
        elif type(result) == str:
            return json.loads(result)["design"]

    def get_design_summary(self):
        return self._design_summary

    def set_project_id(self):
        self._project_id = self._design_summary["project_id"]

    def get_project_id(self):
        return self._project_id

    def set_project_url(self, project_id):
        self._project_url = f"{self._url_prefix}/projects/{project_id}"

    def get_project_url(self):
        return self._project_url

    def get_project_summary_from_webserver(self):
        return self.request_info_from_webserver(f"{self.get_project_url()}")[
            "project"
        ]

    def get_project_summary(self):
        return self._project_summary

    def get_consumption_profile_from_webserver(self):
        return self.request_info_from_webserver(
            f"{self.get_consumption_profile_url()}"
        )["consumption_profile"]

    def get_consumption_profile(self):
        return self._consumption_profile

    def get_consumption_profile_url(self):
        return f"{self.get_project_url()}/consumption_profile"

    def get_design_id(self):
        return self._design_id

    def get_base_url(self):
        return self._base_url

    def get_tenant_id(self):
        return self._tenant_id

    def get_aurora_headers(self):
        return self._headers

    def get_lat_lon_tuple(self):
        return tuple((
            self.get_longitude(),
            self.get_latitude(),
        ))

    def set_bill_of_materials(self):
        return self.get_design_summary()["bill_of_materials"]

    def get_bill_of_materials(self):
        return self._bom

    def create_dicts_from_bom(self):
        self._modules_dict = self._inverters_dict = self._batteries_dict = (
            self._microinverters_dict
        ) = self._dc_optimizers_dict = None

        for dictionary in self.get_bill_of_materials():
            if dictionary["component_type"] == "modules":
                self._modules_dict = dictionary
            if dictionary["component_type"] in ["inverters", "microinverters"]:
                self._inverters_dict = dictionary
                if dictionary["component_type"] == "microinverters":
                    self._microinverters_dict = dictionary
            if dictionary["component_type"] == "batteries":
                self._batteries_dict = dictionary
            if dictionary["component_type"] == "dc_optimizers":
                self._dc_optimizers_dict = dictionary

        # ASSUMPTION: if the design has both an inverter and microinverter, the inverter is taken to be a storage inverter
        # and the inverter parameters are given by the microinverter
        try:
            if (
                self._inverters_dict["component_type"] == "inverters"
                and self._microinverters_dict["component_type"]
                == "microinverters"
            ):
                self._inverters_dict = self._microinverters_dict
        except Exception:
            pass

        design_missing_modules = self._modules_dict is None
        design_missing_inverters_and_microinverters = (
            self._inverters_dict is None and self._microinverters_dict is None
        )
        design_missing_batteries = self._batteries_dict is None

        if design_missing_modules:
            raise AttributeError("Design does not specify a Modules")

        if design_missing_inverters_and_microinverters:
            raise AttributeError(
                "Design does not specify Inverters or Microinverters"
            )

        if design_missing_batteries:
            self._batteries_dict = dict({"id": "", "name": "", "quantity": 0})

    def get_modules_dict(self):
        return self._modules_dict

    def get_module_id(self):
        return self.get_modules_dict()["id"]

    def get_module_name(self):
        return self.get_modules_dict()["name"]

    def get_module_quantity(self):
        return self.get_modules_dict()["quantity"]

    def get_inverters_dict(self):
        return self._inverters_dict

    def set_storage_inverters_dict(self):
        try:
            self.storage_inv = self._design_summary["storage_inverters"].pop()
        except:
            self.storage_inv = None

    def get_storage_inverters_dict(self):
        return self.storage_inv

    def get_inverter_id(self):
        return self.get_inverters_dict()["id"]

    def get_inverter_name(self):
        return self.get_inverters_dict()["name"]

    def get_inverter_count(self):
        return (
            self.get_inverters_dict()["quantity"]
            if self.get_string_inv_quantity() == 0
            else self.get_string_inv_quantity()
        )

    def set_string_inv_quantity(self):
        inv_type = self.get_inverter_type()
        assert inv_type in ["inverters", "microinverters"], (
            "The Aurora design is missing either string inverters or"
            " microinverters"
        )
        try:
            string_inv_qty = (
                len(self.get_design_summary()["string_inverters"])
                if inv_type == "inverters"
                else 0
            )
        except Exception as exception:
            assert False, (
                f"Design Summary of Design id '{self.get_design_id()}' does"
                " not have 'string_inverters' key."
            )

        if inv_type == "inverters":
            assert string_inv_qty > 0, (
                "SAM requires"
                " len(self.get_design_summary()['string_inverters']) to be"
                " positive [equivalent to pvsamv1 execution error."
                " fail(inverter_count,positive): 0]"
            )

        self.string_inv_qty = string_inv_qty

    def get_string_inv_quantity(self):
        return self.string_inv_qty

    def set_inverter_type(self):
        self.inv_type = self.get_inverter_type()

    def get_inverter_type(self):
        return self.get_inverters_dict()["component_type"]

    def get_batteries_dict(self):
        return self._batteries_dict

    def get_batteries_id(self):
        return self.get_batteries_dict()["id"]

    def get_batteries_name(self):
        return self.get_batteries_dict()["name"]

    def get_batteries_quantity(self):
        return self.get_batteries_dict()["quantity"]

    def get_microinverters_dict(self):
        return self._microinverters_dict

    def get_microinverters_name(self):
        return (
            self.get_microinverters_dict()["name"]
            if self._microinverters_dict
            else ""
        )

    def get_microinverters_quantity(self):
        return (
            self.get_microinverters_dict()["quantity"]
            if self._microinverters_dict
            else ""
        )

    def set_dc_optimizers_quantity(self):
        self._dc_optimizers_dict = self.get_dc_optimizers_dict()
        if self._dc_optimizers_dict:
            self.dc_opt_quantity = self._dc_optimizers_dict["quantity"]
        else:
            self.dc_opt_quantity = 0

    def get_dc_optimizers_dict(self):
        return self._dc_optimizers_dict

    def get_dc_optimizers_name(self):
        return (
            self._dc_optimizers_dict["name"]
            if self._dc_optimizers_dict
            else ""
        )

    def get_dc_optimizers_quantity(self):
        return self.dc_opt_quantity

    def get_component_type(self):
        component_type = None
        for dictionary in self.get_bill_of_materials():
            if dictionary["component_type"] == "inverters":
                component_type = dictionary["component_type"]
                break
            if dictionary["component_type"] in [
                "microinverters",
                "dc_optimizers",
            ]:
                component_type = dictionary["component_type"]
                break
        return component_type

    def set_arrays_list(self):
        try:
            self._arrays_list = self.get_design_summary()["arrays"]
        except KeyError:
            warnings.warn("No 'arrays' key found in design summary.")
            with open("batchruns_warning_logs", "a") as f:
                f.write(
                    "No 'arrays' key found in design summary for design id"
                    f" {self._design_id}.\n"
                )
            self._arrays_list = ""

    def get_array_list(self):
        return self._arrays_list

    def set_num_arrays(self):
        self.num_arrays = self.get_num_arrays()

    def get_num_arrays(self):
        return len(self._arrays_list)

    def get_address(self):
        return self.get_project_summary()["address"]

    def get_utility_name(self):
        return self.get_consumption_profile()["utility"]

    def get_utility_rate_version_id(self):
        return self.get_consumption_profile()["utility_rate_version_id"]
