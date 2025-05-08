from fastapi import HTTPException
from app.utils.forwarder import forward_request
from app.schemas.room_response_schema import RoomListModel
from app.schemas.sensor_response_schema import SensorListModel
import os
from dotenv import load_dotenv
from typing import Type, TypeVar

T = TypeVar('T', RoomListModel, SensorListModel)

load_dotenv()
SENSOR_SIM_PATH = os.getenv('SENSOR_SIM', 'http://localhost:8002')
if SENSOR_SIM_PATH is None:
	raise RuntimeError('SENSOR_SIM not found in environment variables')

async def fetch_and_validate(type: Type[T], path: str) -> T:
	try:
		room_data, _ = await forward_request(f'{SENSOR_SIM_PATH}/{path}', 'GET')
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f'Failed to retrieve {path.removesuffix("s")} data from sensor simulation service'
		) from e

	try:
		type.model_validate(room_data)
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f'Invalid or empty {path.removesuffix("s")} data received from sensor simulation service',
		) from e

	return room_data