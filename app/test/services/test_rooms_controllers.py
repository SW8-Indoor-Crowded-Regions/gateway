import pytest
from fastapi import HTTPException
from app.services.rooms_controllers import get_all_rooms, get_room_by_id
from app.schemas.room_response_schema import RoomModel, RoomListModel
from app.test.factories.room_factory import RoomFactory


@pytest.fixture
def mock_forward_request(mocker):
	return mocker.patch('app.services.rooms_controllers.forward_request')


@pytest.fixture
def mock_env(monkeypatch):
	monkeypatch.setattr('app.services.rooms_controllers.SENSOR_SIM_PATH', 'http://mock-sensor-sim')
	monkeypatch.setattr(
		'app.services.rooms_controllers.PATHFINDING_PATH', 'http://mock-pathfinding'
	)


@pytest.mark.asyncio
async def test_get_all_rooms(mock_env, mock_forward_request):
	mock_response = {'rooms': [room.to_dict() for room in [RoomFactory() for _ in range(10)]]}
	mock_forward_request.return_value = (mock_response, 200)

	result = await get_all_rooms()

	assert RoomListModel.model_validate(result) == RoomListModel.model_validate(mock_response)
	mock_forward_request.assert_called_once_with('http://mock-sensor-sim/rooms', 'GET')


@pytest.mark.asyncio
async def test_get_all_rooms_invalid_response(mock_env, mock_forward_request):
	mock_forward_request.return_value = ({'details': 'Invalid response'}, 500)

	with pytest.raises(HTTPException) as exc:
		await get_all_rooms()

	assert exc.value.status_code == 500
	assert exc.value.detail == 'Invalid room data received from sensor simulation service'


@pytest.mark.asyncio
async def test_get_room_by_id(mock_env, mock_forward_request):
	room_id = '67e52c913161b5df7189df14'
	mock_room = RoomFactory(id=room_id).to_dict()
	mock_forward_request.return_value = (mock_room, 200)

	result = await get_room_by_id(room_id)

	assert RoomModel.model_validate(result)
	assert result == mock_room
	mock_forward_request.assert_called_once_with(f'http://mock-sensor-sim/rooms/{room_id}', 'GET')


@pytest.mark.asyncio
async def test_get_room_by_id_invalid_response(mock_env, mock_forward_request):
	mock_forward_request.return_value = ({'details': 'This is an error'}, 500)

	with pytest.raises(HTTPException) as exc:
		await get_room_by_id('1')

	assert exc.value.status_code == 500
	assert exc.value.detail == 'Invalid room data received from sensor simulation service'
