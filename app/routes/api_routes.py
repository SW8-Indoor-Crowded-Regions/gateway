from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.pathfinding_schema import path_finding_request
from app.services.pathfinding_service import calculate_fastest_path
from app.routes.rooms.room_routes import router as room_router
from app.routes.sensors.sensor_routes import router as sensor_router
from app.routes.tests.test_routes import router as test_router

router = APIRouter()

router.include_router(room_router, prefix="/rooms", tags=["rooms"])
router.include_router(sensor_router, prefix="/sensors", tags=["sensors"])
router.include_router(test_router, prefix="/test", tags=["test"])

@router.post("/fastest-path")
async def get_fastest_path(request: path_finding_request):
    return await calculate_fastest_path(request)
