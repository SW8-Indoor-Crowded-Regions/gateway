from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.pathfinding_schema import path_finding_request
from app.services.pathfinding_service import calculate_fastest_path
from app.services.smk_api import search_artwork, get_artwork

router = APIRouter()

@router.get("/test",
            summary="Test if the API is working",
				description="A simple test route to check if the API is working.",
				tags=["test"],
				response_description="A simple message to confirm the API is working.",
				response_model=dict
    		)
async def get_route_test():
    return {"message": "API is working!"}

@router.post("/test")
async def post_route_test(request: BaseModel):
    return {"message": "Received test data."}

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