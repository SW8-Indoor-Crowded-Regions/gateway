from pydantic import BaseModel
from typing import List


class SensorModel(BaseModel):
	id: str
	rooms: List[str]
	latitude: float
	longitude: float
	is_vertical: bool


class SensorListModel(BaseModel):
	sensors: List[SensorModel]


class SensorNoRoomsModel(BaseModel):
	id: str
	latitude: float
	longitude: float

