from fastapi import status, FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.routes.filter_routes import router


app = FastAPI()
app.include_router(router)
client = TestClient(app, root_path='/filters')


def test_get_filters_route_success():
	mock_filters = [
		{
			'type': 'creator',
			'filters': [{'key': 'John Doe', 'count': 10}, {'key': 'Jane Smith', 'count': 5}],
		},
		{
			'type': 'materials',
			'filters': [{'key': 'Oil', 'count': 3}, {'key': 'Canvas', 'count': 7}],
		},
	]

	with patch('app.routes.filter_routes.fetch_filters', return_value=mock_filters):
		response = client.get('/filters')
		assert response.status_code == status.HTTP_200_OK
		assert isinstance(response.json(), list)
		assert response.json()[0]['type'] == 'creator'


def test_get_filters_route_error():
	with patch(
		'app.routes.filter_routes.fetch_filters', side_effect=HTTPException(status_code=500, detail='Internal Server Error')
	):
		response = client.get('/filters')
		assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

def test_post_rooms_success():
    request_data = {
        "filters": [
            {"type": "creator", "keys": ["John Doe", "Jane Smith"]},
            {"type": "materials", "keys": ["Oil"]}
        ]
    }

    mock_response = ["Room 1", "Room 2", "Room 3"]

    with patch("app.routes.filter_routes.filter_to_rooms", return_value=mock_response):
        response = client.post("/rooms", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_response


def test_post_rooms_error():
    request_data = {
        "filters": [
            {"type": "creator", "keys": ["Unknown"]}
        ]
    }

    with patch(
        "app.routes.filter_routes.filter_to_rooms",
        side_effect=HTTPException(status_code=500, detail="Service error")
    ):
        response = client.post("/rooms", json=request_data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Service error"