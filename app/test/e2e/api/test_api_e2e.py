import requests
import pytest

BASE_URL = 'http://gateway:8000'


def get_room_id(room_name: str | None = None):
	"""Fixture to get a room ID from /rooms endpoint."""
	response = requests.get(BASE_URL + '/rooms')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'rooms' in data
	assert len(data['rooms']) > 0
	if room_name:
		room = next((room for room in data['rooms'] if room['name'] == room_name), None)
		assert room is not None, f"Room with name '{room_name}' not found."
		room_id = room['id']
	else:
		room_id = data['rooms'][0]['id']
	return room_id

def test_artwork_query():
	"""Test the /artwork endpoint."""
	response = requests.get(BASE_URL + '/artwork')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'items' in data
	assert isinstance(data['items'], list)
	assert len(data['items']) > 0
	for artwork in data['items']:
		assert 'titles' in artwork
		assert 'artist' in artwork
		assert 'techniques' in artwork
		assert 'colors' in artwork
		assert 'dimensions' in artwork


def test_artwork_query_room():
	"""Test the /artwork endpoint with a room ID."""
	room_id = get_room_id('217A')
	response = requests.get(BASE_URL + f'/artwork?room={room_id}')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'items' in data
	assert isinstance(data['items'], list)
	assert len(data['items']) > 0
	for artwork in data['items']:
		assert 'titles' in artwork
		assert 'artist' in artwork
		assert 'techniques' in artwork
		assert 'colors' in artwork
		assert 'dimensions' in artwork

def test_artwork_query_room_not_found():
	"""Test the /artwork endpoint with a room ID that does not exist."""
	invalid_room_id = "deadbeefdeadbeefdeadbeef"
	response = requests.get(BASE_URL + f'/artwork?room={invalid_room_id}')
	assert response.status_code == 404
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert 'error' in data['detail']
	assert data['detail']['error'] == 'Room not found.'
 
def test_artwork_query_room_invalid():
	"""Test the /artwork endpoint with an invalid room ID."""
	room_id = get_room_id('217A')
	response = requests.get(BASE_URL + f'/artwork?room={room_id}invalid')
	assert response.status_code == 400
	data = response.json()
	assert isinstance(data, dict)
	assert 'detail' in data
	assert 'error' in data['detail']
	assert data['detail']['error'] == 'Invalid room id.'
 
 
