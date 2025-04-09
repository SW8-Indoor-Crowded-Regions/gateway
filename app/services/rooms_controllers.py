import os
from dotenv import load_dotenv
from app.utils.forwarder import forward_request
from app.schemas.room_response_schema import RoomModel, RoomListModel
from fastapi import HTTPException

load_dotenv()
SENSOR_SIM_PATH = os.getenv('SENSOR_SIM', 'http://localhost:8002')
if SENSOR_SIM_PATH is None:
	raise RuntimeError('SENSOR_SIM not found in environment variables')  # pragma: no cover

PATHFINDING_PATH = os.getenv('PATHFINDING', 'http://localhost:8001')
if PATHFINDING_PATH is None:
	raise RuntimeError('PATHFINDING not found in environment variables')  # pragma: no cover


async def get_all_rooms() -> RoomListModel:
	res, status = await forward_request(SENSOR_SIM_PATH + '/rooms', 'GET')
	try:
		RoomListModel.model_validate(res, strict=True)
		return res
	except Exception:
		raise HTTPException(
			status_code=status,
			detail=res.get('detail', 'Invalid room data received from sensor simulation service'),
		)


async def get_room_by_id(room_id: str) -> RoomModel:
	res, status = await forward_request(SENSOR_SIM_PATH + f'/rooms/{room_id}', 'GET')

	try:
		RoomModel.model_validate(res, strict=True)
		return res
	except Exception:
		raise HTTPException(
			status_code=status,
			detail=res.get('detail', 'Invalid room data received from sensor simulation service'),
		)
