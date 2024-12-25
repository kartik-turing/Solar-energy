import json
from typing import Optional
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from app.api.models import PVSimInput
from app.api.utils.logger import logger


class Table(Model):
    class Meta:
        table_name = ""
        region = "us-west-2"
        write_capacity_units = 50
        read_capacity_units = 50

    @classmethod
    def get_all_items(cls) -> list:
        items = []
        for item in cls.scan():
            items.append(
                {"id": item.simulationJobId, "attribute_values": item.Value}
            )
        return items

    @classmethod
    def get_item_by_id(cls, id) -> dict:
        try:
            item = cls.get(id)
            logger.info(item)
            return item.attribute_values if item is not None else {}
        except cls.DoesNotExist:
            return {}

    @classmethod
    def create_new_table(cls):
        if not cls.exists():
            cls.create_table(wait=True)
            logger.info(f"Table '{cls.Meta.table_name}' created successfully!")
        else:
            logger.info(f"Table '{cls.Meta.table_name}' already exists.")

    @classmethod
    def drop_table(cls):
        if cls.exists():
            cls.delete_table()
            logger.info(f"Table '{cls.Meta.table_name}' deleted successfully!")
        else:
            logger.info(f"Table '{cls.Meta.table_name}' does not exist.")


class JobDetailsTable(Table):
    class Meta:
        table_name = "job-details"
        region = "us-west-2"
        write_capacity_units = 50
        read_capacity_units = 50

    simulationJobId = UnicodeAttribute(hash_key=True)
    Value = UnicodeAttribute(null=False)

    @classmethod
    def write_data(
        cls,
        job_response: dict,
        api_input: PVSimInput,
        simulation_params: Optional[dict] = None,
    ):
        # create json in required format
        if simulation_params is None:
            job_value = {
                "designVendorName": api_input.designVendorName,
                "designID": api_input.designID,
                "tenantID": api_input.tenantID,
                "simulationMode": api_input.simulationMode,
                "simulationYears": api_input.simulationYears,
                "outputResolution": api_input.outputResolution,
            }
        else:
            job_value = {
                "designVendorName": api_input.designVendorName,
                "designID": api_input.designID,
                "tenantID": api_input.tenantID,
                "simulationMode": api_input.simulationMode,
                "simulationYears": api_input.simulationYears,
                "outputResolution": api_input.outputResolution,
                "startTime": (
                    simulation_params["start_time"]
                    if "start_time" in simulation_params
                    else ""
                ),
                "endTime": (
                    simulation_params["end_time"]
                    if "end_time" in simulation_params
                    else ""
                ),
                "estimatedSimulationTime": (
                    simulation_params["estimatedSimulationTime"]
                    if "estimatedSimulationTime" in simulation_params
                    else ""
                ),
                "actualSimulationTime": (
                    simulation_params["estimatedSimulationTime"]
                    if "estimatedSimulationTime" in simulation_params
                    else ""
                ),
            }
        if "Success" in job_response["description"]:
            job_value.update({"jobStatus": "COMPLETE"})

        else:
            job_value.update({"jobStatus": "FAILED"})
        if "simulationJobId" in job_response["content"]:
            simulation_job_id = job_response["content"]["simulationJobId"]
            # create ORM class attributes
            try:
                instance = cls(
                    simulationJobId=simulation_job_id,
                    Value=json.dumps(job_response),
                )
                instance.save()
                logger.info(
                    f"Item with JobId {simulation_job_id} added successfully"
                )
            except Exception as exception:
                logger.error(
                    "Item with this JobId"
                    f" {simulation_job_id} not added. {str(exception)}"
                )
        else:
            logger.warning(
                "No simulationJobId defined: Failed to write to database"
            )
