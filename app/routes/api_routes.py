from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.pathfinding_schema import PathfindingRequest
from app.services.pathfinding_service import calculate_fastest_path
from app.services.smk_api import search_artwork, get_artwork

router = APIRouter()

@router.get("/test")
async def get_route_test():
    return {"message": "API is working!"}

@router.post("/test")
async def post_route_test(request: BaseModel):
    return {"message": "Received test data."}

@router.post("/fastest-path")
async def get_fastest_path(request: PathfindingRequest):
    return await calculate_fastest_path(request)

@router.get("/search-artwork")
async def smk_search_artwork(keys: str):
    return await search_artwork(keys)

@router.get("/get-artwork")
async def smk_get_artwork(keys: str):
    return await get_artwork(keys)