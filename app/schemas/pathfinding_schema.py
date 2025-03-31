from pydantic import BaseModel
from typing import List

class path_finding_request(BaseModel):
    source: str
    target: str

class fastest_path_type(BaseModel):
    fastest_path: List[str]
    distance: float