from fastapi import APIRouter
from app.schemas.sensor_response_schemas import SensorModel, SensorListModel
from app.services.sensor_controllers import get_all_sensors, get_sensor_by_id
from app.utils.responses.sensors import get_sensors_responses, get_sensor_by_id_responses

router = APIRouter()


@router.get(
	'/',
	summary='Get all sensors',
	description='Fetch all sensors from the database.',
	response_description='List of all sensors.',
	response_model=SensorListModel,
	responses=get_sensors_responses
)
async def get_all_sensors_route():
	"""
	Fetch all sensors from the database.
	"""
	return await get_all_sensors()

@router.get(
	'/{sensor_id}',
	summary='Get sensor by ID',
	description='Fetch a specific sensor by its ID.',
	response_description='Details of the sensor.',
	response_model= SensorModel,
	responses=get_sensor_by_id_responses
)
async def get_sensor_by_id_route(sensor_id: str):
	"""
	Fetch a specific sensor by its ID.
	"""
	return await get_sensor_by_id(sensor_id)
