from pydantic import BaseModel
from typing import List

class SensorModel(BaseModel):
	id: str
	rooms: List[str]
	latitude: float
	longitude: float
		  

class SensorListModel(BaseModel):
  sensors: List[SensorModel]

