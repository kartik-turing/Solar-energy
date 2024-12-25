import datetime
import os
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.models import PVSimInput
from app.api.utils.client_credentials import oauth2_scheme
from app.api.utils.input_validator import Validator
from app.api.utils.logger import logger
from app.api.utils.response import create_job_result_response
from geli.pysam_pvsim import PySAM_PVSim

router = APIRouter()


@router.post(
    "/simulation/resi/v1/simulationjob",
    description=(
        "Trigger a simulation job for the specified project design. This API"
        " call is synchronous; it blocks until the requested simulation"
        " completes."
    ),
    operation_id="run_simulation_simulation_resi_v1_simulationjob_post",
)
def run_simulation(
    input_params: PVSimInput, Authorization: str = Depends(oauth2_scheme)
) -> Dict:
    try:
        start_timestamp = datetime.datetime.now(datetime.timezone.utc)
        os.environ["access_token"] = Authorization
        simulationJobId = Validator.UUID_Generator()
        try:
            Validator.input_validator(input_params.dict())
            pvsim = PySAM_PVSim(
                input_params.designVendorName,
                input_params.designID,
                input_params.tenantID,
                input_params.simulationMode,
                input_params.simulationYears,
                input_params.outputResolution,
            )
            try:
                pvsim.execute()
                # Build response
                job_result_response = create_job_result_response(
                    input_params.designID,
                    input_params.tenantID,
                    simulationJobId=simulationJobId,
                    SimulationTime=jsonable_encoder(
                        datetime.datetime.now(datetime.timezone.utc)
                        - start_timestamp
                    ),
                    pvsim=pvsim,
                    outputResolution=input_params.outputResolution,
                    simulationYears=input_params.simulationYears,
                    start_timestamp=start_timestamp,
                )
                simulation_params = {"start_time": str(start_timestamp)}
                job_response = {
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": job_result_response,
                        }
                    }
                }
                #JobDetailsTable.write_data(
                #    job_response["responses"]["200"],
                #    input_params,
                #    simulation_params,
                #)
                logger.info(
                    f"Request Successful for design id {input_params.designID}"
                )
                end_timestamp = datetime.datetime.now(datetime.timezone.utc)
                simulation_time = jsonable_encoder(
                    end_timestamp - start_timestamp
                )
                job_response["responses"]["200"]["content"].update(
                    {"simulationRunDuration": simulation_time}
                )
                return JSONResponse(content=job_response, status_code=200)

            except (
                AttributeError,
                ValueError,
                TypeError,
                Exception,
            ) as exception:
                if isinstance(
                    exception, (AttributeError, ValueError, TypeError)
                ):
                    job_response = {
                        "responses": {
                            "400": {
                                "description": "Bad Request",
                                "content": {
                                    "simulationJobId": simulationJobId,
                                    "simulationRunDuration": jsonable_encoder(
                                        datetime.datetime.now(
                                            datetime.timezone.utc
                                        )
                                        - start_timestamp
                                    ),
                                    "tenantId": input_params.tenantID,
                                    "designId": input_params.designID,
                                    "detail": str(exception),
                                },
                            }
                        }
                    }
                    #JobDetailsTable.write_data(
                    #    job_response["responses"]["400"],
                    #    input_params,
                    #    simulation_params=None,
                    #)
                    logger.error(f"An error occured {str(exception)}")
                    end_timestamp = datetime.datetime.now(
                        datetime.timezone.utc
                    )
                    simulation_time = jsonable_encoder(
                        end_timestamp - start_timestamp
                    )
                    job_response["responses"]["400"]["content"].update(
                        {"simulationRunDuration": simulation_time}
                    )
                    return JSONResponse(content=job_response, status_code=400)
                else:
                    logger.error(f"An error occured: {str(exception)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        except (
            AssertionError,
            AttributeError,
            ValueError,
            HTTPException,
            Exception,
        ) as exception:
            if (
                isinstance(exception, HTTPException)
                and exception.status_code == 422
            ):
                error_detail = {
                    "msg": str(exception.detail),
                    "type": type(exception).__name__,
                }
                return JSONResponse(
                    status_code=422,
                    content={
                        "responses": {
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "detail": {
                                        "items": [{
                                            "loc": ["body"],
                                            "msg": error_detail["msg"],
                                            "type": error_detail["type"],
                                            "title": "Detail",
                                        }]
                                    }
                                },
                            }
                        }
                    },
                )
            elif isinstance(
                exception, (AssertionError, AttributeError, ValueError)
            ):
                job_response = {
                    "responses": {
                        "400": {
                            "description": "Bad Request",
                            "content": {
                                "simulationJobId": simulationJobId,
                                "simulationRunDuration": jsonable_encoder(
                                    datetime.datetime.now(
                                        datetime.timezone.utc
                                    )
                                    - start_timestamp
                                ),
                                "tenantId": input_params.tenantID,
                                "designId": input_params.designID,
                                "detail": str(exception),
                            },
                        }
                    }
                }
                logger.error(f"An error occured {str(exception)}")
                end_timestamp = datetime.datetime.now(datetime.timezone.utc)
                simulation_time = jsonable_encoder(
                    end_timestamp - start_timestamp
                )
                job_response["responses"]["400"]["content"].update(
                    {"simulationRunDuration": simulation_time}
                )
                return JSONResponse(content=job_response, status_code=400)
            else:
                logger.error(f"An error occured: {str(exception)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    except Exception as exception:
        logger.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/simulation/resi/v1/simulationjob/detailed",
    description=(
        "Trigger a simulation job for the specified project design. This API"
        " call is synchronous; it blocks until the requested simulation"
        " completes. The output is returned in a detailed format meant for"
        " internal engineering consumption."
    ),
    operation_id="run_simulation_detailed_simulation_resi_v1_simulationjob_detailed_post",
)
def run_simulation_detailed(
    input_params: PVSimInput,
    Authorization: str = Depends(oauth2_scheme),
) -> Dict:
    try:
        start_timestamp = datetime.datetime.now(datetime.timezone.utc)
        os.environ["access_token"] = Authorization
        simulationJobId = Validator.UUID_Generator()
        try:
            Validator.input_validator(input_params.dict())
            pvsim = PySAM_PVSim(
                input_params.designVendorName,
                input_params.designID,
                input_params.tenantID,
                input_params.simulationMode,
                input_params.simulationYears,
                input_params.outputResolution,
            )
            try:
                pvsim.execute()
                # Build response
                job_result_response = create_job_result_response(
                    input_params.designID,
                    input_params.tenantID,
                    simulationJobId=simulationJobId,
                    SimulationTime=jsonable_encoder(
                        datetime.datetime.now(datetime.timezone.utc)
                        - start_timestamp
                    ),
                    pvsim=pvsim,
                    outputResolution=input_params.outputResolution,
                    simulationYears=input_params.simulationYears,
                    start_timestamp=start_timestamp,
                    detailed=True,
                )
                simulation_params = {"start_time": str(start_timestamp)}
                job_response = {
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": job_result_response,
                        }
                    }
                }
                logger.info(
                    f"Request Successful for design id {input_params.designID}"
                )
                end_timestamp = datetime.datetime.now(datetime.timezone.utc)
                simulation_time = jsonable_encoder(
                    end_timestamp - start_timestamp
                )
                job_response["responses"]["200"]["content"].update(
                    {"simulationRunDuration": simulation_time}
                )
                return JSONResponse(content=job_response, status_code=200)

            except (
                AttributeError,
                ValueError,
                TypeError,
                Exception,
            ) as exception:
                if isinstance(
                    exception, (AttributeError, ValueError, TypeError)
                ):
                    job_response = {
                        "responses": {
                            "400": {
                                "description": "Bad Request",
                                "content": {
                                    "simulationJobId": simulationJobId,
                                    "simulationRunDuration": jsonable_encoder(
                                        datetime.datetime.now(
                                            datetime.timezone.utc
                                        )
                                        - start_timestamp
                                    ),
                                    "tenantId": input_params.tenantID,
                                    "designId": input_params.designID,
                                    "detail": str(exception),
                                },
                            }
                        }
                    }
                    logger.error(f"An error occured {str(exception)}")
                    end_timestamp = datetime.datetime.now(
                        datetime.timezone.utc
                    )
                    simulation_time = jsonable_encoder(
                        end_timestamp - start_timestamp
                    )
                    job_response["responses"]["400"]["content"].update(
                        {"simulationRunDuration": simulation_time}
                    )
                    return JSONResponse(content=job_response, status_code=400)
                else:
                    logger.error(f"An error occured: {str(exception)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        except (
            AssertionError,
            AttributeError,
            ValueError,
            HTTPException,
            Exception,
        ) as exception:
            if (
                isinstance(exception, HTTPException)
                and exception.status_code == 422
            ):
                error_detail = {
                    "msg": str(exception.detail),
                    "type": type(exception).__name__,
                }
                return JSONResponse(
                    status_code=422,
                    content={
                        "responses": {
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "detail": {
                                        "items": [{
                                            "loc": ["body"],
                                            "msg": error_detail["msg"],
                                            "type": error_detail["type"],
                                            "title": "Detail",
                                        }]
                                    }
                                },
                            }
                        }
                    },
                )
            elif isinstance(
                exception, (AssertionError, AttributeError, ValueError)
            ):
                job_response = {
                    "responses": {
                        "400": {
                            "description": "Bad Request",
                            "content": {
                                "simulationJobId": simulationJobId,
                                "simulationRunDuration": jsonable_encoder(
                                    datetime.datetime.now(
                                        datetime.timezone.utc
                                    )
                                    - start_timestamp
                                ),
                                "tenantId": input_params.tenantID,
                                "designId": input_params.designID,
                                "detail": str(exception),
                            },
                        }
                    }
                }
                logger.error(f"An error occured {str(exception)}")
                end_timestamp = datetime.datetime.now(datetime.timezone.utc)
                simulation_time = jsonable_encoder(
                    end_timestamp - start_timestamp
                )
                job_response["responses"]["400"]["content"].update(
                    {"simulationRunDuration": simulation_time}
                )
                return JSONResponse(content=job_response, status_code=400)
            else:
                logger.error(f"An error occured: {str(exception)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    except Exception as exception:
        logger.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
