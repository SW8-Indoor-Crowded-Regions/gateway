import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/smk")

class SMKRequest(BaseModel):
    content: str

async def search_artwork(keys: str):
    """
    Calls the external SMK API to search for artworks.
    
    
    Parameters:
        - `keys`: Search term (e.g., "minimumsbetragtning")
    """
    if not keys.strip():
        raise HTTPException(status_code=400, detail="The 'keys' parameter must be a non-empty string.")
    
    params = {
        "keys": keys,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.smk.dk/api/v1/art/search", params=params)
            response.raise_for_status()
            data = response.json()
            print(data)
            filtered_data = data.get("autocomplete")
            return filtered_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def get_artwork(keys: str):
    """
    Calls the external SMK API to get an artworks.
    
    
    Parameters:
        - `keys`: Search term (e.g., "minimumsbetragtning")
    """
    if not keys.strip():
        raise HTTPException(status_code=400, detail="The 'keys' parameter must be a non-empty string.")
    
    params = {
        "keys": keys,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.smk.dk/api/v1/art/search", params=params)
            response.raise_for_status()
            data = response.json()
            filtered_data = [
                {
                    "id": data.get("items", [{}])[0].get("id"),
                    "room": data.get("items", [{}])[0].get("current_location_name"),
                }
            ]
            return filtered_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")