from pydantic import BaseModel
from typing import List

class RoomModel(BaseModel):
	id: str
	name: str
	type: str
	crowd_factor: float
	occupants: int
	area: float
	longitude: float
	latitude: float

class RoomListModel(BaseModel):
	rooms: List[RoomModel]
