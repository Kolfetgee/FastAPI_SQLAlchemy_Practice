from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.dependencies import get_current_user
from src.apps.auth.schemas import (
    AuthUserData,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from src.apps.auth.services import AuthService
from src.apps.user.repository import UserRepository
from src.apps.user.schemas import UserRead
from src.apps.user.services import UserService
from src.db.session import get_db


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    repository = UserRepository(session=db)
    user_service = UserService(repository=repository)
    return AuthService(user_service=user_service)


def raise_auth_integrity_error(error: IntegrityError) -> None:
    error_message = str(error.orig).lower()

    if "duplicate key" in error_message or "unique constraint" in error_message:
        raise HTTPException(
            status_code=409,
            detail="User with this username or email already exists",
        ) from error

    raise HTTPException(
        status_code=400,
        detail="Database integrity error",
    ) from error


@auth_router.post("/register", response_model=UserRead)
async def register_user(
    register_data: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        created_user = await service.register_user(register_data)
    except IntegrityError as error:
        raise_auth_integrity_error(error)

    if created_user is None:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    return created_user


@auth_router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    user_login = await service.login_user(login_data)

    if user_login is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return user_login


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    refreshed_tokens = await service.refresh_access_token(refresh_data.refresh_token)

    if refreshed_tokens is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return refreshed_tokens


@auth_router.get("/me-dep", response_model=UserRead)
async def get_me_dep(current_user: AuthUserData = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
    )


@auth_router.get("/me-middleware", response_model=UserRead)
async def get_me_middleware(request: Request):
    auth_user = getattr(request.state, "auth_user", None)

    if auth_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return UserRead(
        id=auth_user.id,
        username=auth_user.username,
        email=auth_user.email,
    )
