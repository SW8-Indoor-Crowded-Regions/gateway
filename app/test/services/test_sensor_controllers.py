import pytest
from fastapi import HTTPException
from app.services.sensor_controllers import get_all_sensors, get_sensor_by_id
from app.schemas.sensor_response_schema import SensorModel, SensorListModel


# Mocking the environment variables
@pytest.fixture
def mock_env(monkeypatch):
	monkeypatch.setattr('app.services.sensor_controllers.SENSOR_SIM_PATH', 'http://mock-sensor-sim')
	monkeypatch.setattr(
		'app.services.sensor_controllers.PATHFINDING_PATH', 'http://mock-pathfinding'
	)


# Mocking the forward_request method
@pytest.fixture
def mock_forward_request(mocker):
	return mocker.patch('app.services.sensor_controllers.forward_request')


# Mocking a sample sensor
@pytest.fixture
def mock_sensor():
	return {
		'id': 'sensor_123',
		'rooms': ['room_1', 'room_2'],
		'latitude': 1.0,
		'longitude': 1.0,
	}


# Test for getting all sensors
@pytest.mark.asyncio
async def test_get_all_sensors(mock_env, mock_forward_request, mock_sensor):
	mock_response = {'sensors': [mock_sensor, mock_sensor]}
	mock_forward_request.return_value = (mock_response, 200)

	result = await get_all_sensors()

	assert SensorListModel.model_validate(result) == SensorListModel.model_validate(mock_response)
	mock_forward_request.assert_called_once_with('http://mock-sensor-sim/sensors', 'GET')


# Test for handling invalid response when getting all sensors
@pytest.mark.asyncio
async def test_get_all_sensors_invalid_response(mock_env, mock_forward_request):
	mock_forward_request.return_value = ({'details': 'Invalid response'}, 500)

	with pytest.raises(HTTPException) as exc:
		await get_all_sensors()

	assert exc.value.status_code == 500
	assert exc.value.detail == 'Invalid room data received from sensor simulation service'


# Test for getting a sensor by ID
@pytest.mark.asyncio
async def test_get_sensor_by_id(mock_env, mock_forward_request, mock_sensor):
	sensor_id = 'sensor_123'
	mock_forward_request.return_value = (mock_sensor, 200)

	result = await get_sensor_by_id(sensor_id)

	assert SensorModel.model_validate(result) == SensorModel.model_validate(mock_sensor)
	mock_forward_request.assert_called_once_with(
		f'http://mock-sensor-sim/sensors/{sensor_id}', 'GET'
	)


# Test for handling invalid response when getting a sensor by ID
@pytest.mark.asyncio
async def test_get_sensor_by_id_invalid_response(mock_env, mock_forward_request):
	mock_forward_request.return_value = ({'details': 'This is an error'}, 404)

	with pytest.raises(HTTPException) as exc:
		await get_sensor_by_id('sensor_123')

	assert exc.value.status_code == 404
	assert exc.value.detail == 'Invalid room data received from sensor simulation service'
