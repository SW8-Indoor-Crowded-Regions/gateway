from pydantic import BaseModel

class PathfindingRequest(BaseModel):
    source: str
    target: str