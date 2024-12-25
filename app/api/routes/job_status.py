import json
import re
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.api.models import JobStatusResponse
from app.api.utils.client_credentials import oauth2_scheme
from app.api.utils.logger import logger
from app.models.dynamodb_orms import JobDetailsTable


def response_data(
    output_collection: Dict[str, Any], job_data: Dict
) -> Dict[str, any]:
    output_collection["jobStatus"] = (
        "SUCCESS"
        if job_data["description"] == "Successful Response"
        else "FAILED"
    )
    if output_collection["jobStatus"] == "SUCCESS":
        output_collection.update({"jobResult": job_data})
    else:
        output_collection.update({"failureReason":job_data["content"]["detail"]})
    output_collection["simulationSource"] = "Qcells"
    output_collection["designSource"] = "Aurora"



router = APIRouter()


@router.get(
    "/simulation/resi/v1/jobstatus",
    description=(
        "Check the progress and completion status of the specified simulation"
        " job. If the job is complete, simulation results are also returned"
        " along with the status."
    ),
    operation_id="get_simulation_status_simulation_resi_v1_jobstatus_get",
    response_model=JobStatusResponse,
    response_model_exclude_none=True,
)
def get_simulation_status(
    simulationJobID, token: str = Depends(oauth2_scheme)
) -> JobStatusResponse:
    try:
        if not re.fullmatch(r"[a-zA-Z0-9]{9}", simulationJobID):
            raise ValueError(
                "simulationJobID must be a 9-character alphanumeric string."
            )

        job_data = json.loads(
            JobDetailsTable.get_item_by_id(simulationJobID).get("Value", "{}")
        )

        if not job_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        output_collection = {"simulationJobId": simulationJobID}
       
        response_data(output_collection, job_data)
        logger.info(output_collection)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                JobStatusResponse(**output_collection), exclude_none=True
            ),
        )

    except ValueError as value_error:
        response = JSONResponse(
            status_code=422,
            content={
                "description": "Validation Error",
                "content": {
                    "detail": {
                        "items": [{
                            "loc": ["body"],
                            "msg": str(value_error),
                            "type": "ValueError",
                            "title": "Detail",
                        }]
                    }
                },
            },
        )
        logger.error(response.body)
        return response

    except HTTPException as exception:
        response = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "description": "Not Found Error",
                "content": {"detail": f"Job Id {simulationJobID} Not found"},
            },
        )
        logger.error(response.body)
        return response

    except Exception as exception:
        logger.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
