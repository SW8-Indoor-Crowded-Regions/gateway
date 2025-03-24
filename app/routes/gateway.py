from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.forwarder import forward_request

router = APIRouter()

# Define the URLs for each service.
SERVICES = {
    "sensor_sim": "http://localhost:8002",    # Data processing service (returns room data)
    "pathfinding": "http://localhost:8001"      # Pathfinding service
}

# Model for the initial request from the frontend.
class PathfindingRequest(BaseModel):
    source: str
    target: str

# Existing test endpoints
@router.get("/test")
async def get_route_test():
    return {"message": "API is working!"}

@router.post("/test")
async def post_route_test(request: BaseModel):
    # Example test endpoint, adjust as needed.
    return {"message": "Received test data."}

# New endpoint to handle the complete flow.
@router.post("/fastest_path")
async def get_fastest_path(request: PathfindingRequest):
    # Guard clause: ensure source and target are non-empty.
    if not request.source.strip() or not request.target.strip():
        raise HTTPException(status_code=400, detail="Both 'source' and 'target' must be non-empty strings.")
    
    # Step 1: Query sensor simulation service for all room data.
    sensor_sim_url = f"{SERVICES['sensor_sim']}/rooms"
    try:
        room_data = await forward_request(sensor_sim_url, "GET")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve room data from sensor simulation service"
        ) from e

    # Guard clause: validate room_data is present and of expected type.
    if not room_data or not isinstance(room_data, (list, dict)):
        raise HTTPException(
            status_code=500, 
            detail="Invalid or empty room data received from sensor simulation service"
        )

    # Step 2: Prepare payload for the pathfinding service, including the room data.
    payload = {
        "source": request.source,
        "target": request.target,
        "rooms": room_data
    }
    pathfinding_url = f"{SERVICES['pathfinding']}/fastest_path"
    try:
        # Step 3: Send POST request to the pathfinding service.
        path_response = await forward_request(pathfinding_url, "POST", body=payload)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to calculate fastest path from pathfinding service"
        ) from e

    # Guard clause: ensure that the response from pathfinding is valid.
    if not path_response or not isinstance(path_response, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from pathfinding service"
        )

    # Return the result from the pathfinding service to the frontend.
    return path_response
