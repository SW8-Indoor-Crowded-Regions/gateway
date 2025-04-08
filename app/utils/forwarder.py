import httpx
from typing import Any
from fastapi import HTTPException


async def forward_request(
	target_url: str, method: str, params: dict | None = None, body: dict | None = None
) -> tuple[Any, int]:
	"""
	Forward a request to a specified URL using the given HTTP method.
	Args:
		target_url (str): The URL to forward the request to.
		method (str): The HTTP method to use (e.g., 'GET', 'POST').
		params (dict, optional): Query parameters to include in the request.
		body (dict, optional): JSON body to include in the request.
	Returns:
		tuple[dict, int]: A tuple containing the response data and status code.
	"""
	async with httpx.AsyncClient() as client:
		response = await client.request(method, target_url, params=params, json=body)
		if response.status_code != 200:
			if response.json() and 'detail' in response.json():
				raise HTTPException(
					status_code=response.status_code,
					detail={
        				'error': response.json()['detail'],
						'body': body,
						'method': method,
						'url': target_url,
						'params': params,
            	},
				)
			raise HTTPException(
				status_code=response.status_code,
				detail=response.json(),
			)
		return response.json(), response.status_code
