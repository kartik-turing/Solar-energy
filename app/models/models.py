import datetime
import logging
import os
from typing import Optional

from sqlalchemy import (
    ARRAY,
    Column,
    Float,
    Integer,
    Numeric,
    String,
    delete,
    select,
    update,
)
from sqlalchemy.orm import scoped_session

from app.models.conn import Base, Session
from app.models.schemas import BatteryTable, InverterTable, ModuleTable

session = Session()


class Logging(logging.FileHandler):
    def __init__(self, filename: Optional[str] = None):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)


logger = Logging()


class Interface:
    @classmethod
    def get_all(cls):
        try:
            results = session.execute(select(cls)).scalars().all()
            logger.log_info(f"Get {cls.__name__} Query executed successfully")
            return results
        except Exception as exception:
            logger.log_error(
                f"Error in Get All {cls.__tablename__}: {str(exception)}"
            )
            session.rollback()
            raise exception
        finally:
            session.close()

    @classmethod
    def get_component(cls, id: str):
        _scoped_session = scoped_session(Session)
        with _scoped_session() as session_local:
            try:
                result = session_local.execute(
                    select(cls).where(cls.id == id)
                ).scalar_one_or_none()

                logger.log_info(f"Get {id} Query executed successfully")
                return result

            except Exception as exception:
                logger.log_error(f"Error in Get {id}: {str(exception)}")
                session_local.rollback()
                raise exception

            finally:
                session_local.close()

    @classmethod
    def update(cls, data, id: Optional[str] = None):
        if not isinstance(data,dict):
            data_dict = data.__dict__
        else:
            data_dict = data
        if id is None:
            id = data_dict["id"]
        update_values = {}
        for attr,val in data_dict.items():
            if not attr.startswith("_"):
                if not callable(val):
                    update_values[attr] = val
        if update_values:
            try:
                session.execute(
                    update(cls).where(cls.id == id).values(update_values)
                )
                session.commit()
                logger.log_info(f"Update {id} Query executed successfully")

            except Exception as e:
                logger.log_error(f"Error in Update {id}: {str(e)}")
                session.rollback()
                raise e

            finally:
                session.close()

    @classmethod
    def delete(cls, component_id):
        component = cls.get_component(component_id)
        if component != None:
            try:
                session.execute(delete(cls).where(cls.id == component_id))
                session.commit()
            except Exception as e:
                session.rollback()
            finally:
                session.close()
            return "Delete Successful"
        else:
            return None


class Module(Base, Interface):
    __tablename__ = "Modules Table Dev"
    id = Column(String, primary_key=True, doc="Id")
    mod_length = Column(Numeric, nullable=False, doc="Mod Length")
    mod_width = Column(Numeric, nullable=False, doc="Mod Width")
    cec_bifacial_transmission_factor = Column(
        Numeric, nullable=False, doc="Cec Bifacial Transmission Factor"
    )
    cec_bifaciality = Column(Numeric, nullable=False, doc="Cec Bifaciality")
    cec_bifacial_ground_clearance_height = Column(
        Numeric, nullable=False, doc="Cec Bifacial Ground Clearance Height"
    )
    cec_standoff = Column(Numeric, nullable=False, doc="Cec Standoff")
    cec_height = Column(Numeric, nullable=False, doc="Cec height")
    cec_transient_thermal_model_unit_mass = Column(
        Numeric, nullable=False, doc="Cec Transient Thermal Model Unit Mass"
    )
    annual_degradation = Column(
        ARRAY(Numeric), nullable=False, doc="Annual Degradation"
    )

    def __init__(
        self,
        id,
        mod_length,
        mod_width,
        cec_bifacial_transmission_factor,
        cec_bifaciality,
        cec_bifacial_ground_clearance_height,
        cec_standoff,
        cec_height,
        cec_transient_thermal_model_unit_mass,
        annual_degradation,
    ):
        self.id = id
        self.mod_length = mod_length
        self.mod_width = mod_width
        self.cec_bifacial_transmission_factor = (
            cec_bifacial_transmission_factor
        )
        self.cec_bifaciality = cec_bifaciality
        self.cec_bifacial_ground_clearance_height = (
            cec_bifacial_ground_clearance_height
        )
        self.cec_standoff = cec_standoff
        self.cec_height = cec_height
        self.cec_transient_thermal_model_unit_mass = (
            cec_transient_thermal_model_unit_mass
        )
        self.annual_degradation = annual_degradation

    @classmethod
    def addModule(cls, module: ModuleTable):
        present = cls.get_component(module.id)
        if not present:
            try:
                session.add(Module(**module.dict()))
                session.commit()
                logger.log_info(
                    f"Write {module.id} Query executed successfully"
                )

            except Exception as exception:
                session.rollback()
                logger.log_error(
                    f"Error in Write {module.id}: {str(exception)}"
                )
                raise exception
            finally:
                session.close()

        else:
            cls.update(module)


