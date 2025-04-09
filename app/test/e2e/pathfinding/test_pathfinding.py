import pytest
import requests

@pytest.fixture(scope='module')
def sensor_ids():
	"""Fixture to get a room ID from /sensors endpoint."""
	BASE_URL = 'http://gateway:8000'

	response = requests.get(BASE_URL + '/sensors')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'sensors' in data
	assert len(data['sensors']) > 0
	sensor_id1 = data['sensors'][0]['id']
	sensor_id2 = data['sensors'][20]['id']
	return sensor_id1, sensor_id2

def test_pathfinding(sensor_ids):
	"""Test the /fastest-path endpoint."""

	BASE_URL = 'http://gateway:8000'
 
	sensor_id1, sensor_id2 = sensor_ids

	# Define the request body
	request_body = {
		"source": sensor_id1,
		"target": sensor_id2,
	}

	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
 
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'fastest_path' in data
	assert isinstance(data['fastest_path'], list)
	assert len(data['fastest_path']) > 0
	for sensor in data['fastest_path']:
		assert isinstance(sensor, dict)
		assert 'id' in sensor
		assert isinstance(sensor['id'], str)
		assert sensor['id'].isalnum()
		assert 'latitude' in sensor
		assert isinstance(sensor['latitude'], float)
		assert 'longitude' in sensor
		assert isinstance(sensor['longitude'], float)
	assert 'distance' in data
	assert isinstance(data['distance'], (int, float))
 
 
def test_pathfinding_invalid_source(sensor_ids):
	"""Test the /fastest-path endpoint with invalid source."""
	BASE_URL = 'http://gateway:8000'
	sensor_id1, sensor_id2 = sensor_ids
	# Define the request body
	request_body = {
		"source": "invalid_source",
		"target": sensor_id2,
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail']['error'] == "Source sensor 'invalid_source' not found in the sensor graph."
 
def test_pathfinding_invalid_target(sensor_ids):
	"""Test the /fastest-path endpoint with invalid target."""
	BASE_URL = 'http://gateway:8000'
	sensor_id1, sensor_id2 = sensor_ids
	# Define the request body
	request_body = {
		"source": sensor_id1,
		"target": "invalid_target",
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail']['error'] == "Target sensor 'invalid_target' not found in the sensor graph."
 
def test_pathfinding_empty_source(sensor_ids):
	"""Test the /fastest-path endpoint with empty source."""
	BASE_URL = 'http://gateway:8000'
	sensor_id1, sensor_id2 = sensor_ids
	# Define the request body
	request_body = {
		"source": "",
		"target": sensor_id2,
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 422
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail'] == [{
		'ctx': {
			'error': {}
		},
		'input': '',
		'type': 'value_error',
		'loc': ['body', 'source'],
		'msg': "Value error, Field 'source' must be a non-empty string."
	}]
 
def test_pathfinding_no_target(sensor_ids):
	"""Test the /fastest-path endpoint with no target."""
	BASE_URL = 'http://gateway:8000'
	sensor_id1, sensor_id2 = sensor_ids
	# Define the request body
	request_body = {
		"source": sensor_id1,
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 422
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail'] == [{
		'input': {
			'source': sensor_id1
   	},
		'type': 'missing',
		'loc': ['body', 'target'],
		'msg': "Field required"
	}]