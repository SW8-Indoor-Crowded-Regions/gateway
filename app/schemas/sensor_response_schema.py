from pydantic import BaseModel
from typing import List
from app.schemas.room_response_schema import RoomFromPathfindingModel

class SensorModel(BaseModel):
	id: str
	rooms: List[str]
	latitude: float
	longitude: float
 
class SensorWithRoomsModel(BaseModel):
	id: str
	rooms: List[RoomFromPathfindingModel]
	latitude: float
	longitude: float

class SensorListModel(BaseModel):
  sensors: List[SensorModel]