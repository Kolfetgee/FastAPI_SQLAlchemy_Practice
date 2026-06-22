import httpx


JSONPLACEHOLDER_POSTS_URL = "https://jsonplaceholder.typicode.com/posts"


class ExternalPostsService:
    async def get_posts(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(JSONPLACEHOLDER_POSTS_URL)
            response.raise_for_status()
            return response.json()