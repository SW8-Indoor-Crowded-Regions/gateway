from pydantic import BaseModel
from typing import List, Dict

class sensor_data_type(BaseModel):
    sensors: List[Dict]