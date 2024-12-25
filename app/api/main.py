import logging
import os
import re
import traceback
from collections import Counter

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param

from app.api.routes import (
    components_management,
    health,
    job_status,
    simulation_job_management,
)
from app.auth import authenticate_current_user as authorize

load_dotenv("app/config/.env")

api_router_simulation = APIRouter()
api_router_simulation.include_router(
    simulation_job_management.router,
    tags=["Simulation Job Management"],
)
api_router_simulation.include_router(
    job_status.router,
    tags=["Simulation Job Management"],
)
api_router_simulation.include_router(
    health.health_router,
    tags=["Common"],
)
api_router_components = APIRouter()
api_router_components.include_router(
    components_management.router, tags=["Components Management"]
)
app = FastAPI(docs_url="/swagger")
app.include_router(api_router_simulation)
app2 = FastAPI(docs_url="/swagger")

app2.include_router(api_router_components)


@app2.middleware("http")
@app.middleware("http")
async def token_based_authentication(request: Request, call_next):
    if os.getenv("YOUR_ENV") and os.getenv("YOUR_ENV") == "testing":
        return await call_next(request)

    elif request.url.path.startswith("/simulation"):
        response_auth_failure = {
            "responses": {
                "401": {
                    "description": "Authorization Error",
                    "content": {
                        "detail": "Token missing",
                    },
                }
            }
        }
        token = request.headers.get("Authorization")

        if not token:
            return JSONResponse(
                status_code=401,
                content=response_auth_failure,
            )
        scheme, access_token = get_authorization_scheme_param(token)
        if scheme.lower() != "bearer" or not access_token:
            response_auth_failure["responses"]["401"]["content"][
                "detail"
            ] = response_auth_failure["responses"]["401"]["content"][
                "detail"
            ].replace(
                "Token missing", "Token missing or Invalid Token"
            )
            return JSONResponse(
                content=response_auth_failure,
                status_code=401,
            )
        try:
            authorize(access_token)
        except (HTTPException, Exception) as exception:
            traceback_str = traceback.format_exc()
            logging.error(traceback_str)

            response_auth_failure["responses"]["401"]["content"][
                "detail"
            ] = response_auth_failure["responses"]["401"]["content"][
                "detail"
            ].replace(
                "Token missing", "Invalid Token"
            )
            return JSONResponse(
                content=response_auth_failure,
                status_code=401,
            )
    return await call_next(request)


@app2.exception_handler(RequestValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    validation_errors = []
    for error in exc.errors():
        loc = error["loc"]
        type_ = error["type"]
        error_msg = []
        if type_ == "value_error.missing":
            # Handle missing field error
            error_msg = f'Missing field: {error["loc"][-1]}'
        elif type_ == "value_error.jsondecode" or type_ == "type_error.dict":
            doc = error["ctx"]["doc"]
            missing_comma_pattern = re.compile(
                r'("[^"]+":\s*[^,}\n]+)(?=\s*(?:,|\n|\}))'
            )

            empty_value_pattern = re.compile(r'("[^"]+":\s*(?:,\s*|\n\s*|}))')
            missing_commas = missing_comma_pattern.findall(doc)
            for mc in missing_commas:
                counter = Counter(str(mc))
                if counter.get(":") > 1:
                    error_msg.append(f"Missing comma: {mc}")

            empty_values = empty_value_pattern.findall(doc)
            for ev in empty_values:
                error_msg.append(f"Empty value: {ev}")
        elif type_=='value_error':
            error_msg.append(error["msg"])
        validation_errors.append({
            "loc": loc,
            "msg": error_msg,
            "type": type_,
        })
    response_content = {
        "responses": {
            "422": {
                "description": "Validation Error",
                "content": {
                    "detail": {"items": validation_errors, "title": "Detail"}
                },
            }
        }
    }
    logging.error(response_content)
    return JSONResponse(status_code=422, content=response_content)
