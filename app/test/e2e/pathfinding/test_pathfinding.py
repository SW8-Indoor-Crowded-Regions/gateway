import pytest
import requests
import logging

@pytest.fixture(scope='module')
def room_ids():
	"""Fixture to get a room ID from /rooms endpoint."""
	BASE_URL = 'http://gateway:8000'

	response = requests.get(BASE_URL + '/rooms')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'rooms' in data
	assert len(data['rooms']) > 0
	room_id1 = data['rooms'][0]['id']
	room_id2 = data['rooms'][20]['id']
	return room_id1, room_id2

def test_pathfinding(room_ids):
	"""Test the /fastest-path endpoint."""

	BASE_URL = 'http://gateway:8000'
 
	room_id1, room_id2 = room_ids

	# Define the request body
	request_body = {
		"source": room_id1,
		"target": room_id2,
	}

	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	

	data = response.json()
	logging.error(f"Response: {data}")
	assert response.status_code == 200
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
 
 
def test_pathfinding_invalid_source(room_ids):
	"""Test the /fastest-path endpoint with invalid source."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2 = room_ids
	# Define the request body
	request_body = {
		"source": "invalid_source",
		"target": room_id2,
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail']['error'] == "Source room 'invalid_source' is not valid."
 
def test_pathfinding_invalid_target(room_ids):
	"""Test the /fastest-path endpoint with invalid target."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2 = room_ids
	# Define the request body
	request_body = {
		"source": room_id1,
		"target": "invalid_target",
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail']['error'] == "Target room 'invalid_target' is not valid."
 
def test_pathfinding_empty_source(room_ids):
	"""Test the /fastest-path endpoint with empty source."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2 = room_ids
	# Define the request body
	request_body = {
		"source": "",
		"target": room_id2,
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
 
def test_pathfinding_no_target(room_ids):
	"""Test the /fastest-path endpoint with no target."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2 = room_ids
	# Define the request body
	request_body = {
		"source": room_id1,
	}
	response = requests.post(BASE_URL + '/fastest-path', json=request_body)
	assert response.status_code == 422
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail'] == [{
		'input': {
			'source': room_id1
   	},
		'type': 'missing',
		'loc': ['body', 'target'],
		'msg': "Field required"
	}]