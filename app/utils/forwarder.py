import httpx


async def forward_request(
    target_url: str, method: str, params: dict = None, body: dict = None
):
    async with httpx.AsyncClient() as client:
        response = await client.request(method, target_url, params=params, json=body)
        return response.json()
