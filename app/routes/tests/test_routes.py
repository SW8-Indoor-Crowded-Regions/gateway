from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get(
	'/',
	summary='Test if the API is working',
	description='A simple test route to check if the API is working.',
	tags=['test'],
	response_description='A simple message to confirm the API is working.',
	response_model=dict[str, str],
)
async def get_route_test():
	return {'message': 'API is working!'}


@router.post('/')
async def post_route_test(request: BaseModel):
	return {'message': 'Received test data.'}
