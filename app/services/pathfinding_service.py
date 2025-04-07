from fastapi import HTTPException
from app.utils.forwarder import forward_request
from app.schemas.pathfinding_schema import FrontendPathFindingRequest, FastestPathModel
from app.schemas.room_response_schema import RoomListModel
from app.schemas.sensor_response_schema import SensorListModel
import os
from dotenv import load_dotenv

load_dotenv()
SENSOR_SIM_PATH = os.getenv('SENSOR_SIM', 'http://localhost:8002')
if SENSOR_SIM_PATH is None:
	raise RuntimeError('SENSOR_SIM not found in environment variables')  # pragma: no cover

PATHFINDING_PATH = os.getenv('PATHFINDING', 'http://localhost:8001')
if PATHFINDING_PATH is None:
	raise RuntimeError('PATHFINDING not found in environment variables')  # pragma: no cover


async def calculate_fastest_path(request: FrontendPathFindingRequest) -> FastestPathModel:
	# Query sensor simulation service for room data.
	sensor_sim_rooms_url = f'{SENSOR_SIM_PATH}/rooms'
	sensor_sim_sensors_url = f'{SENSOR_SIM_PATH}/sensors'

	try:
		room_data, _ = await forward_request(sensor_sim_rooms_url, 'GET')
	except Exception as e:
		raise HTTPException(
			status_code=500, detail='Failed to retrieve room data from sensor simulation service'
		) from e

	try:
		RoomListModel.model_validate(room_data)
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail='Invalid or empty room data received from sensor simulation service',
		) from e

	try:
		sensor_data, _ = await forward_request(sensor_sim_sensors_url, 'GET')
	except Exception as e:
		raise HTTPException(
			status_code=500, detail='Failed to retrieve sensor data from sensor simulation service'
		) from e

	try:
		SensorListModel.model_validate(sensor_data)
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail='Invalid or empty sensor data received from sensor simulation service',
		) from e

	# Prepare payload for the pathfinding service.
	payload = {
		'source_sensor': request.source,
		'target_sensor': request.target,
		'rooms': room_data['rooms'],
		'sensors': sensor_data['sensors'],
	}

	# Send POST request to the pathfinding service.
	pathfinding_url = f'{PATHFINDING_PATH}/pathfinding/fastest-path'

	try:
		path_response, status = await forward_request(pathfinding_url, 'POST', body=payload)
	except Exception as e:  # pragma: no cover
		raise HTTPException(  # pragma: no cover
			status_code=500, detail='Error communicating with pathfinding service'
		) from e

	try:
		path_response = FastestPathModel.model_validate(path_response)
	except Exception as e:  # pragma: no cover)
		raise HTTPException(  # pragma: no cover
			status_code=status, detail=path_response.get('detail', 'Invalid pathfinding response')
		) from e

	return path_response
