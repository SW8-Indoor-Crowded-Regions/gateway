import requests
import pytest

BASE_URL = 'http://gateway:8000' 

@pytest.fixture(scope="module")
def room_id():
    """Fixture to get a room ID from /rooms endpoint."""
    response = requests.get(BASE_URL + '/rooms')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'rooms' in data
    assert len(data['rooms']) > 0
    room_id = data['rooms'][0]['id']
    return room_id

def test_rooms():
	"""Test the /rooms endpoint."""
	response = requests.get(BASE_URL + '/rooms')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'rooms' in data
	assert isinstance(data['rooms'], list)
	assert len(data['rooms']) > 0
	print(data['rooms'][0]['id'])
	for room in data['rooms']:
		assert 'id' in room
		assert 'name' in room
		assert 'crowd_factor' in room
		assert 'occupants' in room
		assert 'area' in room
		assert 'longitude' in room
		assert 'latitude' in room
		assert 'type' in room
		assert isinstance(room['id'], str)
		assert isinstance(room['name'], str)
		assert isinstance(room['crowd_factor'], (int, float))
		assert isinstance(room['occupants'], (int, float))
		assert isinstance(room['area'], (int, float))
		assert isinstance(room['longitude'], (int, float))
		assert isinstance(room['latitude'], (int, float))
		assert isinstance(room['type'], str)
  
def test_room_by_id(room_id):
	"""Test the /rooms/{room_id} endpoint."""
	response = requests.get(BASE_URL + f'/rooms/{room_id}')
	assert response.status_code == 200
	room = response.json()
	assert isinstance(room, dict)
	assert 'id' in room
	assert 'name' in room
	assert 'crowd_factor' in room
	assert 'occupants' in room
	assert 'area' in room
	assert 'longitude' in room
	assert 'latitude' in room
	assert 'type' in room
	assert isinstance(room['id'], str)
	assert isinstance(room['name'], str)
	assert isinstance(room['crowd_factor'], (int, float))
	assert isinstance(room['occupants'], (int, float))
	assert isinstance(room['area'], (int, float))
	assert isinstance(room['longitude'], (int, float))
	assert isinstance(room['latitude'], (int, float))
	assert isinstance(room['type'], str)