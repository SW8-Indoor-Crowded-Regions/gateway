#import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes.api_routes import router
import json

app = FastAPI()
app.include_router(router)
client = TestClient(app)

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

def test_get_artwork_valid():
    response = client.get("/get-artwork?keys=Minimumsbetragtning")
    assert response.status_code == 200
    assert {
        "id": "1170016772_object",
        "room": "Sal 263C"
    } in response.json()

def test_get_artwork_empty_string():
    response = client.get("/get-artwork?keys=")
    assert response.status_code == 400
    assert response.json()["detail"] == "The 'keys' parameter must be a non-empty string."

def test_get_artwork_no_keys():
    response = client.get("/get-artwork")
    assert response.status_code == 422

def test_get_artwork_invalid_json_response(monkeypatch):
    """Simulates an invalid JSON response from the SMK API"""

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                raise json.JSONDecodeError("Invalid JSON", "", 0)

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    response = client.get("/get-artwork?keys=query")

    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]