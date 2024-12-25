from typing import Any, Callable

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_healthz import HealthCheckRegistry

from app.api.utils.client_credentials import oauth2_scheme

_healthChecks = HealthCheckRegistry()

health_router = APIRouter()


# customizes health_check_route of fastapi_healthz
def custom_health_check_route(registry: HealthCheckRegistry) -> Callable:
    def encode_json(value: Any) -> Any:
        return jsonable_encoder({} if value is None else value)

    def endpoint(Authorization: str = Depends(oauth2_scheme)) -> JSONResponse:
        res = registry.check()
        if res["status"] == "HealthCheckStatusEnum.HEALTHY":
            res["status"] = "UP"
        elif res["status"] == "HealthCheckStatusEnum.UNHEALTHY":
            res["status"] = "DOWN"
        status_code = 200 if res["status"] == "UP" else 500

        return JSONResponse(content=encode_json(res), status_code=status_code)

    return endpoint


healthz = custom_health_check_route(registry=_healthChecks)

health_router.add_api_route("/simulation/resi/v1/healthz", endpoint=healthz)
