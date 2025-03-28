from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes.tests.test_routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_get_route_test():
	response = client.get('/')
	print(response.__str__())
	print(response._content.decode())
	assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
	assert response.json() == {'message': 'API is working!'}, f"Expected message 'API is working!', got {response.json()}"


def test_post_route_test():
	response = client.post('/', json={})
	assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
	assert response.json() == {'message': 'Received test data.'}, f"Expected message 'Received test data.', got {response.json()}"