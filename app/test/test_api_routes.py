import os
import importlib
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

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: {
        "SENSOR_SIM": "http://mock-sensor-sim",
        "PATHFINDING": "http://mock-pathfinding"
    }.get(key, default))


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
async def test_blank_input():
    request = path_finding_request(source="   ", target="RoomA")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 400
    assert "non-empty" in exc_info.value.detail

@pytest.mark.asyncio
async def test_room_data_forward_exception(monkeypatch):
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
    async def fake_forward_request(url, method, body=None, params=None):
        return "invalid data structure"
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    with pytest.raises(HTTPException) as exc_info:
        await pathfinding_service.calculate_fastest_path(request)
    assert exc_info.value.status_code == 500
    assert "Invalid or empty room data" in exc_info.value.detail

@pytest.mark.asyncio
async def test_success(monkeypatch):
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
        pytest.fail("should not make more than 3 calls in the test")
    monkeypatch.setattr(pathfinding_service, "forward_request", fake_forward_request)
    request = path_finding_request(source="RoomA", target="RoomB")
    response = await pathfinding_service.calculate_fastest_path(request)
    assert response.model_dump() == VALID_FASTEST_PATH_RESPONSE

# Tests for missing environment variables

def test_missing_pathfinding(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: None if key == "PATHFINDING" else default)
    with pytest.raises(RuntimeError, match="PATHFINDING not found"):
        importlib.reload(pathfinding_service)

def test_missing_sensor_sim(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: None if key == "SENSOR_SIM" else default)
    with pytest.raises(RuntimeError, match="SENSOR_SIM not found"):
        importlib.reload(pathfinding_service)
