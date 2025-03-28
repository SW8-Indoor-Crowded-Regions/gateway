from fastapi import APIRouter
from app.schemas.pathfinding_schema import path_finding_request
from app.services.pathfinding_service import calculate_fastest_path
from app.routes.room_routes import router as room_router
from app.routes.sensor_routes import router as sensor_router
from app.routes.tests.test_routes import router as test_router
from app.services.smk_api import search_artwork, get_artwork

router = APIRouter()

router.include_router(room_router, prefix="/rooms", tags=["rooms"])
router.include_router(sensor_router, prefix="/sensors", tags=["sensors"])
router.include_router(test_router, prefix="/test", tags=["test"])

@router.post("/fastest-path")
async def get_fastest_path(request: path_finding_request):
    return await calculate_fastest_path(request)

@router.get(
    path="/search-artwork", 
    tags=['SMK API'],
    description='Get a list of suggested artworks based on query.',
    response_model=list[str],
    response_description='Artwork names corresponding most to query.',
    summary='Get a list of artwork names corresponding most to given query.',
)
async def smk_search_artwork(keys: str):
    return await search_artwork(keys)

@router.get(
    path="/get-artwork",
    tags=['SMK API'],
    description='Get information about a specified artwork from SMK API.',
    response_model=list[dict],
    response_description='Returns information about the artwork.',
    summary='Get artwork information.',
)
async def smk_get_artwork(keys: str):
    return await get_artwork(keys)