from fastapi import HTTPException
import requests
from app.schemas.filter_schemas import FilterToRoomsRequest, Filter

filter_types = [
	'creator',
	'materials',
]

def get_filters() -> list[dict]:
	"""Fetch all artworks from the SMK API."""
	base_url = 'https://api.smk.dk/api/v1/art/search'
	page_size = 10

	response = requests.get(
		base_url,
		params={
			'keys': '*',
			'offset': 0,
			'rows': page_size,
			'filters': '[on_display:true]',
			'facets': filter_types,
		},
	)
	if response.status_code != 200:
		raise HTTPException(
			status_code=response.status_code,
			detail=f'Failed to fetch data: {response.text}'
		)
	data = response.json()
	filters = data.get('facets', [])
	if not filters:
		raise HTTPException(
			status_code=500,
			detail='No filters found in the response.'
		)
  
	result = get_facet_count(filters)
	return result

  
	
  
def get_facet_count(facets: dict) -> list[dict]:
	"""Get the creators of the artworks and their counts."""
	result = []
	for facet, items in facets.items():
		obj = {
			'type': facet,
			'filters': []
		}
		for i in range(0, len(items), 2):
			name = items[i]
			count = items[i + 1]
			obj['filters'].append({'key': name, 'count': count})
		result.append(obj)

	return result

def filter_to_rooms(request: FilterToRoomsRequest) -> list[str]:
	"""Return the rooms needed to find all artworks based on the filters."""
	rooms = []
	for type in request.filters:
		for filter in type.keys:
			rooms.extend(get_rooms(type.type, filter))
	return rooms


def get_rooms(filter_name: str, value: str) -> list[str]:
	"""Get the rooms based on the filter name and value."""
	result = requests.get(
		'https://api.smk.dk/api/v1/art/search',
		params={
			'keys': '*',
			'offset': 0,
			'rows': 10,
			'filters': f'[on_display:true]',
			'filters': f'[{filter_name}:{value}]',
			'facets': ['current_location_name'],
		},
	)
 
	if result.status_code != 200:
		raise HTTPException(
			status_code=result.status_code,
			detail=f'Failed to fetch data: {result.text}'
		)
  
	data = result.json()
 
	rooms = data.get('facets', {}).get('current_location_name', [])
	if not rooms:
		return []
	rooms = [rooms[i] for i in range(0, len(rooms), 2)]

	
	return rooms