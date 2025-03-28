from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.pathfinding_schema import path_finding_request
from app.services.pathfinding_service import calculate_fastest_path
from app.routes.rooms.room_routes import router as room_router

router = APIRouter()

router.include_router(room_router, prefix="/rooms", tags=["rooms"])

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
