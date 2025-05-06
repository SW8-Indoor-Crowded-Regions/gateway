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
	room_id3 = data['rooms'][40]['id']
	return room_id1, room_id2, room_id3

@pytest.fixture(scope='module')
def room_names():
	"""Fixture to get room names from /rooms endpoint."""
	BASE_URL = 'http://gateway:8000'

	response = requests.get(BASE_URL + '/rooms')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'rooms' in data
	assert len(data['rooms']) > 0
	room_name1 = data['rooms'][0]['name']
	room_name2 = data['rooms'][20]['name']
	room_name3 = data['rooms'][40]['name']
	return room_name1, room_name2, room_name3


def test_pathfinding(room_ids, room_names):
	"""Test the /multi-point-path endpoint."""

	BASE_URL = 'http://gateway:8000'
 
	room_id1, room_id2, room_id3 = room_ids
	room_name1, room_name2, room_name3 = room_names

	# Define the request body
	request_body = {
		"source": room_id1,
		"targets": [room_name2, room_name3],
	}

	response = requests.post(BASE_URL + '/multi-point-path', json=request_body)
	

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
 
 
def test_pathfinding_invalid_source(room_ids, room_names):
	"""Test the /multi-point-path endpoint with invalid source."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2, room_id3 = room_ids
	room_name1, room_name2, room_name3 = room_names
	
	# Define the request body
	request_body = {
		"source": "invalid_source",
		"targets": [room_name2, room_name3],
	}
	response = requests.post(BASE_URL + '/multi-point-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'error' in data
	assert 'detail' in data['error']
	assert data['error']['detail'] == "Room 'invalid_source' in the tour is not valid."
 
def test_pathfinding_invalid_target(room_ids, room_names):
	"""Test the /multi-point-path endpoint with invalid target."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2, room_id3 = room_ids
	room_name1, room_name2, room_name3 = room_names
 
	# Define the request body
	request_body = {
		"source": room_id1,
		"targets": ["invalid_target"],
	}
	response = requests.post(BASE_URL + '/multi-point-path', json=request_body)
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail'] == "No valid target rooms found in the request."
 
def test_pathfinding_empty_source(room_ids, room_names):
	"""Test the /multi-point-path endpoint with empty source."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2, room_id3 = room_ids
	room_name1, room_name2, room_name3 = room_names
 
	# Define the request body
	request_body = {
		"source": "",
		"targets": [room_name2, room_name3],
	}
	response = requests.post(BASE_URL + '/multi-point-path', json=request_body)
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
 
def test_pathfinding_no_target(room_ids, room_names):
	"""Test the /multi-point-path endpoint with no target."""
	BASE_URL = 'http://gateway:8000'
	room_id1, room_id2, room_id3 = room_ids
	room_name1, room_name2, room_name3 = room_names

	# Define the request body
	request_body = {
		"source": room_id1,
	}
	print(f"URL: {BASE_URL + '/multi-point-path'}")
	response = requests.post(BASE_URL + '/multi-point-path', json=request_body)
	assert response.status_code == 422
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert data['detail'] == [{
		'type': 'missing',
		'loc': ['body', 'targets'],
		'msg': 'Field required',
		'input': {'source': room_id1}
	}]