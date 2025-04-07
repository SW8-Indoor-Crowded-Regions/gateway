from pydantic import BaseModel
from typing import List
from app.schemas.sensor_response_schema import SensorNoRoomsModel

class FrontendPathFindingRequest(BaseModel):
    source: str
    target: str

class FastestPathModel(BaseModel):
    fastest_path: List[SensorNoRoomsModel]
    distance: float
