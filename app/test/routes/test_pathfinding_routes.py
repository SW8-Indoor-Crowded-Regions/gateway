from fastapi import FastAPI
from fastapi.testclient import TestClient
import importlib
import pytest

# Import the router from the new structure.
from app.routes.api_routes import router
from app.services import pathfinding_service
from app.utils import room_sensor_fetch
from app.test.factories.sensor_factory import SensorFactory
from app.test.factories.room_factory import RoomFactory


app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
	monkeypatch.setattr(
		'app.services.pathfinding_service.os.getenv',
		lambda key, default=None: {
			'SENSOR_SIM': 'http://mock-sensor-sim',
			'PATHFINDING': 'http://mock-pathfinding',
		}.get(key, default),
	)


@pytest.fixture()
def valid_room_data():
	return {
		'rooms': [
			room.to_dict() for room in [RoomFactory() for _ in range(10)]
		],
	}


@pytest.fixture
def valid_sensor_data():
    return {
        "sensors": [sensor.to_dict() for sensor in [SensorFactory() for _ in range(10)]],
    }


@pytest.fixture
def valid_fastest_path_response():
	return {"fastest_path": [
			{
				"id": "67d935b1d6d3ce76bef2c8e9",
				"longitude": 16.369509547137667,
				"latitude": 23.8621854675587,
				"rooms": [
					{
						"id": "67d935add6d3ce76bef2c884",
						"name": "106",
						"crowd_factor": 0.3,
						"occupants": 15,
						"area": 50.0,
						"popularity_factor": 0.6133044537264026
					},
					{
						"id": "67d935add6d3ce76bef2c883",
						"name": "107",
						"crowd_factor": 0.3,
						"occupants": 12,
						"area": 50.0,
						"popularity_factor": 0.19071676094915843
					}
				]
			},
			{
				"id": "67d935b1d6d3ce76bef2c8ea",
				"longitude": 61.74727469899295,
				"latitude": 72.87442522121299,
				"rooms": [
					{
						"id": "67d935add6d3ce76bef2c885",
						"name": "105",
						"crowd_factor": 0.3,
						"occupants": 3,
						"area": 50.0,
						"popularity_factor": 0.3210981611492981
					},
					{
						"id": "67d935add6d3ce76bef2c884",
						"name": "106",
						"crowd_factor": 0.3,
						"occupants": 15,
						"area": 50.0,
						"popularity_factor": 0.6133044537264026
					}
				]
			}
		],
		"distance": 0.09
	}


# Test: Blank source value should trigger 400 error.
def test_blank_source():
	payload = {'source': '   ', 'target': 'RoomA'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 422
	assert response.json()['detail'] == [
		{
			'ctx': {'error': {}},
			'input': '   ',
			'type': 'value_error',
			'loc': ['body', 'source'],
			'msg': "Value error, Field 'source' must be a non-empty string.",
		}
	]


# Test: Blank target value should trigger 400 error.
def test_blank_target():
	payload = {'source': 'RoomA', 'target': '   '}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 422
	assert response.json()['detail'] == [
		{
			'ctx': {'error': {}},
			'input': '   ',
			'type': 'value_error',
			'loc': ['body', 'target'],
			'msg': "Value error, Field 'target' must be a non-empty string.",
		}
	]


# Test: Simulate sensor simulation service failure (first forward_request call fails).
def test_sensor_sim_failure(monkeypatch):
	async def fake_forward_request(*args, **kwargs):
		raise Exception('Sensor service error')

	monkeypatch.setattr('app.utils.room_sensor_fetch.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert 'Failed to retrieve room data' in response.json()['detail']


# Test: When sensor service returns invalid room data (not a dict with 'rooms' key or a list).
def test_invalid_room_data(monkeypatch):
	async def fake_forward_request(*args, **kwargs):
		return 'invalid data', 200

	monkeypatch.setattr('app.utils.room_sensor_fetch.forward_request', fake_forward_request)

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

	monkeypatch.setattr('app.utils.room_sensor_fetch.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert (
		'Failed to retrieve sensor data from sensor simulation service' in response.json()['detail']
	)


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

	monkeypatch.setattr('app.utils.room_sensor_fetch.forward_request', fake_forward_request)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 500
	assert (
		'Invalid or empty sensor data received from sensor simulation service'
		in response.json()['detail']
	)


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
		else:
			raise Exception(f'Unexpected API call with count {call_count}')

	async def fake_forward_request_path(url, method, body=None, params=None):
		return valid_fastest_path_response, 200

	monkeypatch.setattr('app.utils.room_sensor_fetch.forward_request', fake_forward_request)
	monkeypatch.setattr('app.services.pathfinding_service.forward_request', fake_forward_request_path)

	payload = {'source': 'RoomA', 'target': 'RoomB'}
	response = client.post('/fastest-path', json=payload)
	assert response.status_code == 200, f'Unexpected status code: {response.json()}'
	json_response = response.json()
	assert 'fastest_path' in json_response
	assert 'distance' in json_response


def test_missing_pathfinding(monkeypatch):
	monkeypatch.setattr(
		'app.services.pathfinding_service.os.getenv',
		lambda key, default=None: None if key == 'PATHFINDING' else default,
	)
	with pytest.raises(RuntimeError, match='PATHFINDING not found'):
		importlib.reload(pathfinding_service)


def test_missing_sensor_sim(monkeypatch):
	monkeypatch.setattr(
		'app.utils.room_sensor_fetch.os.getenv',
		lambda key, default=None: None if key == 'SENSOR_SIM' else default,
	)
	with pytest.raises(RuntimeError, match='SENSOR_SIM not found'):
		importlib.reload(room_sensor_fetch)
