from fastapi import HTTPException
from app.utils.forwarder import forward_request
from app.schemas.pathfinding_schema import PathfindingRequest

# Define the URLs for each service.
SERVICES = {
    "sensor_sim": "http://localhost:8002",    # Data processing service (returns room data)
    "pathfinding": "http://localhost:8001"      # Pathfinding service
}

async def calculate_fastest_path(request: PathfindingRequest) -> dict:
    # Validate input: ensure source and target are non-empty.
    if not request.source.strip() or not request.target.strip():
        raise HTTPException(status_code=400, detail="Both 'source' and 'target' must be non-empty strings.")
    
    # Step 1: Query sensor simulation service for room data.
    sensor_sim_url = f"{SERVICES['sensor_sim']}/rooms"
    try:
        room_data = await forward_request(sensor_sim_url, "GET")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve room data from sensor simulation service"
        ) from e

    # Validate room data structure.
    if isinstance(room_data, dict) and "rooms" in room_data:
        room_list = room_data["rooms"]
    elif isinstance(room_data, list):
        room_list = room_data
    else:
        raise HTTPException(
            status_code=500, 
            detail="Invalid or empty room data received from sensor simulation service"
        )
    
    # Step 2: Prepare payload for the pathfinding service.
    payload = {
        "source_sensor": request.source,
        "target_sensor": request.target,
        "rooms": room_list
    }

    # Step 3: Send POST request to the pathfinding service.
    pathfinding_url = f"{SERVICES['pathfinding']}/pathfinding/fastest-path"
    try:
        path_response = await forward_request(pathfinding_url, "POST", body=payload)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to calculate fastest path from pathfinding service"
        ) from e

    # Validate the response from pathfinding.
    if not path_response or not isinstance(path_response, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from pathfinding service"
        )

    return path_response
