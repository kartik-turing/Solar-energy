import json
import re
from typing import DefaultDict
from app.api.models import AggregatedComponentParams


class Components:
    @classmethod
    def add_runner_params(cls, components, pvsim):

        microinverter_name = pvsim.runner.aurora_api.get_microinverters_name()
        if microinverter_name:
            cls.microinverter_name = microinverter_name
            cls.microinverter_qty = (
                pvsim.runner.aurora_api.get_microinverters_quantity()
            )
            cls.inverter_name = ""
            cls.inverter_qty = None
        else:
            cls.inverter_name = pvsim.runner.aurora_api.get_inverter_name()
            cls.inverter_qty = pvsim.runner.aurora_api.get_inverter_count()
            cls.microinverter_name = ""
            cls.microinverter_qty = None
        # add runner battery params
        batt_params_dict = {
            "batt_ac_or_dc": "batteryAcOrDcCoupled",
            "batt_power_charge_max_kwac": "battPowerChargeMaxKwac",
            "batt_power_discharge_max_kwac": "battPowerDischargeMaxKwac",
            "batt_computed_bank_capacity": "battComputedBankCapacity",
        }
        for key, val in batt_params_dict.items():
            if key == "batt_ac_or_dc":
                try:
                    value = (
                        "AC"
                        if getattr(pvsim.runner.battery, key) == 1
                        else "DC"
                    )
                except:
                    value = None
            else:
                try:
                    value = getattr(pvsim.runner.battery, key)
                except:
                    value = None

            components.update({val: value})

    @classmethod
    def extract_agg_components(
        cls,
        pvsim,
        simulationJobId,
        timestamp,
        tenantID,
        designID,
        status,
        detail=None,
    ):

        components = DefaultDict()
        cls.add_runner_params(components, pvsim)
        system_design = pvsim.runner.system_design
        arrays = pvsim.runner.aurora_api.get_array_list()

        JobStatus = (
            detail if detail == "SUCCESS" else (status if status else "FAILED")
        )

        # fetch state and zipcode using regex
        pattern = r"([A-Z]{2})\s+(\d{5})"

        address = pvsim.runner.aurora_api.get_address()

        match = re.search(pattern, address)

        state = None
        zipcode = None
        if match:
            state = match.group(1)
            zipcode = match.group(2)

        components.update({
            "jobRunTime": str(timestamp),
            "jobId": simulationJobId,
            "jobStatus": JobStatus,
            "tenantId": tenantID,
            "designId": designID,
            "state": state,
            "zipcode": zipcode,
            "moduleName": pvsim.runner.aurora_api.get_module_name(),
            "moduleCount": pvsim.runner.aurora_api.get_module_quantity(),
            "inverterName": cls.inverter_name,
            "inverterCount": cls.inverter_qty,
            "microinverterName": cls.microinverter_name,
            "microinverterCount": cls.microinverter_qty,
            "dcOptimizerName": (
                pvsim.runner.aurora_api.get_dc_optimizers_name()
            ),
            "dcOptimizerCount": (
                pvsim.runner.aurora_api.get_dc_optimizers_quantity()
            ),
            "batteryName": pvsim.runner.aurora_api.get_batteries_name(),
            "batteryCount": pvsim.runner.aurora_api.get_batteries_quantity(),
            "systemCapacity": pvsim.system_capacity,
        })

        components.update({
            "auroraAnnualProduction": (
                pvsim.runner.aurora_api.get_design_summary()[
                    "energy_production"
                ]["annual"]
            )
        })
        monthlyProd_aurora = pvsim.runner.aurora_api.get_design_summary()[
            "energy_production"
        ]["monthly"]

        for idx, prod in enumerate(monthlyProd_aurora):
            components.update({f"auroraMonth{idx+1}Production": prod})
        components.update(
            {"numberOfArrays": pvsim.runner.aurora_api.get_num_arrays()}
        )

        for idx, arr in enumerate(arrays):
            if (
                f"subarray{idx+1}_azimuth"
                in system_design._subarray_design_dict
            ):
                components[f"array{idx+1}Azimuth"] = (
                    system_design._subarray_design_dict[
                        f"subarray{idx+1}_azimuth"
                    ]
                )
            else:
                components[f"array{idx+1}Azimuth"] = None

            if f"subarray{idx+1}_tilt" in system_design._subarray_design_dict:
                components[f"array{idx+1}Tilt"] = (
                    system_design._subarray_design_dict[
                        f"subarray{idx+1}_tilt"
                    ]
                )
            else:
                components[f"array{idx+1}Tilt"] = None

            if (
                arr.get("shading", {})
                .get("solar_access", {})
                .get("annual", {})
            ):
                components[f"array{idx+1}AnnualSolarAccess"] = arr["shading"][
                    "solar_access"
                ]["annual"]
            else:
                components[f"array{idx+1}AnnualSolarAccess"] = None
            if (
                arr.get("shading", {})
                .get("total_solar_resource_fraction", {})
                .get("annual", {})
            ):
                components[f"array{idx+1}AnnualTsrf"] = arr["shading"][
                    "total_solar_resource_fraction"
                ]["annual"]
            else:
                components[f"array{idx+1}AnnualTsrf"] = None

        if status:
            JobStatus = "SUCCESS"
            components.update({"jobStatus": JobStatus})
            monthlyProd = pvsim.pv.Outputs.monthly_energy
            annualProd = pvsim.pv.Outputs.annual_energy
            components.update({"pysamAnnualProduction": annualProd})
            for idx, prod in enumerate(monthlyProd):
                components.update({f"pysamMonth{idx+1}Production": prod})
            # add pvsim Outputs params
            pvsim_outputs = {
                "kwh_per_kw": "kwhPerKw",
                "annual_ac_battery_loss_percent": "annualAcBatteryLossPercent",
                "annual_ac_inv_clip_loss_percent": (
                    "annualAcInvClipLossPercent"
                ),
                "annual_ac_inv_eff_loss_percent": "annualAcInvEffLossPercent",
                "annual_ac_inv_pnt_loss_percent": "annualAcInvPntLossPercent",
                "annual_ac_inv_pso_loss_percent": "annualAcInvPsoLossPercent",
                "annual_ac_lifetime_loss_percent": (
                    "annualAcLifetimeLossPercent"
                ),
                "annual_ac_perf_adj_loss_percent": (
                    "annualAcPerfAdjLossPercent"
                ),
                "annual_ac_wiring_loss_percent": "annualAcWiringLossPercent",
                "annual_dc_battery_loss_percent": "annualDcBatteryLossPercent",
                "annual_dc_diodes_loss_percent": "annualDcDiodesLossPercent",
                "annual_dc_lifetime_loss_percent": (
                    "annualDcLifetimeLossPercent"
                ),
                "annual_dc_inv_tdc_loss_percent": "annualDcInvTdcLossPercent",
                "annual_dc_mismatch_loss_percent": (
                    "annualDcMismatchLossPercent"
                ),
                "annual_dc_module_loss_percent": "annualDcModuleLossPercent",
                "annual_dc_mppt_clip_loss_percent": (
                    "annualDcMpptClipLossPercent"
                ),
                "annual_dc_nameplate_loss_percent": (
                    "annualDcNameplateLossPercent"
                ),
                "annual_dc_optimizer_loss_percent": (
                    "annualDcOptimizerLossPercent"
                ),
                "annual_dc_perf_adj_loss_percent": (
                    "annualDcPerfAdjLossPercent"
                ),
                "annual_dc_snow_loss_percent": "annualDcSnowLossPercent",
                "annual_dc_tracking_loss_percent": (
                    "annualDcTrackingLossPercent"
                ),
                "annual_dc_wiring_loss_percent": "annualDcWiringLossPercent",
                "annual_distribution_clipping_loss_percent": (
                    "annualDistributionClippingLossPercent"
                ),
                "annual_poa_cover_loss_percent": "annualPoaCoverLossPercent",
                "annual_poa_shading_loss_percent": (
                    "annualPoaShadingLossPercent"
                ),
                "annual_poa_soiling_loss_percent": (
                    "annualPoaSoilingLossPercent"
                ),
                "annual_subhourly_clipping_loss_percent": (
                    "annualSubhourlyClippingLossPercent"
                ),
                "annual_total_loss_percent": "annualTotalLossPercent",
                "annual_transmission_loss_percent": (
                    "annualTransmissionLossPercent"
                ),
                "annual_xfmr_loss_percent": "annualXfmrLossPercent",
                "annual_ac_gross": "annualAcGross",
                "annual_dc_gross": "annualDcGross",
                "annual_poa_eff": "annualPoaEff",
            }

            for k, v in pvsim_outputs.items():
                try:
                    value = getattr(pvsim.pv.Outputs, k)

                except:
                    value = None
                components.update({v: value})

        return json.loads(AggregatedComponentParams(**components).json())
