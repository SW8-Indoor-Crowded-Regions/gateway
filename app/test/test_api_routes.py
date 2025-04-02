import os
import importlib
import asyncio
import pytest
from fastapi import HTTPException

# Import the models to create valid requests/responses.
from app.schemas.pathfinding_schema import path_finding_request

# Import the function under test.
from app.services import pathfinding_service

# Dummy valid data for each service call.
VALID_ROOM_DATA = {"rooms": [{"id": "room1"}, {"id": "room2"}]}
VALID_SENSOR_DATA = {"sensors": [{"id": "sensor1"}, {"id": "sensor2"}]}
VALID_FASTEST_PATH_RESPONSE = {"fastest_path": ["RoomA", "room1", "RoomB"], "distance": 10}


# -------------------------------
# Tests for calculate_fastest_path
# -------------------------------

@pytest.mark.asyncio
async def test_blank_input():
    # Test that blank source (or target) triggers 400 error.
    request = path_finding_request(source="   ", target="RoomA")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 400
    assert "non-empty" in exc_info.value.detail

@pytest.mark.asyncio
async def test_room_data_forward_exception(monkeypatch):
    # Simulate exception during room data retrieval (first forward_request call).
    async def fake_forward_request(url, method, body=None, params=None):
        raise Exception("Room data fetch error")
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Failed to retrieve room data" in exc_info.value.detail

@pytest.mark.asyncio
async def test_invalid_room_data(monkeypatch):
    # Simulate invalid room data causing model validation failure.
    async def fake_forward_request(url, method, body=None, params=None):
        return "invalid data"
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Invalid or empty room data" in exc_info.value.detail

@pytest.mark.asyncio
async def test_sensor_data_forward_exception(monkeypatch):
    # Simulate exception during sensor data retrieval (second forward_request call).
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return VALID_ROOM_DATA
        elif call_count == 2:
            raise Exception("Sensor data fetch error")
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Failed to retrieve sensor data" in exc_info.value.detail

@pytest.mark.asyncio
async def test_invalid_sensor_data(monkeypatch):
    # Simulate invalid sensor data causing model validation failure.
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return VALID_ROOM_DATA
        elif call_count == 2:
            return "invalid sensor data"
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Invalid or empty sensor data" in exc_info.value.detail

@pytest.mark.asyncio
async def test_pathfinding_forward_exception(monkeypatch):
    # Simulate exception during the pathfinding service call (third forward_request call).
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return VALID_ROOM_DATA
        elif call_count == 2:
            return VALID_SENSOR_DATA
        elif call_count == 3:
            raise Exception("Pathfinding service error")
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Failed to calculate fastest path" in exc_info.value.detail

@pytest.mark.asyncio
async def test_invalid_pathfinding_response(monkeypatch):
    # Simulate invalid pathfinding response causing model validation failure.
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return VALID_ROOM_DATA
        elif call_count == 2:
            return VALID_SENSOR_DATA
        elif call_count == 3:
            return "invalid path response"
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Invalid response from pathfinding service" in exc_info.value.detail

@pytest.mark.asyncio
async def test_success(monkeypatch):
    # Simulate a successful flow with all valid responses.
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return VALID_ROOM_DATA
        elif call_count == 2:
            return VALID_SENSOR_DATA
        elif call_count == 3:
            return VALID_FASTEST_PATH_RESPONSE
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    response = await pathfinding_service.calculate_fastest_path(request)
    # Compare dictionaries (assuming fastest_path_type is a Pydantic model)
    assert response.dict() == VALID_FASTEST_PATH_RESPONSE

# -----------------------------------------------
# Tests to trigger module-level environment variable errors
# -----------------------------------------------

def test_missing_sensor_sim(monkeypatch):
    # Override os.getenv so that SENSOR_SIM returns None.
    original_getenv = os.getenv
    def fake_getenv(key, default=None):
        if key == "SENSOR_SIM":
            return None
        return original_getenv(key, default)
    monkeypatch.setattr(os, "getenv", fake_getenv)
    # Reload the module so that the module-level code runs again.
    with pytest.raises(RuntimeError, match="SENSOR_SIM not found"):
        importlib.reload(pathfinding_service)

def test_missing_pathfinding(monkeypatch):
    # Override os.getenv so that PATHFINDING returns None.
    original_getenv = os.getenv
    def fake_getenv(key, default=None):
        if key == "PATHFINDING":
            return None
        return original_getenv(key, default)
    monkeypatch.setattr(os, "getenv", fake_getenv)
    with pytest.raises(RuntimeError, match="PATHFINDING not found"):
        importlib.reload(pathfinding_service)
