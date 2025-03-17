import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/smk")

class SMKRequest(BaseModel):
    content: str

@router.get("/test")
async def smk_home():
    return {"message": "SMK API is working!"}

@router.get("/search-artwork")
async def search_artwork(keys: str):
    """
    Calls the external SMK API to search for artworks.
    
    
    Parameters:
        - `keys`: Search term (e.g., "minimumsbetragtning")
    """
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

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"SMK API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")