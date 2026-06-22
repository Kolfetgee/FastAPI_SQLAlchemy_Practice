from fastapi import APIRouter

from src.apps.auth.routers import auth_router
from src.apps.project.routers import project_router
from src.apps.user.routers import user_router
from src.apps.external.routers import external_router

api_v1_router = APIRouter()
api_v1_router.include_router(user_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(project_router)
api_v1_router.include_router(external_router)