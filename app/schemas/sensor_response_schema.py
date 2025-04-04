from pydantic import BaseModel
from typing import List

class SensorModel(BaseModel):
	id: str
	rooms: List[str]
		  

class SensorListModel(BaseModel):
  sensors: List[SensorModel]

