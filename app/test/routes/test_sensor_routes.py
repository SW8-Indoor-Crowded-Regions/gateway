import pytest
from fastapi.testclient import TestClient
from app.routes.api_routes import router
from fastapi import HTTPException
from app.test.factories.sensor_factory import SensorFactory


@pytest.fixture
def mock_get_all_sensors(mocker):
	return mocker.patch('app.routes.sensor_routes.get_all_sensors')


@pytest.fixture
def mock_get_sensor_by_id(mocker):
	return mocker.patch('app.routes.sensor_routes.get_sensor_by_id')


@pytest.fixture
def client():
	with TestClient(router) as client:
		yield client


@pytest.mark.asyncio
async def test_get_all_sensors_route(client, mock_get_all_sensors):
	mock_response = {'sensors': [sensor.to_dict() for sensor in [SensorFactory() for _ in range(10)]]}
	mock_get_all_sensors.return_value = mock_response

	response = client.get('/sensors/')  # Assuming the endpoint is '/sensors/'

	assert response.status_code == 200
	assert response.json() == mock_response
	mock_get_all_sensors.assert_called_once()


@pytest.mark.asyncio
async def test_get_sensor_by_id_route(client, mock_get_sensor_by_id):
	sensor_id = '67e52c913161b5df7189df14'
	# Mocking the response for 'get_sensor_by_id'
	mock_response = SensorFactory(id=sensor_id).to_dict()
	mock_get_sensor_by_id.return_value = mock_response

	response = client.get(
		f'/sensors/{sensor_id}'
	)  # Assuming the endpoint is '/sensors/{sensor_id}'

	assert response.status_code == 200
	assert response.json() == mock_response
	mock_get_sensor_by_id.assert_called_once_with(sensor_id)


@pytest.mark.asyncio
async def test_get_sensor_by_id_invalid_response(client, mock_get_sensor_by_id):
	sensor_id = 'non_existent_id'
	mock_get_sensor_by_id.side_effect = HTTPException(detail='Sensor not found', status_code=404)

	with pytest.raises(HTTPException) as exc:
		client.get(f'/sensors/{sensor_id}')
	assert exc.value.status_code == 404, f'Expected 404, got {exc.value.status_code}'
	assert exc.value.detail == 'Sensor not found', (
		f'Expected "Sensor not found", got {exc.value.detail}'
	)
