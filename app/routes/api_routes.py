from fastapi import APIRouter, Depends
from app.schemas.pathfinding_schema import FrontendPathFindingRequest
from app.services.pathfinding_service import calculate_fastest_path
from app.routes.room_routes import router as room_router
from app.routes.sensor_routes import router as sensor_router
from app.services.smk_api import search_artwork, query_artwork
from app.schemas.smk_api_schemas import FilterParams, ArtworkResponse, artwork_response_example

router = APIRouter()

router.include_router(room_router, prefix='/rooms', tags=['rooms'])
router.include_router(sensor_router, prefix='/sensors', tags=['sensors'])


@router.post('/fastest-path')
async def get_fastest_path(request: FrontendPathFindingRequest):
	return await calculate_fastest_path(request)


# Health check route
@router.get(
	'/health',
	tags=['Health Check'],
	description='Check the health of the API.',
	response_model=dict,
	response_description='Returns the status of the API.',
	summary='Health check of the API.',
	responses={
		200: {
			'description': 'API is healthy',
			'content': {'application/json': {'example': {'status': 'ok'}}},
		},
		500: {
			'description': 'Internal Server Error',
			'content': {'application/json': {'example': {'status': 'error'}}},
		},
	},
)
async def health_check():
	return {'status': 'ok'}


@router.get(
	path='/search-artwork',
	tags=['SMK API'],
	description='Get a list of suggested artworks based on query.',
	response_model=list[str],
	response_description='Artwork names corresponding most to query.',
	summary='Get a list of artwork names corresponding most to given query.',
)
async def smk_search_artwork(keys: str):
	return await search_artwork(keys)


# Route to get all artworks using a query
@router.get(
   path='/artwork',
   tags=['SMK API'],
	description='Get artwork based on a query. This endpoint allows you to search by keywords, and filter artworks by room id.',
	response_model=ArtworkResponse,
	response_model_exclude_none=True,
	response_description='Returns a list of artworks based on the query.',
	summary='Get artworks based on a query.',
	responses=artwork_response_example,
)
async def smk_get_artwork_by_query(query: FilterParams = Depends()):
	res = await query_artwork(query)
   
	return res
   