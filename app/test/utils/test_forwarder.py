import pytest
import httpx
from fastapi import HTTPException
from app.utils.forwarder import forward_request

# A fake response object that simulates httpx.Response.json()
class FakeResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.status_code = 200

    def json(self):
        return self._json

# A fake AsyncClient for successful requests.
class FakeAsyncClient:
	async def request(self, method, target_url, params=None, json=None):
		# Simulate a response that echoes back the parameters
		return FakeResponse({
			"method": method,
			"url": target_url,
			"params": params,
			"body": json
		})

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		pass

# A fake AsyncClient that simulates an error in the request.
class FakeAsyncClientError:
	def __init__(self):
		self.detail = ""
		self.status_code = 400
	async def request(self, method, target_url, params=None, json=None):
		raise httpx.HTTPError("Simulated request error")

	def json(self):
		if hasattr(self, "detail"):
			return {"detail": self.detail}
		else:
			return {}

	def text(self):
		return "Simulated error text"

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		pass

@pytest.mark.asyncio
async def test_forward_request_success(monkeypatch):
    # Override httpx.AsyncClient with our fake success client.
    monkeypatch.setattr(httpx, "AsyncClient", lambda: FakeAsyncClient())
    
    result, status = await forward_request(
        "http://example.com", "GET", params={"a": 1}, body={"key": "value"}
    )
    assert result == {
        "method": "GET",
        "url": "http://example.com",
        "params": {"a": 1},
        "body": {"key": "value"}
    }
    assert status == 200

@pytest.mark.asyncio
async def test_forward_request_error(monkeypatch):
    # Override httpx.AsyncClient with our fake error client.
    monkeypatch.setattr(httpx, "AsyncClient", lambda: FakeAsyncClientError())
    
    with pytest.raises(httpx.HTTPError, match="Simulated request error"):
        await forward_request("http://example.com", "POST")


@pytest.mark.asyncio
async def test_forward_request_error_detail(mocker):
	response = FakeAsyncClientError()
	response.detail = "Simulated error detail"
	response.status_code = 400
	mocker.patch(
	"httpx.AsyncClient.request",
		return_value=response,
	)

	with pytest.raises(HTTPException) as exc_info:
		await forward_request("http://example.com", "GET")

	assert exc_info.value.detail == {
			"error": "Simulated error detail",
			"body": None,
			"method": "GET",
			"url": "http://example.com",
			"params": None,
	}
 
@pytest.mark.asyncio
async def test_forward_request_error_no_detail(mocker):
	response = FakeAsyncClientError()
	del response.detail
	response.status_code = 400
	mocker.patch(
	"httpx.AsyncClient.request",
		return_value=response,
	)

	with pytest.raises(HTTPException) as exc_info:
		await forward_request("http://example.com", "GET")

	assert exc_info.value.detail == {}