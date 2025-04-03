import requests
import pytest

BASE_URL = 'http://gateway:8000'


@pytest.fixture(scope='module')
def sensor_id():
	"""Fixture to get a sensor ID from /sensors endpoint."""
	response = requests.get(BASE_URL + '/sensors')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'sensors' in data
	assert len(data['sensors']) > 0
	sensor_id = data['sensors'][0]['id']

	return sensor_id


def test_sensors():
	"""Test the /sensors endpoint."""
	response = requests.get(BASE_URL + '/sensors')
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert 'sensors' in data
	assert isinstance(data['sensors'], list)
	assert len(data['sensors']) > 0
	for sensor in data['sensors']:
		assert 'id' in sensor
		assert 'rooms' in sensor
		assert isinstance(sensor['id'], str)
		assert isinstance(sensor['rooms'], list)
		assert len(sensor['rooms']) == 2
		for room in sensor['rooms']:
			assert isinstance(room, str)
			assert room.isalnum()


def test_sensor_by_id(sensor_id):
	"""Test the /sensors/{sensor_id} endpoint."""
	response = requests.get(BASE_URL + f'/sensors/{sensor_id}')
	assert response.status_code == 200
	sensor = response.json()
	assert isinstance(sensor, dict)
	assert 'id' in sensor
	assert 'rooms' in sensor
	assert sensor['id'] == sensor_id
	assert isinstance(sensor['rooms'], list)
	assert len(sensor['rooms']) == 2
	for room in sensor['rooms']:
		assert isinstance(room, str)
		assert room.isalnum()
