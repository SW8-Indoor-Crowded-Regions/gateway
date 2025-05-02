from fastapi import APIRouter
from app.schemas.filter_schemas import FilterResponse
from app.utils.responses.filter import get_filters_responses
from app.services.filter_service import get_filters as fetch_filters

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
