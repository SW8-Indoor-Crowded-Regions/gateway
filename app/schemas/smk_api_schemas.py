from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import Query
from typing import List
from datetime import datetime




class FilterParams:
	def __init__(
		self,
		keys: Optional[str] = Query(
			default=None, title='Search term', description='Search term for the artwork.', example='minimumsbetragtning'
		),
		room: Optional[str] = Query(
			default=None, title='Room', description='Id of the room to filter artworks by.', example='67efbb210b23f5290bff702e'
		),
		limit: Optional[int] = Query(
			default=None, title='Limit', description='Number of artworks to return.', example=10
		),
		offset: Optional[int] = Query(
			default=None, title='Offset', description='Offset for pagination.', example=0
		),
	):
		self.keys = keys
		self.room = room
		self.limit = limit
		self.offset = offset

	def dict_exclude_none(self) -> dict:
		return {k: v for k, v in self.__dict__.items() if v is not None}

	def get(self, key: str, default=None) -> Any:
		return getattr(self, key, default) # pragma: no cover

	def json(self) -> dict:
		return self.dict_exclude_none()

	class Config:
		json_schema_extra = {
			'examples': [{'room': '67efbb210b23f5290bff702e', 'limit': 10, 'offset': 0, 'keys': 'minimumsbetragtning'}]
		}


class Dimension(BaseModel):
	notes: Optional[str] = None
	part: Optional[str] = None
	type: Optional[str] = None
	unit: Optional[str] = None
	value: Optional[str] = None


class ProductionDate(BaseModel):
	start: Optional[datetime] = None
	end: Optional[datetime] = None
	period: Optional[str] = None


class Title(BaseModel):
	title: Optional[str] = None
	type: Optional[str] = None
	language: Optional[str] = None


class Artwork(BaseModel):
	responsible_department: Optional[str] = None
	current_location_name: Optional[str] = None
	acquisition_date: Optional[datetime] = None
	dimensions: Optional[List[Dimension]] = []
	production_date: List[ProductionDate] = []
	techniques: List[str] = []
	titles: Optional[List[Title]] = []
	colors: Optional[List[str]] = []
	artist: List[str] = []


class ArtworkResponse(BaseModel):
	offset: int
	rows: int
	found: int
	items: List[Artwork]
	facets: Optional[Dict[str, Any]] = {}
	facets_ranges: Optional[Dict[str, Any]] = {}
 
	def __init__(self, **data):
		super().__init__(**data)
		self.offset = data.get('offset', 0)
		self.rows = data.get('rows', 0)
		self.found = data.get('found', 0)
		self.items = [Artwork(**item) for item in data.get('items', [])]
		self.facets = data.get('facets', {})
		self.facets_ranges = data.get('facets_ranges', {})


artwork_response_example: Dict[int | str, Dict[str, Any]] = {
	200: {
		'offset': 0,
		'rows': 1,
		'found': 1,
		'items': [
			{
				'responsible_department': 'Department of Paintings',
				'current_location_name': 'Room 101',
				'acquisition_date': '2023-01-01T00:00:00Z',
				'dimensions': [],
				'production_date': [],
				'techniques': ['Oil on canvas'],
				'titles': [],
				'colors': ['Red', 'Blue'],
				'artist': ['John Doe'],
			},
			{
				'responsible_department': 'Department of Sculptures',
				'current_location_name': 'Room 102',
				'acquisition_date': '2023-01-02T00:00:00Z',
				'dimensions': [],
				'production_date': [],
				'techniques': ['Marble'],
				'titles': [],
				'colors': ['White'],
				'artist': ['Jane Smith'],
			},
		],
		'facets': {},
		'facets_ranges': {},
		'autocomplete': [],
	},
	400: {
		'description': 'Bad Request - Invalid room id',
		'content': {'application/json': {'example': {'detail': 'Invalid room id'}}},
	},
}