class Inverter(Base, Interface):
    __tablename__ = "Inverters Table Dev"
    id = Column(String, primary_key=True, doc="Id")
    inv_tdc_cec_db = Column(String, nullable=False, doc="Inv Tdc Cec Db")
    inv_snl_eff_cec = Column(Float, nullable=False, doc="Inv Snl Eff Cec")

    def __init__(self, id, inv_tdc_cec_db, inv_snl_eff_cec):
        self.id = id
        self.inv_tdc_cec_db = inv_tdc_cec_db
        self.inv_snl_eff_cec = inv_snl_eff_cec

    @classmethod
    def addInverter(cls, inverter: InverterTable):
        present = cls.get_component(inverter.id)
        if not present:
            try:
                session.add(Inverter(**inverter.dict()))
                session.commit()
                logger.log_info(
                    f"Write {inverter.id} Query executed successfully"
                )
            except Exception as exception:
                session.rollback()
                logger.log_error(
                    f"Error in Write {inverter.id}: {str(exception)}"
                )
                raise exception
            finally:
                session.close()
        else:
            cls.update(inverter)


class Battery(Base, Interface):
    __tablename__ = "Batteries Table Dev"
    id = Column(String, primary_key=True, doc="id")
    en_batt = Column(Integer, nullable=False, doc="En Batt")
    batt_ac_dc_efficiency = Column(
        Numeric, nullable=False, doc="Batt Ac Dc Efficiency"
    )
    batt_dc_ac_efficiency = Column(
        Numeric, nullable=False, doc="Batt Dc Ac Efficiency"
    )
    batt_dc_dc_efficiency = Column(
        Numeric, nullable=False, doc="Batt Dc Dc Efficiency"
    )
    batt_ac_or_dc = Column(Integer, nullable=False, doc="Batt Ac Or Dc")
    batt_computed_bank_capacity = Column(
        Float, nullable=False, doc="Batt Computed Bank Capacity"
    )
    batt_power_charge_max_kwdc = Column(
        Float, nullable=False, doc="Batt Power Charge Max Kwdc"
    )
    batt_power_charge_max_kwac = Column(
        Float, nullable=False, doc="Batt Power Charge Max Kwac"
    )
    batt_power_discharge_max_kwdc = Column(
        Float, nullable=False, doc="Batt Power Discharge Max Kwdc"
    )
    batt_power_discharge_max_kwac = Column(
        Float, nullable=False, doc="Batt Power Discharge Max Kwac"
    )
    batt_meter_position = Column(
        Integer, nullable=False, doc="Batt Meter Position"
    )
    batt_computed_series = Column(
        Integer, nullable=False, doc="Batt Computed Series"
    )
    batt_computed_strings = Column(
        Integer, nullable=False, doc="Batt Computed Strings"
    )
    batt_surface_area = Column(Float, nullable=False, doc="Batt Surface Area")
    batt_mass = Column(Float, nullable=False, doc="Batt Mass")
    batt_current_charge_max = Column(
        Float, nullable=False, doc="Batt Current Charge Max"
    )
    batt_current_discharge_max = Column(
        Float, nullable=False, doc="Batt Current Discharge Max"
    )
    batt_replacement_capacity = Column(
        Integer, nullable=False, doc="Batt Replacement Capacity"
    )
    batt_replacement_option = Column(
        Integer, nullable=False, doc="Batt Replacement Option"
    )
    batt_inverter_efficiency_cutoff = Column(
        Float, nullable=False, doc="Batt Inverter Efficiency Cutoff"
    )
    batt_current_choice = Column(
        Integer, nullable=False, doc="Batt Current Choice"
    )
    batt_chem = Column(Integer, nullable=False, doc="Batt Chem")
    batt_lifetime_matrix = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Lifetime Matrix"
    )
    batt_calendar_choice = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Calendar Choice"
    )
    batt_calendar_q0 = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Calendar Q0"
    )
    batt_calendar_a = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Calendar A"
    )
    batt_calendar_b = Column(Numeric, nullable=False, doc="Batt Calendar B")
    batt_calendar_c = Column(Numeric, nullable=False, doc="Batt Calendar C")
    batt_voltage_matrix = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Voltage Matrix"
    )
    batt_Vfull = Column(Numeric, nullable=False, doc="Batt Vfull")
    batt_Vexp = Column(ARRAY(Numeric), nullable=False, doc="Batt Vexp")
    batt_Vnom_default = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Vnom Default"
    )
    batt_Vnom = Column(ARRAY(Numeric), nullable=False, doc="Batt Vnom")
    batt_Vcut = Column(Numeric, nullable=False, doc="Batt Vcut")
    batt_Qfull_flow = Column(Numeric, nullable=False, doc="Batt Qfull Flow")
    batt_Qfull = Column(Numeric, nullable=False, doc="Batt Qfull")
    batt_Qnom = Column(Numeric, nullable=False, doc="Batt Qnom")
    batt_Qexp = Column(Numeric, nullable=False, doc="Batt Qexp")
    batt_C_rate = Column(Numeric, nullable=False, doc="Batt C Rate")
    batt_life_model = Column(Numeric, nullable=False, doc="Batt Life Model")
    batt_initial_SOC = Column(Numeric, nullable=False, doc="Batt Initial Soc")
    batt_maximum_SOC = Column(Numeric, nullable=False, doc="Batt Maximum Soc")
    batt_minimum_SOC = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Minimum Soc"
    )
    batt_minimum_outage_SOC = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Minimum Outage Soc"
    )
    batt_minimum_modetime = Column(
        Numeric, nullable=False, doc="Batt Minimum Modetime"
    )
    batt_resistance = Column(Numeric, nullable=False, doc="Batt Resistance")
    batt_h_to_ambient = Column(
        ARRAY(Numeric), nullable=False, doc="Batt H To Ambient"
    )
    batt_Cp = Column(Numeric, nullable=False, doc="Batt Cp")
    batt_room_temperature_celsius = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Room Temperature Celsius"
    )
    cap_vs_temp = Column(ARRAY(Numeric), nullable=False, doc="Cap Vs Temp")
    batt_calendar_lifetime_matrix = Column(
        ARRAY(Numeric), nullable=False, doc="Batt Calendar Lifetime Matrix"
    )
    batt_voltage_choice = Column(
        Numeric, nullable=False, doc="Batt Voltage Choice"
    )

    def __init__(
        self,
        id,
        en_batt,
        batt_ac_dc_efficiency,
        batt_dc_ac_efficiency,
        batt_dc_dc_efficiency,
        batt_ac_or_dc,
        batt_computed_bank_capacity,
        batt_power_charge_max_kwdc,
        batt_power_charge_max_kwac,
        batt_power_discharge_max_kwdc,
        batt_power_discharge_max_kwac,
        batt_meter_position,
        batt_computed_series,
        batt_computed_strings,
        batt_surface_area,
        batt_mass,
        batt_current_charge_max,
        batt_current_discharge_max,
        batt_replacement_capacity,
        batt_replacement_option,
        batt_inverter_efficiency_cutoff,
        batt_current_choice,
        batt_chem,
        batt_lifetime_matrix,
        batt_calendar_choice,
        batt_calendar_q0,
        batt_calendar_a,
        batt_calendar_b,
        batt_calendar_c,
        batt_voltage_matrix,
        batt_Vfull,
        batt_Vexp,
        batt_Vnom_default,
        batt_Vnom,
        batt_Vcut,
        batt_Qfull_flow,
        batt_Qfull,
        batt_Qnom,
        batt_Qexp,
        batt_C_rate,
        batt_life_model,
        batt_initial_SOC,
        batt_maximum_SOC,
        batt_minimum_SOC,
        batt_minimum_outage_SOC,
        batt_minimum_modetime,
        batt_resistance,
        batt_h_to_ambient,
        batt_Cp,
        batt_room_temperature_celsius,
        cap_vs_temp,
        batt_calendar_lifetime_matrix,
        batt_voltage_choice,
    ):
        self.id = id
        self.en_batt = en_batt
        self.batt_ac_dc_efficiency = batt_ac_dc_efficiency
        self.batt_dc_ac_efficiency = batt_dc_ac_efficiency
        self.batt_dc_dc_efficiency = batt_dc_dc_efficiency
        self.batt_ac_or_dc = batt_ac_or_dc
        self.batt_computed_bank_capacity = batt_computed_bank_capacity
        self.batt_power_charge_max_kwdc = batt_power_charge_max_kwdc
        self.batt_power_charge_max_kwac = batt_power_charge_max_kwac
        self.batt_power_discharge_max_kwdc = batt_power_discharge_max_kwdc
        self.batt_power_discharge_max_kwac = batt_power_discharge_max_kwac
        self.batt_meter_position = batt_meter_position
        self.batt_computed_series = batt_computed_series
        self.batt_computed_strings = batt_computed_strings
        self.batt_surface_area = batt_surface_area
        self.batt_mass = batt_mass
        self.batt_current_charge_max = batt_current_charge_max
        self.batt_current_discharge_max = batt_current_discharge_max
        self.batt_replacement_capacity = batt_replacement_capacity
        self.batt_replacement_option = batt_replacement_option
        self.batt_inverter_efficiency_cutoff = batt_inverter_efficiency_cutoff
        self.batt_current_choice = batt_current_choice
        self.batt_chem = batt_chem
        self.batt_lifetime_matrix = batt_lifetime_matrix
        self.batt_calendar_choice = batt_calendar_choice
        self.batt_calendar_q0 = batt_calendar_q0
        self.batt_calendar_a = batt_calendar_a
        self.batt_calendar_b = batt_calendar_b
        self.batt_calendar_c = batt_calendar_c
        self.batt_voltage_matrix = batt_voltage_matrix
        self.batt_Vfull = batt_Vfull
        self.batt_Vexp = batt_Vexp
        self.batt_Vnom_default = batt_Vnom_default
        self.batt_Vnom = batt_Vnom
        self.batt_Vcut = batt_Vcut
        self.batt_Qfull_flow = batt_Qfull_flow
        self.batt_Qfull = batt_Qfull
        self.batt_Qnom = batt_Qnom
        self.batt_Qexp = batt_Qexp
        self.batt_C_rate = batt_C_rate
        self.batt_life_model = batt_life_model
        self.batt_initial_SOC = batt_initial_SOC
        self.batt_maximum_SOC = batt_maximum_SOC
        self.batt_minimum_SOC = batt_minimum_SOC
        self.batt_minimum_outage_SOC = batt_minimum_outage_SOC
        self.batt_minimum_modetime = batt_minimum_modetime
        self.batt_resistance = batt_resistance
        self.batt_h_to_ambient = batt_h_to_ambient
        self.batt_Cp = batt_Cp
        self.batt_room_temperature_celsius = batt_room_temperature_celsius
        self.cap_vs_temp = cap_vs_temp
        self.batt_calendar_lifetime_matrix = batt_calendar_lifetime_matrix
        self.batt_voltage_choice = batt_voltage_choice

    @classmethod
    def addBattery(cls, battery: BatteryTable):
        present = cls.get_component(battery.id)
        if not present:
            try:
                session.add(Battery(**battery.dict()))
                session.commit()
                logger.log_info(
                    f"Write {battery.id} Query executed successfully"
                )
            except Exception as exception:
                session.rollback()
                logger.log_error(
                    f"Error in Write {battery.id}: {str(exception)}"
                )
                raise exception
            finally:
                session.close()

        else:
            cls.update(battery)
            session.close()
