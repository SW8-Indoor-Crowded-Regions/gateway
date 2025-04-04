from pydantic import BaseModel
from typing import List

class FrontendPathFindingRequest(BaseModel):
    source: str
    target: str

class FastestPathModel(BaseModel):
    fastest_path: List[str]
    distance: float