from fastapi import HTTPException
from app.utils.forwarder import forward_request
from app.schemas.pathfinding_schema import FrontendPathFindingRequest, FastestPathModel, FrontendMultiPathRequest
from app.schemas.room_response_schema import RoomListModel
from app.schemas.sensor_response_schema import SensorListModel
from app.utils.room_sensor_fetch import fetch_and_validate
import os
from dotenv import load_dotenv
import requests

load_dotenv()

PATHFINDING_PATH = os.getenv('PATHFINDING', 'http://localhost:8001')
if PATHFINDING_PATH is None:
	raise RuntimeError('PATHFINDING not found in environment variables')  # pragma: no cover

async def calculate_fastest_path(request: FrontendPathFindingRequest) -> FastestPathModel:
	room_data = await fetch_and_validate(RoomListModel, 'rooms')
	sensor_data = await fetch_and_validate(SensorListModel, 'sensors')

	# Prepare payload for the pathfinding service.
	payload = {
		'source_room': request.source,
		'target_room': request.target,
		'rooms': room_data.rooms,
		'sensors': sensor_data.sensors,
	}

	# Send POST request to the pathfinding service.
	pathfinding_url = f'{PATHFINDING_PATH}/pathfinding/fastest-path'

	path_response, _ = await forward_request(pathfinding_url, 'POST', body=payload)

	return path_response

async def calculate_fastest_multipoint_path(request: FrontendMultiPathRequest) -> FastestPathModel:
	room_data = await fetch_and_validate(RoomListModel, 'rooms')
	sensor_data = await fetch_and_validate(SensorListModel, 'sensors')
 
	targets = [room['id'] for room in room_data['rooms'] if room['name'] in request.targets] # type: ignore
	if not targets:
		raise HTTPException(
			status_code=400,
			detail='No valid target rooms found in the request.',
		)
  
	payload = {
		'source_room': request.source,
		'target_rooms': targets,
		'rooms': room_data['rooms'], # type: ignore
		'sensors': sensor_data['sensors'], # type: ignore
	}
 
	res =requests.post(
		f'{PATHFINDING_PATH}/pathfinding/multiple-points',
		json=payload,
	)
	
	if res.status_code != 200:
		raise HTTPException(
			status_code=res.status_code,
			detail={
				'error': res.json(),
				'body': payload if len(payload.__str__()) < 1000 else 'Body too large to display',
				'method': 'POST',
				'url': f'{PATHFINDING_PATH}/pathfinding/fastest-multipoint-path',
			},
		)
  
	return res.json()