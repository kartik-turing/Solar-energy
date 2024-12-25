from decimal import Decimal
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.api.models import (
    DesignDetails,
    DesignSourceEnum,
    EnergyProductionAnnual,
    EnergyProductionHourly,
    EnergyProductionMonth,
    SimulationAPIResponse,
    SimulationAPIResponseDetailed,
    SimulationSourceEnum,
)
from app.api.utils.component_extractor import Components
from app.api.utils.logger import logger


def create_job_result_response(
    designId,
    tenantId,
    simulationJobId,
    SimulationTime,
    pvsim,
    outputResolution,
    simulationYears,
    start_timestamp,
    detailed=False,
):

    numBatteries = pvsim.runner.aurora_api.get_batteries_quantity()
    batterySize = []

    aggregated_component_parameters = Components.extract_agg_components(
        pvsim,
        simulationJobId,
        str(start_timestamp),
        tenantId,
        designId,
        1,
    )
    batterySize = []
    if aggregated_component_parameters:
        if aggregated_component_parameters["batteryName"]:
            batterySize.append(aggregated_component_parameters["batteryName"])
        if aggregated_component_parameters["batteryCount"]:
            batterySize.append(aggregated_component_parameters["batteryCount"])
        if aggregated_component_parameters["battPowerChargeMaxKwac"]:
            batterySize.append(
                aggregated_component_parameters["battPowerChargeMaxKwac"]
            )
        if aggregated_component_parameters["battPowerDischargeMaxKwac"]:
            batterySize.append(
                aggregated_component_parameters["battPowerDischargeMaxKwac"]
            )
        if aggregated_component_parameters["battComputedBankCapacity"]:
            batterySize.append(
                aggregated_component_parameters["battComputedBankCapacity"]
            )

    design_details = DesignDetails(
        systemSize=pvsim.system_capacity,
        numBatteries=numBatteries,
        batterySize=batterySize,
        estimatedAvoidedCost=sum(
            pvsim.utility.Outputs.year1_monthly_utility_bill_wo_sys
        )
        - sum(pvsim.utility.Outputs.year1_monthly_utility_bill_w_sys),
    )

    if outputResolution.lower() == "year":
        energy_production = EnergyProductionAnnual(
            annual=[pvsim.pv.Outputs.annual_energy] * simulationYears,
        )
    elif outputResolution.lower() == "month":
        energy_production = EnergyProductionMonth(
            annual=[pvsim.pv.Outputs.annual_energy] * simulationYears,
            monthly=list(pvsim.pv.Outputs.monthly_energy) * simulationYears,
        )

    elif outputResolution.lower() == "hour":
        energy_production = EnergyProductionHourly(
            annual=[pvsim.pv.Outputs.annual_energy],
            monthly=list(pvsim.pv.Outputs.monthly_energy),
            hourly=list(pvsim.pv.Outputs.gen),
        )
    else:
        energy_production = None

    try:
        if detailed == True:
            job_result_response = SimulationAPIResponseDetailed(
                designSource=DesignSourceEnum.Aurora,
                simulationSource=SimulationSourceEnum.Qcells,
                simulationJobId=simulationJobId,
                simulationRunDuration=SimulationTime,
                designDetails=design_details,
                energyProduction=energy_production,
                aggregated_component_params=aggregated_component_parameters,
            )
        else:
            job_result_response = SimulationAPIResponse(
                designSource=DesignSourceEnum.Aurora,
                simulationSource=SimulationSourceEnum.Qcells,
                simulationJobId=simulationJobId,
                simulationRunDuration=SimulationTime,
                designDetails=design_details,
                energyProduction=energy_production,
            )
        return jsonable_encoder(
            job_result_response.__dict__,
            custom_encoder={
                Decimal: lambda d: float(d),
                BaseModel: lambda b: jsonable_encoder(
                    b.dict().items(),
                    custom_encoder={Decimal: lambda d: float(d)},
                ),
            },
        )
    except Exception as exception:
        logger.error(
            f"An error occurred in building Job Response. {str(exception)}"
        )
        raise
