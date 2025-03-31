from fastapi import HTTPException
from app.utils.forwarder import forward_request
from app.schemas.pathfinding_schema import path_finding_request, fastest_path_type
from app.schemas.room_response_schema import room_data_type
from app.schemas.sensor_response_schema import sensor_data_type

import os
from dotenv import load_dotenv

load_dotenv()
SENSOR_SIM_PATH = os.getenv("SENSOR_SIM", "http://localhost:8002")
if SENSOR_SIM_PATH is None:
    raise RuntimeError("SENSOR_SIM not found in environment variables")

PATHFINDING_PATH = os.getenv("PATHFINDING", "http://localhost:8001")
if PATHFINDING_PATH is None:
    raise RuntimeError("PATHFINDING not found in environment variables")

async def calculate_fastest_path(request: path_finding_request) -> fastest_path_type:
    # Validate input: ensure source and target are non-empty.
    if not request.source.strip() or not request.target.strip():
        raise HTTPException(status_code=400, detail="Both 'source' and 'target' must be non-empty strings.")
    
    # Query sensor simulation service for room data.
    sensor_sim_rooms_url = f"{SENSOR_SIM_PATH}/rooms"
    sensor_sim_sensors_url = f"{SENSOR_SIM_PATH}/sensors"

    try:
        room_data = await forward_request(sensor_sim_rooms_url, "GET")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve room data from sensor simulation service"
        ) from e

    try:
        validated_room_data = room_data_type.model_validate(room_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Invalid or empty room data received from sensor simulation service"
        ) from e
    
    room_list = validated_room_data.rooms   

    try:
        sensor_data = await forward_request(sensor_sim_sensors_url, "GET")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve sensor data from sensor simulation service"
        ) from e

    try:
        validated_sensor_data = sensor_data_type.model_validate(sensor_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Invalid or empty sensor data received from sensor simulation service"
        ) from e
    
    # Extract the inner list of sensors to ensure JSON serializability.
    sensor_list = validated_sensor_data.sensors

    # Prepare payload for the pathfinding service.
    payload = {
        "source_sensor": request.source,
        "target_sensor": request.target,
        "rooms": room_list,
        "sensors": sensor_list
    }

    # Send POST request to the pathfinding service.
    pathfinding_url = f"{PATHFINDING_PATH}/pathfinding/fastest-path"

    try:
        path_response = await forward_request(pathfinding_url, "POST", body=payload)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to calculate fastest path from pathfinding service"
        ) from e

    try:
        path_response = fastest_path_type.model_validate(path_response)        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Invalid response from pathfinding service"
        ) from e

    return path_response
