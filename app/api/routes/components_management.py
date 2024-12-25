import json
import logging
import re
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.utils.client_credentials import oauth2_scheme
from app.api.utils.logger import logger
from app.models.models import Battery, Inverter, Module
from app.models.schemas import BatteryTable, InverterTable, ModuleTable

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def parse_result(result) -> dict:
    result = {
        k: (
            (int(v) if isinstance(v, Decimal) and v % 1 == 0 else float(v))
            if isinstance(v, Decimal)
            else v
        )
        for k, v in result.items()
        if not k.startswith("_sa_")
    }
    return result


# parses tables data to json
def parse_result_battery(result) -> dict:
    result.pop("_sa_instance_state", None)
    result = re.sub(
        r"Decimal\('([^']+)'\)",
        lambda m: str(float(m.group(1))),
        str(result),
    )
    result = json.loads(result.replace("'", '"'))
    for key, val in result.items():
        if (
            isinstance(val, list)
            and len(val) == 1
            and not isinstance(val[0], list)
        ):
            if "temperature" not in key:
                result[key] = val[0]
    remove_decimal(result)
    return result


# recursively removes unnecessary 0 after decimal
def remove_decimal(json_result) -> dict:
    if isinstance(json_result, dict):
        for key, value in json_result.items():
            json_result[key] = remove_decimal(value)
    elif isinstance(json_result, list):
        for i in range(len(json_result)):
            json_result[i] = remove_decimal(json_result[i])
    elif isinstance(json_result, tuple):
        return tuple(remove_decimal(item) for item in json_result)
    elif isinstance(json_result, float) and json_result == int(json_result):
        json_result = int(json_result)
    return json_result


