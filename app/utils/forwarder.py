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
  
		try:
			response_data = response.json()
		except Exception: # pragma: no cover
			response_data = response.text # pragma: no cover
		if response.status_code != 200:
			if response_data and 'detail' in response_data:
				if isinstance(response_data, str):
					error_message = response_data # pragma: no cover
				else:
					error_message = response_data.get('detail', 'Unknown error')
				raise HTTPException(
					status_code=response.status_code,
					detail={
        				'error': error_message,
						'body': body if len(body.__str__()) < 1000 else 'Body too large to display',
						'method': method,
						'url': target_url if len(target_url) < 1000 else 'URL too large to display',
						'params': params if len(params.__str__()) < 1000 else 'Params too large to display',
            	},
				)
			raise HTTPException(
				status_code=response.status_code,
				detail=response_data,
			)
		return response.json(), response.status_code
