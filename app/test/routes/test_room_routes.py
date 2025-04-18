import pytest
from fastapi.testclient import TestClient
from app.routes.api_routes import router
from fastapi import HTTPException
from app.test.factories.room_factory import RoomFactory


@pytest.fixture
def mock_get_all_rooms(mocker):
	return mocker.patch('app.routes.room_routes.get_all_rooms')


@pytest.fixture
def mock_get_room_by_id(mocker):
	return mocker.patch('app.routes.room_routes.get_room_by_id')


@pytest.fixture
def client():
	with TestClient(router) as client:
		yield client


@pytest.mark.asyncio
async def test_get_all_rooms_route(client, mock_get_all_rooms):
	mock_response = {'rooms': [room.to_dict() for room in [RoomFactory() for _ in range(10)]]}
	mock_get_all_rooms.return_value = mock_response

	response = client.get('/rooms/')

	assert response.status_code == 200
	assert response.json() == mock_response
	mock_get_all_rooms.assert_called_once()


@pytest.mark.asyncio
async def test_get_room_by_id_route(client, mock_get_room_by_id):
	room_id = '67e52c913161b5df7189df14'
	# Mocking the response for 'get_room_by_id'
	mock_response = RoomFactory(id=room_id).to_dict()
	mock_get_room_by_id.return_value = mock_response

	response = client.get(f'/rooms/{room_id}')  # Assuming the endpoint is '/rooms/{room_id}'

	assert response.status_code == 200
	assert response.json() == mock_response
	mock_get_room_by_id.assert_called_once_with(room_id)


@pytest.mark.asyncio
async def test_get_room_by_id_invalid_response(client, mock_get_room_by_id):
	room_id = 'non_existent_id'
	mock_get_room_by_id.side_effect = HTTPException(detail='Room not found', status_code=404)

	with pytest.raises(HTTPException) as exc:
		client.get(f'/rooms/{room_id}')
		assert exc.value.status_code == 404, f'Expected 404, got {exc.value.status_code}'
		assert exc.value.detail == 'Room not found', (
			f'Expected "Room not found", got {exc.value.detail}'
		)