@router.get(
    "/simulation/resi/v1/modules",
    description="Get all module components.",
    operation_id="get_modules_simulation_resi_v1_modules_get",
    response_model=dict,
)
def get_modules(Authorization: str = Depends(oauth2_scheme)) -> dict:
    try:
        result = Module.get_all()
        data_collection = []
        if result:
            for inst_mod in result:
                data = {
                    key: getattr(inst_mod, key)
                    for key in list(ModuleTable.__fields__.keys())
                    if not key.startswith("_")
                }
                data_collection.append(jsonable_encoder(ModuleTable(**data)))
            response = {
                "description": "Successful Response",
                "content": {
                    "items": {"ModuleComponentResponse": data_collection}
                },
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error("Modules Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {"404": {"detail": f"Modules Not found"}}
                },
            )
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put(
    "/simulation/resi/v1/modules",
    description="Add a module component.",
    operation_id="add_module_simulation_resi_v1_modules_put",
)
def add_module(
    module_data: ModuleTable, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        Module.addModule(module_data)
        response = {
            "description": "Successful Response",
            "content": {
                "ModuleComponentResponse": jsonable_encoder(module_data)
            },
        }
        logger.info(response)
        return JSONResponse(status_code=200, content=response)
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/simulation/resi/v1/modules/{module_id}",
    description="Get a module component.",
    operation_id="get_module_simulation_resi_v1_modules__module_id__get",
    response_model=dict,
)
def get_module(
    module_id: str, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        module_data = Module.get_component(module_id)
        if module_data:
            data = {
                key: getattr(module_data, key)
                for key in list(ModuleTable.__fields__.keys())
                if not key.startswith("_")
            }
            response = {
                "description": "Successful Response",
                "content": {
                    "ModuleComponentResponse": jsonable_encoder(
                        parse_result(data)
                    )
                },
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Module {module_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Module {module_id} Not found"}
                    }
                },
            )

    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch(
    "/simulation/resi/v1/modules/{module_id}",
    description="Modify a module component (partial updates).",
    operation_id="modify_module_simulation_resi_v1_modules__module_id__patch",
)
def modify_module(
    module_id: str, params: dict, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        if "id" in params:
            raise Exception
        module_data = {
            k: v
            for k, v in params.items()
            if v is not None and k != "self" and k != "id"
        }
        # Retrieve Data
        module_table = Module.get_component(module_id)
        if module_table:
            current_data = module_table.__dict__
            updated_data = current_data
            updated_data.update(module_data)
            updated_data.pop("_sa_instance_state", None)
            module_table = ModuleTable(**updated_data)
            Module.update(module_table, module_id)  # Apply updates

            data = {
                key: getattr(module_table, key)
                for key in list(ModuleTable.__fields__.keys())
                if not key.startswith("_")
            }
            response = {
                "description": "Successful Response",
                "content": {"ModuleComponentResponse": jsonable_encoder(data)},
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Module {module_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Module {module_id} Not found"}
                    }
                },
            )
    except ValueError as exception:
        message = str(exception)
        error_type = type(exception).__name__
        if "annual_degradation" in message:
            message = message[message.find("Value") :].split("[")[0].strip()
            error_type = "value_error"

        error_detail = {"msg": [message], "type": error_type}
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

    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete(
    "/simulation/resi/v1/modules/{module_id}",
    description="Delete a module component.",
    operation_id="delete_module_simulation_resi_v1_modules__module_id__delete",
)
def delete_module(module_id: str, Authorization: str = Depends(oauth2_scheme)):
    try:
        delete_state = Module.delete(module_id)
        if delete_state == "Delete Successful":
            response = {
                "description": "Successful Response",
                "content": {
                    "description": f"Module {module_id} deleted successfully"
                },
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Module {module_id} Not found"}
                    }
                },
            )
    except Exception as exception:
        logging.error(f"An error occurred: {str(exception)}: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/simulation/resi/v1/inverters",
    description="Get all inverter components.",
    operation_id="get_inverters_simulation_resi_v1_inverters_get",
    response_model=dict,
)
def get_inverters(Authorization: str = Depends(oauth2_scheme)) -> dict:
    try:
        result = Inverter.get_all()
        data_collection = []
        if result:
            for inst_mod in result:
                data = {
                    key: getattr(inst_mod, key)
                    for key in list(InverterTable.__fields__.keys())
                    if not key.startswith("_")
                }
                data_collection.append(jsonable_encoder(InverterTable(**data)))
            response = {
                "description": "Successful Response",
                "content": {
                    "items": {"InverterComponentResponse": data_collection}
                },
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error("Inverters Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {"404": {"detail": f"Inverters Not found"}}
                },
            )
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put(
    "/simulation/resi/v1/inverters",
    description="Add an inverter component.",
    operation_id="add_inverter_simulation_resi_v1_inverters_put",
)
def add_inverter(
    inverter_data: InverterTable, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        Inverter.addInverter(inverter_data)
        response = {
            "description": "Successful Response",
            "content": {
                "InverterComponentResponse": jsonable_encoder(inverter_data)
            },
        }
        logger.info(response)
        return JSONResponse(status_code=200, content=response)
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/simulation/resi/v1/inverters/{inverter_id}",
    description="Get an inverter component.",
    operation_id="get_inverter_simulation_resi_v1_inverters__inverter_id__get",
    response_model=dict,
)
def get_inverter(
    inverter_id: str, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        inverter_data = Inverter.get_component(inverter_id)
        if inverter_data:
            data = {
                key: getattr(inverter_data, key)
                for key in list(InverterTable.__fields__.keys())
                if not key.startswith("_")
            }
            response = {
                "description": "Successful Response",
                "content": {
                    "InverterComponentResponse": jsonable_encoder(
                        parse_result(data)
                    )
                },
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Inverter {inverter_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Inverter {inverter_id} Not found"}
                    }
                },
            )
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch(
    "/simulation/resi/v1/inverters/{inverter_id}",
    description="Modify an inverter component (partial updates).",
    operation_id=(
        "modify_inverter_simulation_resi_v1_inverters__inverter_id__patch"
    ),
)
def modify_inverter(
    inverter_id: str, params: dict, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        if "id" in params:
            raise Exception
        inverter_data = {
            k: v
            for k, v in params.items()
            if v is not None and k != "self" and k != "id"
        }
        # Partially Update Data
        Inverter.update(inverter_data, inverter_id)
        # Retrieve Updated Data
        inverter_data = Inverter.get_component(inverter_id)
        if inverter_data:
            data = {
                key: getattr(inverter_data, key)
                for key in list(InverterTable.__fields__.keys())
                if not key.startswith("_")
            }
            response = {
                "description": "Successful Response",
                "content": {"InverterComponentResponse": data},
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Inverter {inverter_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Inverter {inverter_id} Not found"}
                    }
                },
            )
    except ValueError as exception:
        error_detail = {
            "msg": str(exception),
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
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete(
    "/simulation/resi/v1/inverters/{inverter_id}",
    description="Delete an inverter component.",
    operation_id=(
        "delete_inverter_simulation_resi_v1_inverters__inverter_id__delete"
    ),
)
def delete_inverter(
    inverter_id: str, Authorization: str = Depends(oauth2_scheme)
):
    try:
        delete_state = Inverter.delete(inverter_id)
        if delete_state == "Delete Successful":
            response = {
                "description": "Successful Response",
                "content": {
                    "description": (
                        f"Inverter {inverter_id} deleted successfully"
                    )
                },
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Inverter {inverter_id} Not found"}
                    }
                },
            )
    except Exception as exception:
        logging.error(f"An error occurred: {str(exception)}: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/simulation/resi/v1/batteries",
    description="Get all battery components.",
    operation_id="get_batteries_simulation_resi_v1_batteries_get",
    response_model=dict,
)
def get_batteries(Authorization: str = Depends(oauth2_scheme)) -> dict:
    try:
        result = Battery.get_all()
        data_collection = []
        if result:
            for inst_mod in result:
                data = {
                    key: getattr(inst_mod, key)
                    for key in list(BatteryTable.__fields__.keys())
                    if not key.startswith("_")
                }
                data_collection.append(jsonable_encoder(BatteryTable(**data)))
            response = {
                "description": "Successful Response",
                "content": {
                    "items": {"BatteryComponentResponse": data_collection}
                },
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error("Batteries Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {"404": {"detail": f"Batteries Not found"}}
                },
            )
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put(
    "/simulation/resi/v1/batteries",
    description="Add a battery component.",
    operation_id="add_battery_simulation_resi_v1_batteries_put",
)
def add_battery(
    battery_data: BatteryTable, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        Battery.addBattery(battery_data)
        response = {
            "description": "Successful Response",
            "content": {
                "BatteryComponentResponse": jsonable_encoder(battery_data)
            },
        }
        logger.info(response)
        return JSONResponse(status_code=200, content=response)
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/simulation/resi/v1/batteries/{battery_id}",
    description="Get a battery component.",
    operation_id="get_battery_simulation_resi_v1_batteries__battery_id__get",
    response_model=dict,
)
def get_battery(
    battery_id: str, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        battery_data = Battery.get_component(battery_id)
        if battery_data:
            data = parse_result_battery({
                key: getattr(battery_data, key)
                for key in list(BatteryTable.__fields__.keys())
                if not key.startswith("_")
            })

            response = {
                "description": "Successful Response",
                "content": {"BatteryComponentResponse": data},
            }
            logger.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Battery {battery_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Battery {battery_id} Not found"}
                    }
                },
            )
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch(
    "/simulation/resi/v1/batteries/{battery_id}",
    description="Modify a battery component (partial updates).",
    operation_id=(
        "modify_battery_simulation_resi_v1_batteries__battery_id__patch"
    ),
)
def modify_battery(
    battery_id: str, params: dict, Authorization: str = Depends(oauth2_scheme)
) -> dict:
    try:
        if "id" in params:
            raise Exception
        battery_data = {
            k: v
            for k, v in params.items()
            if v is not None and k != "self" and k != "id"
        }
        # Partially Update Data
        Battery.update(battery_data, battery_id)
        # Retrieve Updated Data
        battery_data = Battery.get_component(battery_id)
        if battery_data:
            data = parse_result_battery({
                key: getattr(battery_data, key)
                for key in list(BatteryTable.__fields__.keys())
                if not key.startswith("_")
            })
            response = {
                "description": "Successful Response",
                "content": {"BatteryComponentResponse": data},
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            logger.error(f"Battery {battery_id} Not found")
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Battery {battery_id} Not found"}
                    }
                },
            )
    except ValueError as exception:
        error_detail = {
            "msg": str(exception),
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
    except Exception as exception:
        logging.error(f"An error occured: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete(
    "/simulation/resi/v1/batteries/{battery_id}",
    description="Delete a battery component.",
    operation_id=(
        "delete_battery_simulation_resi_v1_batteries__battery_id__delete"
    ),
)
def delete_battery(
    battery_id: str, Authorization: str = Depends(oauth2_scheme)
):
    try:
        delete_state = Battery.delete(battery_id)
        if delete_state == "Delete Successful":
            response = {
                "description": "Successful Response",
                "content": {
                    "description": f"Battery {battery_id} deleted successfully"
                },
            }
            logging.info(response)
            return JSONResponse(status_code=200, content=response)
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "responses": {
                        "404": {"detail": f"Battery {battery_id} Not found"}
                    }
                },
            )
    except Exception as exception:
        logging.error(f"An error occurred: {str(exception)}: {str(exception)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
