import uuid
from fastapi.exceptions import HTTPException
from pydantic import UUID4


class Validator:
    @classmethod
    def UUID_Generator(cls):
        unique_id = uuid.uuid4()
        unique_id_str = str(unique_id).replace("-", "")[:9]
        return unique_id_str

    @classmethod
    def input_validator(cls, inputParams):
        cls.validate_missing_parameters(inputParams)
        cls.check_design_vendor_name(inputParams["designVendorName"])
        cls.check_uuid(inputParams["designID"], "designID")
        cls.check_uuid(inputParams["tenantID"], "tenantID")
        cls.check_simulation_mode(inputParams["simulationMode"])
        cls.check_simulation_years(
            inputParams["simulationYears"], inputParams["outputResolution"]
        )
        cls.check_output_resolution(inputParams["outputResolution"])

    @staticmethod
    def validate_missing_parameters(input_params):
        expected_params = {
            "designVendorName",
            "designID",
            "tenantID",
            "simulationMode",
            "simulationYears",
            "outputResolution",
        }

        missing_params = expected_params - set(input_params.keys())
        if missing_params:
            raise HTTPException(
                status_code=422,
                detail=f"Missing parameters: {', '.join(missing_params)}",
            )

    @staticmethod
    def check_design_vendor_name(designVendorName):
        if not isinstance(designVendorName, str):
            raise HTTPException(
                status_code=422, detail=f"designVendorName should be a string"
            )

        if designVendorName.upper() != "AURORA":
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid design vendor name: {designVendorName}. Must be"
                    " 'AURORA'."
                ),
            )

    @staticmethod
    def check_uuid(uuid_str, param):
        if not isinstance(uuid_str, str):
            raise HTTPException(
                status_code=422, detail=f"{param} should be a UUID string"
            )
        try:
            uuid_obj = uuid.UUID(hex=uuid_str)
        except ValueError:
            raise HTTPException(
                status_code=422, detail=f"Invalid UUID format for {param}"
            )

    @staticmethod
    def check_simulation_mode(mode):
        if not isinstance(mode, str):
            raise HTTPException(
                status_code=422, detail=f"simulationMode should be a string"
            )
        if mode.upper() not in ["MODE_PV"]:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid simulationMode: {mode}. Must be 'Mode_PV'.",
            )

    @staticmethod
    def check_simulation_years(years, outputResolution):
        if not isinstance(years, int):
            raise HTTPException(
                status_code=422, detail=f"years should be an integer"
            )
        if years > 1 and outputResolution == "hour":
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Hourly energy option is not supported for"
                    f" simulationYears>1"
                ),
            )
        elif (years > 1 and years not in [5, 10, 20, 25, 30, 35]) or years < 1:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"simulationYears {years} not supported. Supported"
                    " simulationYears are [1, 5, 10, 20, 25, 30, 35]"
                ),
            )

    @staticmethod
    def check_output_resolution(resolution):
        if not isinstance(resolution, str):
            raise HTTPException(
                status_code=422, detail=f"outputResolution should be a string"
            )
        if resolution.lower() not in ["month", "year", "hour"]:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid outputResolution: {resolution}, Must be one of"
                    " 'month', 'year' or 'hour'."
                ),
            )
