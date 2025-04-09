import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app.utils.forwarder import forward_request
import math
from app.schemas.smk_api_schemas import FilterParams, ArtworkResponse

router = APIRouter(prefix='/smk')


class SMKRequest(BaseModel):
	content: str


async def search_artwork(keys: str):
	"""
	Calls the external SMK API to search for artworks.


	Parameters:
	    - `keys`: Search term (e.g., "minimumsbetragtning")
	"""
	if not keys.strip():
		raise HTTPException(
			status_code=400, detail="The 'keys' parameter must be a non-empty string."
		)

	params = {
		'keys': keys,
	}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get('https://api.smk.dk/api/v1/art/search', params=params)
			response.raise_for_status()
			data = response.json()
			filtered_data = data.get('autocomplete')
			return filtered_data

	except Exception as e:
		raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


async def query_artwork(query_obj: FilterParams=Depends()) -> ArtworkResponse:
	load_dotenv()
	SENSOR_SIM_PATH = os.getenv('SENSOR_SIM', 'http://localhost:8002')
	if SENSOR_SIM_PATH is None:
		raise RuntimeError('SENSOR_SIM not found in environment variables')  # pragma: no cover
	query = query_obj.json()
	room = None
	if query.get('room') is not None:
		room, status = await forward_request(SENSOR_SIM_PATH + '/rooms/' + query.get('room', ''), 'GET')
		if not status == 200 or not room:
			raise HTTPException(status_code=status, detail=room['detail'])

 
	fields = 'current_location_name,dimensions,artist,acquisition_date,responsible_department,titles,production_date,colors,techniques'
 
	artworks, _ = await forward_request(
		'https://api.smk.dk/api/v1/art/search',
		'GET',
		params={
			'keys': query.get('keys') if query.get('keys') else '*',
			'filters': f'[current_location_name:sal {room.get("name", "")}]' if room else None,
			'rows': min(query.get('limit', math.inf), 2000) if query.get('limit') else None,
			'offset': query.get('offset', None) if query.get('offset') else None,
			'fields': fields,
		}
	)

	return artworks