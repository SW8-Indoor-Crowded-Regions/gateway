from fastapi import APIRouter
from app.schemas.room_response_schema import RoomModel, RoomListModel
from app.services.rooms_controllers import get_all_rooms, get_room_by_id
from app.utils.responses.rooms import get_room_by_id_responses, get_rooms_responses

router = APIRouter()


@router.get(
	'/',
	summary='Get all rooms',
	description='Fetch all rooms from the database.',
	response_description='List of all rooms.',
	response_model=RoomListModel,
	responses=get_rooms_responses
)
async def get_all_rooms_route():
	"""
	Fetch all rooms from the database.
	"""
	return await get_all_rooms()


@router.get(
	'/{room_id}',
	summary='Get room by ID',
	description='Fetch a specific room by its ID.',
	response_description='Details of the room.',
	response_model= RoomModel,
	responses=get_room_by_id_responses
)
async def get_room_by_id_route(room_id: str):
	"""
	Fetch a specific room by its ID.
	"""
	return await get_room_by_id(room_id)
