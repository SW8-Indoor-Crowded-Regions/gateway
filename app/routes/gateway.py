from fastapi import APIRouter, Request
from pydantic import BaseModel

# from app.utils.forwarder import forward_request


router = APIRouter()


# Backend services listed here
SERVICES = {
    "routing": "http://localhost:8001",
}


class MessageRequest(BaseModel):
    msg: str


@router.get("/test")
async def get_route_test():
    return {"message": "API is working!"}


@router.post("/test")
async def post_route_test(request: MessageRequest):
    return {"message": f"Received: {request.msg}"}
