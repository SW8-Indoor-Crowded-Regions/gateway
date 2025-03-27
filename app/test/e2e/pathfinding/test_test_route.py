import requests
import time

BASE_URL = 'http://gateway:8000'  # Your gateway service


def wait_for_service(url, timeout=60):
	"""Wait for the service to be available before sending requests."""
	start_time = time.time()
	while time.time() - start_time < timeout:
		try:
			response = requests.get(url)
			if response.status_code == 200:
				print('Gateway is up!')
				return True
		except requests.ConnectionError:
			pass
		time.sleep(2)
	raise TimeoutError(f'Service {url} did not become available in time.')


def test_post_req():
	"""E2E test to fetch a path from the gateway."""
	# Ensure the service is running before testing
	wait_for_service(f'{BASE_URL}/test', timeout=5)  # Adjust if needed

	# Define the test payload (example points)
	payload = {'msg': 'Hello, world!'}

	# Send the request
	response = requests.post(f'{BASE_URL}/test', json=payload)

	# Assertions
	assert response.status_code == 200, f'Unexpected status code: {response.status_code}'
	data = response.json()
	assert data['message'] == f'Received: {payload["msg"]}', f'Unexpected response: {data["message"]}'
