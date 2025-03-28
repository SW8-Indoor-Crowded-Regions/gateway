from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.get("/test",
            summary="Test if the API is working",
				description="A simple test route to check if the API is working.",
				tags=["test"],
				response_description="A simple message to confirm the API is working.",
				response_model=BaseModel
    		)
async def get_route_test():
    return {"message": "API is working!"}

@router.post("/test")
async def post_route_test(request: BaseModel):
    return {"message": "Received test data."}