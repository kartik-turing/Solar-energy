from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Extra, Field


class PVSimInput(BaseModel):
    designVendorName: str
    designID: str
    tenantID: str
    simulationMode: str
    simulationYears: int
    outputResolution: str

    class Config:
        extra = Extra.forbid


class DesignSourceEnum(str, Enum):
    Aurora = "Aurora"
    Qcells = "Qcells"


class SimulationSourceEnum(str, Enum):
    Qcells = "Qcells"
    Aurora = "Aurora"


class AggregatedComponentParams(BaseModel):
    jobRunTime: str = Field(title="Jobruntime")
    jobId: str = Field(title="Jobid")
    jobStatus: str = Field(title="Jobstatus")
    tenantId: str = Field(title="Tenantid")
    designId: str = Field(title="Designid")
    state: str = Field(title="State")
    zipcode: str = Field(title="Zipcode")
    # Component details
    moduleName: str = Field(title="Modulename")
    moduleCount: int = Field(title="Modulecount")
    inverterName: Optional[str] = Field(title="Invertername")
    inverterCount: Optional[int] = Field(title="Invertercount")
    microinverterName: Optional[str] = Field(title="Microinvertername")
    microinverterCount: Optional[int] = Field(title="Microinvertercount")
    dcOptimizerName: Optional[str] = Field(title="Dcoptimizername")
    dcOptimizerCount: Optional[int] = Field(title="Dcoptimizercount")
    batteryName: Optional[str] = Field(title="Batteryname")
    batteryCount: Optional[int] = Field(title="Batterycount")
    batteryAcOrDcCoupled: Optional[str] = Field(title="Batteryacordccoupled")
    # System details
    systemCapacity: Optional[Decimal] = Field(title="Systemcapacity")
    kwhPerKw: Optional[Decimal] = Field(title="Kwhperkw")

    # Pysam Production (annual and Monthly)
    pysamAnnualProduction: Optional[Decimal] = Field(
        title="Pysamannualproduction"
    )
    pysamMonth1Production: Optional[Decimal] = Field(
        title="Pysammonth1Production"
    )
    pysamMonth2Production: Optional[Decimal] = Field(
        title="Pysammonth2Production"
    )
    pysamMonth3Production: Optional[Decimal] = Field(
        title="Pysammonth3Production"
    )
    pysamMonth4Production: Optional[Decimal] = Field(
        title="Pysammonth4Production"
    )
    pysamMonth5Production: Optional[Decimal] = Field(
        title="Pysammonth5Production"
    )
    pysamMonth6Production: Optional[Decimal] = Field(
        title="Pysammonth6Production"
    )
    pysamMonth7Production: Optional[Decimal] = Field(
        title="Pysammonth7Production"
    )
    pysamMonth8Production: Optional[Decimal] = Field(
        title="Pysammonth8Production"
    )
    pysamMonth9Production: Optional[Decimal] = Field(
        title="Pysammonth9Production"
    )
    pysamMonth10Production: Optional[Decimal] = Field(
        title="Pysammonth10Production"
    )
    pysamMonth11Production: Optional[Decimal] = Field(
        title="Pysammonth11Production"
    )
    pysamMonth12Production: Optional[Decimal] = Field(
        title="Pysammonth12Production"
    )

    auroraAnnualProduction: Decimal = Field(title="Auroraannualproduction")
    auroraMonth1Production: Decimal = Field(title="Auroramonth1Production")
    auroraMonth2Production: Decimal = Field(title="Auroramonth2Production")
    auroraMonth3Production: Decimal = Field(title="Auroramonth3Production")
    auroraMonth4Production: Decimal = Field(title="Auroramonth4Production")
    auroraMonth5Production: Decimal = Field(title="Auroramonth5Production")
    auroraMonth6Production: Decimal = Field(title="Auroramonth6Production")
    auroraMonth7Production: Decimal = Field(title="Auroramonth7Production")
    auroraMonth8Production: Decimal = Field(title="Auroramonth8Production")
    auroraMonth9Production: Decimal = Field(title="Auroramonth9Production")
    auroraMonth10Production: Decimal = Field(title="Auroramonth10Production")
    auroraMonth11Production: Decimal = Field(title="Auroramonth11Production")
    auroraMonth12Production: Decimal = Field(title="Auroramonth12Production")
    numberOfArrays: int = Field(title="Numberofarrays")
    array1Azimuth: Decimal = Field(title="Array1Azimuth")
    array1Tilt: Decimal = Field(title="Array1Tilt")
    array1AnnualSolarAccess: Decimal = Field(title="Array1Annualsolaraccess")
    array1AnnualTsrf: Decimal = Field(title="Array1Annualtsrf")
    array2Azimuth: Optional[Decimal] = Field(
        title="Array2Azimuth", default=None
    )
    array2Tilt: Optional[Decimal] = Field(title="Array2Tilt", default=None)
    array2AnnualSolarAccess: Optional[Decimal] = Field(
        title="Array2Annualsolaraccess", default=None
    )
    array2AnnualTsrf: Optional[Decimal] = Field(
        title="Array2Annualtsrf", default=None
    )
    array3Azimuth: Optional[Decimal] = Field(
        title="Array3Azimuth", default=None
    )
    array3Tilt: Optional[Decimal] = Field(title="Array3Tilt", default=None)
    array3AnnualSolarAccess: Optional[Decimal] = Field(
        title="Array3Annualsolaraccess", default=None
    )
    array3AnnualTsrf: Optional[Decimal] = Field(
        title="Array3Annualtsrf", default=None
    )
    array4Azimuth: Optional[Decimal] = Field(
        title="Array4Azimuth", default=None
    )
    array4Tilt: Optional[Decimal] = Field(title="Array4Tilt", default=None)
    array4AnnualSolarAccess: Optional[Decimal] = Field(
        title="Array4Annualsolaraccess", default=None
    )
    array4AnnualTsrf: Optional[Decimal] = Field(
        title="Array4Annualtsrf", default=None
    )
    # Annual loss percentages
    annualAcBatteryLossPercent: Optional[Decimal] = Field(
        title="Annualacbatterylosspercent", default=None
    )
    annualAcInvClipLossPercent: Optional[Decimal] = Field(
        title="Annualacinvcliplosspercent", default=None
    )
    annualAcInvEffLossPercent: Optional[Decimal] = Field(
        title="Annualacinvefflosspercent", default=None
    )
    annualAcInvPntLossPercent: Optional[Decimal] = Field(
        title="Annualacinvpntlosspercent", default=None
    )
    annualAcInvPsoLossPercent: Optional[Decimal] = Field(
        title="Annualacinvpsolosspercent", default=None
    )
    annualAcLifetimeLossPercent: Optional[Decimal] = Field(
        title="Annualaclifetimelosspercent", default=None
    )
    annualAcPerfAdjLossPercent: Optional[Decimal] = Field(
        title="Annualacperfadjlosspercent", default=None
    )
    annualAcWiringLossPercent: Optional[Decimal] = Field(
        title="Annualacwiringlosspercent", default=None
    )
    annualDcBatteryLossPercent: Optional[Decimal] = Field(
        title="Annualdcbatterylosspercent", default=None
    )
    annualDcDiodesLossPercent: Optional[Decimal] = Field(
        title="Annualdcdiodeslosspercent", default=None
    )
    annualDcLifetimeLossPercent: Optional[Decimal] = Field(
        title="Annualdclifetimelosspercent", default=None
    )
    annualDcInvTdcLossPercent: Optional[Decimal] = Field(
        title="Annualdcinvtdclosspercent", default=None
    )
    annualDcMismatchLossPercent: Optional[Decimal] = Field(
        title="Annualdcmismatchlosspercent", default=None
    )
    annualDcModuleLossPercent: Optional[Decimal] = Field(
        title="Annualdcmodulelosspercent", default=None
    )
    annualDcMpptClipLossPercent: Optional[Decimal] = Field(
        title="Annualdcmpptcliplosspercent", default=None
    )
    annualDcNameplateLossPercent: Optional[Decimal] = Field(
        title="Annualdcnameplatelosspercent", default=None
    )
    annualDcOptimizerLossPercent: Optional[Decimal] = Field(
        title="Annualdcoptimizerlosspercent", default=None
    )
    annualDcPerfAdjLossPercent: Optional[Decimal] = Field(
        title="Annualdcperfadjlosspercent", default=None
    )
    annualDcSnowLossPercent: Optional[Decimal] = Field(
        title="Annualdcsnowlosspercent", default=None
    )
    annualDcTrackingLossPercent: Optional[Decimal] = Field(
        title="Annualdctrackinglosspercent", default=None
    )
    annualDcWiringLossPercent: Optional[Decimal] = Field(
        title="Annualdcwiringlosspercent", default=None
    )
    annualDistributionClippingLossPercent: Optional[Decimal] = Field(
        title="Annualdistributionclippinglosspercent", default=None
    )
    annualPoaCoverLossPercent: Optional[Decimal] = Field(
        title="Annualpoacoverlosspercent", default=None
    )
    annualPoaShadingLossPercent: Optional[Decimal] = Field(
        title="Annualpoashadinglosspercent", default=None
    )
    annualPoaSoilingLossPercent: Optional[Decimal] = Field(
        title="Annualpoasoilinglosspercent", default=None
    )
    annualSubhourlyClippingLossPercent: Optional[Decimal] = Field(
        title="Annualsubhourlyclippinglosspercent", default=None
    )
    annualTotalLossPercent: Optional[Decimal] = Field(
        title="Annualtotallosspercent", default=None
    )
    annualTransmissionLossPercent: Optional[Decimal] = Field(
        title="Annualtransmissionlosspercent", default=None
    )
    annualXfmrLossPercent: Optional[Decimal] = Field(
        title="Annualxfmrlosspercent", default=None
    )
    # Annual Metrics
    annualAcGross: Optional[Decimal] = Field(
        title="Annualacgross", default=None
    )
    annualDcGross: Optional[Decimal] = Field(
        title="Annualdcgross", default=None
    )
    annualPoaEff: Optional[Decimal] = Field(title="Annualpoaeff", default=None)
    # Battery details
    battPowerChargeMaxKwac: Optional[Decimal] = Field(
        title="Battpowerchargemaxkwac", default=None
    )
    battPowerDischargeMaxKwac: Optional[Decimal] = Field(
        title="Battpowerdischargemaxkwac", default=None
    )
    battComputedBankCapacity: Optional[Decimal] = Field(
        title="Battcomputedbankcapacity", default=None
    )

    class Config:
        extra = Extra.forbid


