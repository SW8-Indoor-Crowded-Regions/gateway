#import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the router from the new structure.
from app.routes.api_routes import router
# forward_request will be monkeypatched in some tests.

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Tests for the "/test" endpoints

def test_get_route_test():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "API is working!"}

def test_post_route_test():
    # Since the POST endpoint accepts any valid JSON as a BaseModel,
    # sending an empty JSON object should be sufficient.
    response = client.post("/test", json={})
    assert response.status_code == 200
    assert response.json() == {"message": "Received test data."}

# Tests for the "/fastest-path" endpoint guard clauses

# Test: Blank source value should trigger 400 error.
def test_blank_source():
    payload = {"source": "   ", "target": "RoomA"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 400
    assert "non-empty" in response.json()["detail"]

# Test: Blank target value should trigger 400 error.
def test_blank_target():
    payload = {"source": "RoomA", "target": "   "}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 400
    assert "non-empty" in response.json()["detail"]

# Test: Simulate sensor simulation service failure (first forward_request call fails).
def test_sensor_sim_failure(monkeypatch):
    async def fake_forward_request(*args, **kwargs):
        raise Exception("Sensor service error")
    monkeypatch.setattr("app.services.pathfinding_service.forward_request", fake_forward_request)

    payload = {"source": "RoomA", "target": "RoomB"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 500
    assert "Failed to retrieve room data" in response.json()["detail"]

# Test: When sensor service returns invalid room data (not a dict with 'rooms' key or a list).
def test_invalid_room_data(monkeypatch):
    async def fake_forward_request(*args, **kwargs):
        return "invalid data"
    monkeypatch.setattr("app.services.pathfinding_service.forward_request", fake_forward_request)

    payload = {"source": "RoomA", "target": "RoomB"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 500
    assert "Invalid or empty room data" in response.json()["detail"]

# Test: Simulate failure from the pathfinding service (second forward_request call fails).
def test_pathfinding_failure(monkeypatch):
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call: sensor simulation returns valid room data.
            return {"rooms": [{"id": "room1"}, {"id": "room2"}]}
        elif call_count == 2:
            raise Exception("Pathfinding error")
    monkeypatch.setattr("app.services.pathfinding_service.forward_request", fake_forward_request)

    payload = {"source": "RoomA", "target": "RoomB"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 500
    assert "Failed to calculate fastest path" in response.json()["detail"]

# Test: When pathfinding returns an invalid response (not a dict).
def test_invalid_pathfinding_response(monkeypatch):
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Return valid room data.
            return {"rooms": [{"id": "room1"}, {"id": "room2"}]}
        elif call_count == 2:
            # Return an invalid response.
            return None
    monkeypatch.setattr("app.services.pathfinding_service.forward_request", fake_forward_request)

    payload = {"source": "RoomA", "target": "RoomB"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 500
    assert "Invalid response from pathfinding service" in response.json()["detail"]

# Test: A successful flow where both forward_request calls return valid data.
def test_success(monkeypatch):
    call_count = 0
    async def fake_forward_request(url, method, body=None, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Return room data as a list.
            return [{"id": "room1"}, {"id": "room2"}]
        elif call_count == 2:
            # Return a valid pathfinding response.
            return {"path": ["RoomA", "room1", "RoomB"], "cost": 10}
    monkeypatch.setattr("app.services.pathfinding_service.forward_request", fake_forward_request)

    payload = {"source": "RoomA", "target": "RoomB"}
    response = client.post("/fastest-path", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    assert "path" in json_response
    assert "cost" in json_response
