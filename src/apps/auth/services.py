from src.apps.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.apps.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.apps.user.schemas import UserCreate, UserRead
from src.apps.user.services import UserService


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def register_user(self, register_data: RegisterRequest) -> UserRead | None:
        existing_user = await self.user_service.get_auth_user_by_email(register_data.email)

        if existing_user is not None:
            return None

        user_create = UserCreate(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password,
        )

        return await self.user_service.create_user(user_create)

    async def login_user(self, login_data: LoginRequest) -> TokenResponse | None:
        auth_user = await self.user_service.get_auth_user_by_email(login_data.email)

        if auth_user is None:
            return None

        if auth_user.password != login_data.password:
            return None

        access_token = create_access_token({"sub": auth_user.email})
        refresh_token = create_refresh_token({"sub": auth_user.email})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse | None:
        payload = decode_token(refresh_token)

        if payload is None:
            return None

        if payload.get("type") != "refresh":
            return None

        email = payload.get("sub")
        if email is None:
            return None

        auth_user = await self.user_service.get_auth_user_by_email(email)
        if auth_user is None:
            return None

        new_access_token = create_access_token({"sub": auth_user.email})
        new_refresh_token = create_refresh_token({"sub": auth_user.email})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
