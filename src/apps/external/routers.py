from fastapi import APIRouter

from src.apps.external.services import ExternalPostsService


external_router = APIRouter(prefix="/external", tags=["External"])


@external_router.get("/posts")
async def get_external_posts():
    service = ExternalPostsService()
    return await service.get_posts()