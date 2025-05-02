from fastapi import APIRouter, Request
from app.schemas.filter_schemas import FilterResponse, FilterToRoomsRequest
from app.utils.responses.filter import get_filters_responses, filter_to_rooms_responses
from app.services.filter_service import get_filters as fetch_filters, filter_to_rooms

router = APIRouter()


@router.get(
	'/',
	summary='Get a list of available filters.',
	description='Get a list of available filters.',
	response_model=list[FilterResponse],
	response_description='List of available filters.',
	responses=get_filters_responses,
)
async def get_filters():
	"""
	Get a list of available filters.
	"""
	filters = fetch_filters()
	return filters

@router.post(
	'/rooms',
	summary='Get rooms associated with a list of filters.',
	description='Get the name of rooms associated with a list of filters.',
	response_model=list[str],
	response_description='List of room names that match the filter.',
	responses=filter_to_rooms_responses,
)
async def filters_to_rooms(request: FilterToRoomsRequest):
	"""
	Get rooms needed to visit all artworks based on filters.
	"""
	rooms = filter_to_rooms(request)
	return rooms