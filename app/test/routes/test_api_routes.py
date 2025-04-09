import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
import json
import pytest

# Import the router from the new structure.
from app.routes.api_routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_health_check():
	response = client.get('/health')
	assert response.status_code == 200
	assert response.json() == {'status': 'ok'}
 
 
def test_search_artwork_valid():
    response = client.get("/search-artwork?keys=minimumsbetragtning")
    assert response.status_code == 200
    assert "Minimumsbetragtning" in response.json()

def test_search_artwork_empty_string():
    response = client.get("/search-artwork?keys=")
    assert response.status_code == 400
    assert response.json()["detail"] == "The 'keys' parameter must be a non-empty string."

def test_search_artwork_no_keys():
    response = client.get("/search-artwork")
    assert response.status_code == 422

def test_search_artwork_invalid_json_response(monkeypatch):
    """Simulates an invalid JSON response from the SMK API"""

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                raise json.JSONDecodeError("Invalid JSON", "", 0)

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    response = client.get("/search-artwork?keys=query")

    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]
    
    
def test_search_artwork_api_failure(monkeypatch):
	"""Simulates a failure from the SMK API"""

	async def mock_get(*args, **kwargs):
		class MockResponse:
			def raise_for_status(self):
					raise Exception("API failure")
			def json(self):
					return {}

		return MockResponse()

	monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

	response = client.get("/search-artwork?keys=query")

	assert response.status_code == 500
	assert "Internal server error" in response.json()["detail"]


@pytest.fixture
def mock_api_response():
		return {
			"autocomplete": [
			],
			"found": 2,
			"rows": 10,
			"offset": 0,
			"items": [
				{
					"current_location_name": "Room 1",
					"dimensions": [],
					"artist": ["Artist Name"],
					"acquisition_date": "2023-01-01",
					"responsible_department": "Department Name",
					"titles": [{
						"title": "Title 1",
						"language": "da",
        			}],
					"production_date": [{
        				"date": datetime.datetime(2023, 1, 1)
            	}],
					"colors": ["Red", "Blue"],
					"techniques": ["Oil", "Acrylic"]
				},
				{
					"current_location_name": "Room 2",
					"dimensions": [],
					"artist": ["Another Artist"],
					"acquisition_date": "2023-02-01",
					"responsible_department": "Another Department",
					"titles": [{
						"title": "Title 2",
						"language": "en",
		  			}],
					"production_date": [{
						"date": datetime.datetime(2023, 2, 1)
					}],
					"colors": ["Green"],
					"techniques": ["Watercolor"]
				}
			]
		}, 200


@pytest.fixture
def mock_room():
		return {"name": "Room 1"}, 200


@pytest.fixture
def mock_room_invalid():
		return {"detail": {
			'body': None,
			'error': 'Invalid room id.',
			'method': 'GET',
			'url': 'http://localhost:8002/rooms/invalid_room_id',
			'params': None,
     }}, 400


@pytest.fixture
def mock_room_not_found():
		return {"detail": {
			'body': None,
			'error': 'Room not found.',
			'method': 'GET',
			'url': 'http://localhost:8002/rooms/invalid_room_id',
			'params': None,
     }}, 404


@pytest.mark.asyncio
async def test_artwork_query(mocker, mock_api_response, mock_room):
	payload = {
		"keys": "Test title",
		"room": "67efbb200b23f5290bff700f"
	}

	mocker.patch("app.services.smk_api.forward_request", side_effect=[mock_room, mock_api_response])
 
	response = client.get("/artwork", params=payload)
	assert response.status_code == 200
	assert isinstance(response.json(), dict)
 
	assert "items" in response.json()
	assert len(response.json()["items"]) == 2
 
@pytest.mark.asyncio
async def test_artwork_query_no_room(mocker, mock_api_response, mock_room):
	payload = {
		"keys": "Test title",
	}
 
	mocker.patch("app.services.smk_api.forward_request", side_effect=[mock_api_response])
 
	response = client.get("/artwork", params=payload)
	assert response.status_code == 200
	assert isinstance(response.json(), dict)
 
	assert "items" in response.json()
	assert len(response.json()["items"]) == 2
 
 
@pytest.mark.asyncio
async def test_artwork_query_invalid_room(mocker, mock_room_invalid):
	payload = {
		"keys": "Test title",
		"room": "invalid_room_id"
	}
 
	mocker.patch("app.services.smk_api.forward_request", side_effect=[mock_room_invalid])
 
	response = client.get("/artwork", params=payload)
	assert response.status_code == 400
	assert response.json()["detail"] == {
		'body': None,
		'error': 'Invalid room id.',
		'method': 'GET',
		'url': 'http://localhost:8002/rooms/invalid_room_id',
		'params': None,
	}

@pytest.mark.asyncio
async def test_artwork_query_room_not_found(mocker, mock_room_not_found):
	payload = {
		"keys": "Test title",
		"room": "dddddd200b23f5290bff7d0f"
	}
 
	mocker.patch("app.services.smk_api.forward_request", side_effect=[mock_room_not_found])
 
	response = client.get("/artwork", params=payload)
	assert response.status_code == 404
	assert response.json()["detail"] == {
		'body': None,
		'error': 'Room not found.',
		'method': 'GET',
		'url': 'http://localhost:8002/rooms/invalid_room_id',
		'params': None,
	}