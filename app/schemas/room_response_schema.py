from pydantic import BaseModel
from typing import List, Dict

class room_data_type(BaseModel):
    rooms: List[Dict]