class DesignDetails(BaseModel):
    systemSize: Decimal = Field(
        title="Systemsize", description="capacity of the PV system"
    )
    numBatteries: int = Field(
        title="Numbatteries", description="number of batteries in the system"
    )
    batterySize: List[Union[Decimal, str, None]] = Field(
        title="Batterysize",
        description="size of each battery in the system",
        min_items=0,
        max_items=5,
        allow_none=True,
    )
    estimatedAvoidedCost: Decimal = Field(
        title="Estimatedavoidedcost",
        description=(
            "calculated as (utility bill before solar - utility bill after"
            " solar)"
        ),
    )


class EnergyProduction(BaseModel):
    annual: List[Decimal] = Field(min_items=1, max_items=35)


class EnergyProductionAnnual(EnergyProduction):
    pass


class EnergyProductionMonth(EnergyProduction):
    monthly: List[Decimal] = Field(min_items=12, max_items=420)


class EnergyProductionHourly(EnergyProduction):
    monthly: List[Decimal] = Field(...)
    hourly: List[Decimal] = Field(min_items=8760, max_items=8760)


class SimulationAPIResponse(BaseModel):
    designSource: str = Field(title="Designsource")
    simulationSource: str = Field(title="Simulationsource")
    simulationJobId: str = Field(title="Simulationjobid")
    simulationRunDuration: Decimal = Field(title="Simulationrunduration")
    designDetails: Optional[DesignDetails]
    energyProduction: EnergyProduction


class SimulationAPIResponseDetailed(SimulationAPIResponse):
    aggregated_component_params: Optional[dict] = Field(
        title="aggregated_component_params"
    )


class SimulationComponentsResponse(BaseModel):
    modules: Optional[Dict[str, Any]] = None
    inverters: Optional[Dict[str, Any]] = None
    batteries: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class JobStatusResponse(BaseModel):
    designSource: str
    simulationSource: str
    simulationJobId: str
    jobStatus: str
    jobResult: Optional[Dict] = None
    failureReason: Optional[str] = None

    class Config:
        extra = Extra.forbid
