from fastapi import FastAPI
from fastapi.testclient import TestClient
import importlib
import pytest

# Import the router from the new structure.
from app.routes.api_routes import router
from app.services import pathfinding_service


app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: {
        "SENSOR_SIM": "http://mock-sensor-sim",
        "PATHFINDING": "http://mock-pathfinding"
    }.get(key, default))

@pytest.fixture()
def valid_room_data():
	return {
		'rooms': [
			{
				'id': 'room1',
				'name': 'RoomA',
				'type': 'EXHIBITION',
				'crowd_factor': 0.5,
				'occupants': 10,
				'area': 100.0,
				'longitude': 1.0,
				'latitude': 1.0,
				'popularity_factor': 1.0
			},
			{
				'id': 'room2',
				'name': 'RoomB',
				'type': 'EXHIBITION',
				'crowd_factor': 0.5,
				'occupants': 10,
				'area': 100.0,
				'longitude': 1.0,
				'latitude': 1.0,
				'popularity_factor': 1.0
			},
		]
	}

@pytest.fixture
def valid_sensor_data():
    return {
        "sensors": [
            {"id": "sensor1", "rooms": ["RoomA", "RoomB"], "latitude": 55.6887823848, "longitude": 12.57792893289},
            {"id": "sensor2", "rooms": ["RoomA", "RoomB"], "latitude": 55.6887823848, "longitude": 12.57792893289}
        ]
    }
@pytest.fixture
def valid_fastest_path_response():
	return {"fastest_path": [
  	{"id": "RoomA", "latitude": 55.6887823848, "longitude": 12.57792893289},
   	{"id": "room1", "latitude": 55.6887823848, "longitude": 12.57792893289},
   	{"id": "RoomB", "latitude": 55.6887823848, "longitude": 12.57792893289}],
  	"distance": 10}

def test_health_check():
	response = client.get('/health')
	assert response.status_code == 200
	assert response.json() == {'status': 'ok'}

# Test: Blank source value should trigger 400 error.
def test_blank_source():
	payload = {'source': '   ', 'target': 'RoomA'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 400
	assert 'non-empty' in response.json()['detail']


# Test: Blank target value should trigger 400 error.
def test_blank_target():
	payload = {'source': 'RoomA', 'target': '   '}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 400
	assert 'non-empty' in response.json()['detail']


# Test: Simulate sensor simulation service failure (first forward_request call fails).
def test_sensor_sim_failure(monkeypatch):
	async def fake_forward_request(*args, **kwargs):
		raise Exception('Sensor service error')

	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert 'Failed to retrieve room data' in response.json()['detail']


# Test: When sensor service returns invalid room data (not a dict with 'rooms' key or a list).
def test_invalid_room_data(monkeypatch):
	async def fake_forward_request(*args, **kwargs):
		return 'invalid data', 200

	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert 'Invalid or empty room data' in response.json()['detail']


# Test: Simulate failure from the pathfinding service (second forward_request call fails).
def test_pathfinding_failure(monkeypatch, valid_room_data):
	call_count = 0

	async def fake_forward_request(url, method, body=None, params=None):
		nonlocal call_count
		call_count += 1
		if call_count == 1:
			# First call: sensor simulation returns valid room data.
			return valid_room_data, 200
		elif call_count == 2:
			raise Exception('Pathfinding error')

	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert 'Failed to retrieve sensor data from sensor simulation service' in response.json()['detail']


# Test: When pathfinding returns an invalid response (not a dict).
def test_invalid_pathfinding_response(monkeypatch, valid_room_data):
	call_count = 0

	async def fake_forward_request(url, method, body=None, params=None):
		nonlocal call_count
		call_count += 1
		if call_count == 1:
			# Return valid room data.
			return valid_room_data, 200
		elif call_count == 2:
			# Return an invalid response.
			return {}, 500

	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert 'Invalid or empty sensor data received from sensor simulation service' in response.json()['detail']


# Test: A successful flow where both forward_request calls return valid data.
def test_success(monkeypatch, valid_room_data, valid_sensor_data, valid_fastest_path_response):
	call_count = 0

	async def fake_forward_request(url, method, body=None, params=None):
		nonlocal call_count
		call_count += 1
		if call_count == 1:
			# Return room data as a dictionary with a "rooms" key.
			return valid_room_data, 200
		elif call_count == 2:
			# return sensor data 
			return valid_sensor_data, 200
		elif call_count == 3:
			# Return a valid pathfinding response with the expected keys.
			return valid_fastest_path_response, 200
		else:
			raise Exception(f"Unexpected API call with count {call_count}")
		
	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 200
	json_response = response.json()
	assert 'fastest_path' in json_response
	assert 'distance' in json_response

def test_missing_pathfinding(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: None if key == "PATHFINDING" else default)
    with pytest.raises(RuntimeError, match="PATHFINDING not found"):
        importlib.reload(pathfinding_service)

def test_missing_sensor_sim(monkeypatch):
    monkeypatch.setattr("app.services.pathfinding_service.os.getenv", lambda key, default=None: None if key == "SENSOR_SIM" else default)
    with pytest.raises(RuntimeError, match="SENSOR_SIM not found"):
        importlib.reload(pathfinding_service)
