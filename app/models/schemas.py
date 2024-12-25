from decimal import Decimal
from typing import List, Union

from pydantic import BaseModel, Extra, root_validator


class ModuleTable(BaseModel):
    mod_length: Decimal
    mod_width: Decimal
    cec_bifacial_transmission_factor: int
    cec_bifaciality: int
    cec_bifacial_ground_clearance_height: int
    cec_standoff: int
    cec_height: int
    cec_transient_thermal_model_unit_mass: Decimal
    annual_degradation: List[Decimal]
    id: str

    @root_validator(pre=True)
    def validate_annual_degradation(cls, values):
        annual_degradation = values.get("annual_degradation")
        if annual_degradation:
            if len(annual_degradation) > 35:
                raise ValueError(
                    "The list of annual_degradation values cannot contain more"
                    " than 35 items. Please reduce the number of items in the"
                    " list."
                )
            if not all(0 <= value <= 100 for value in annual_degradation):
                raise ValueError(
                    "All values in the annual_degradation list must be between"
                    " 0 and 100, inclusive. Please ensure all values are"
                    " within this range."
                )
            return values

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = False


class InverterTable(BaseModel):
    inv_tdc_cec_db: str
    inv_snl_eff_cec: Decimal
    id: str

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = False


class BatteryTable(BaseModel):
    en_batt: int
    batt_ac_dc_efficiency: Decimal
    batt_dc_ac_efficiency: Decimal
    batt_dc_dc_efficiency: Decimal
    batt_ac_or_dc: int
    batt_computed_bank_capacity: Decimal
    batt_power_charge_max_kwdc: Decimal
    batt_power_charge_max_kwac: Decimal
    batt_power_discharge_max_kwdc: Decimal
    batt_power_discharge_max_kwac: Decimal
    batt_meter_position: int
    batt_computed_series: int
    batt_computed_strings: int
    batt_surface_area: Decimal
    batt_mass: Decimal
    batt_current_charge_max: Decimal
    batt_current_discharge_max: Decimal
    batt_replacement_capacity: int
    batt_replacement_option: int
    batt_inverter_efficiency_cutoff: int
    batt_current_choice: int
    batt_chem: int
    batt_lifetime_matrix: List[List[Decimal]]
    batt_calendar_choice: List[int]
    batt_calendar_q0: List[Decimal]
    batt_calendar_a: List[Decimal]
    batt_calendar_b: int
    batt_calendar_c: int
    batt_voltage_matrix: List[List[int]]
    batt_Vfull: Decimal
    batt_Vexp: List[Decimal]
    batt_Vnom_default: List[Decimal]
    batt_Vnom: List[Decimal]
    batt_Vcut: Decimal
    batt_Qfull_flow: int
    batt_Qfull: Decimal
    batt_Qnom: int
    batt_Qexp: Decimal
    batt_C_rate: Decimal
    batt_life_model: int
    batt_initial_SOC: int
    batt_maximum_SOC: int
    batt_minimum_SOC: List[int]
    batt_minimum_outage_SOC: List[int]
    batt_minimum_modetime: int
    batt_resistance: Decimal
    batt_h_to_ambient: List[Decimal]
    batt_Cp: int
    batt_room_temperature_celsius: List[Union[int, Decimal]]
    cap_vs_temp: List[List[Union[Decimal, int]]]
    batt_calendar_lifetime_matrix: List[List[Union[Decimal, int]]]
    batt_voltage_choice: int
    id: str

    class Config:
        arbitrary_types_allowed = False
        extra = Extra.forbid
        smart_union = True
