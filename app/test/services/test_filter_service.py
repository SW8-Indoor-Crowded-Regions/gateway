import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from app.schemas.filter_schemas import FilterToRoomsRequest, FilterRequest
import requests

from app.services.filter_service import get_filters, get_facet_count, filter_to_rooms, get_rooms


@pytest.fixture
def mock_facets():
	return {
		'creator': ['John Doe', 10, 'Jane Smith', 5],
		'materials': ['Oil', 3, 'Canvas', 7],
	}


@pytest.fixture
def mocked_response(mock_facets):
	return {'facets': mock_facets}


def test_get_facet_count(mock_facets):
	result = get_facet_count(mock_facets)
	expected = [
		{
			'type': 'creator',
			'filters': [
				{'key': 'John Doe', 'count': 10},
				{'key': 'Jane Smith', 'count': 5},
			],
		},
		{
			'type': 'materials',
			'filters': [
				{'key': 'Oil', 'count': 3},
				{'key': 'Canvas', 'count': 7},
			],
		},
	]
	assert result == expected


def test_get_filters_success(monkeypatch, mocked_response):
	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 200
		mock_resp.json.return_value = mocked_response
		return mock_resp

	monkeypatch.setattr(requests, 'get', mock_get)

	result = get_filters()
	assert isinstance(result, list)
	assert 'creator' in result[0]['type']
	assert 'materials' in result[1]['type']
	assert len(result[0]['filters']) == 2
	assert len(result[1]['filters']) == 2


def test_get_filters_http_error(monkeypatch):
	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 404
		mock_resp.text = 'Not Found'
		return mock_resp

	monkeypatch.setattr(requests, 'get', mock_get)

	with pytest.raises(HTTPException) as exc_info:
		get_filters()
	assert exc_info.value.status_code == 404
	assert 'Failed to fetch data' in exc_info.value.detail


def test_get_filters_no_facets(monkeypatch):
	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 200
		mock_resp.json.return_value = {'facets': {}}
		return mock_resp

	monkeypatch.setattr(requests, 'get', mock_get)

	with pytest.raises(HTTPException) as exc_info:
		get_filters()
	assert exc_info.value.status_code == 500
	assert 'No filters found' in exc_info.value.detail


# ---------- Unit test for filter_to_rooms ----------


def test_filter_to_rooms_aggregates_rooms():
	request_data = FilterToRoomsRequest(
		filters=[
			FilterRequest(type='creator', keys=['John Doe', 'Jane Smith']),
			FilterRequest(type='materials', keys=['Oil']),
		]
	)

	mock_return = {
		('creator', 'John Doe'): ['Room 1'],
		('creator', 'Jane Smith'): ['Room 2'],
		('materials', 'Oil'): ['Room 3'],
	}

	def mock_get_rooms(filter_type, value):
		return mock_return[(filter_type, value)]

	with patch('app.services.filter_service.get_rooms', side_effect=mock_get_rooms):
		result = filter_to_rooms(request_data)
		assert sorted(result) == ['Room 1', 'Room 2', 'Room 3']


# ---------- Tests for get_rooms ----------


def test_get_rooms_success(monkeypatch):
	mock_response_data = {'facets': {'current_location_name': ['Room A', 5, 'Room B', 3]}}

	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 200
		mock_resp.json.return_value = mock_response_data
		return mock_resp

	monkeypatch.setattr('requests.get', mock_get)

	result = get_rooms('creator', 'John Doe')
	assert result == ['Room A', 'Room B']


def test_get_rooms_empty(monkeypatch):
	mock_response_data = {'facets': {'current_location_name': []}}

	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 200
		mock_resp.json.return_value = mock_response_data
		return mock_resp

	monkeypatch.setattr('requests.get', mock_get)

	result = get_rooms('creator', 'Nonexistent')
	assert result == []


def test_get_rooms_http_error(monkeypatch):
	def mock_get(*args, **kwargs):
		mock_resp = MagicMock()
		mock_resp.status_code = 500
		mock_resp.text = 'Internal Server Error'
		return mock_resp

	monkeypatch.setattr('requests.get', mock_get)

	with pytest.raises(HTTPException) as exc_info:
		get_rooms('creator', 'John Doe')
	assert exc_info.value.status_code == 500
	assert 'Failed to fetch data' in str(exc_info.value.detail)
