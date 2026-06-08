from src.apps.auth.schemas import AuthUserData
from src.apps.user.repository import UserRepository
from src.apps.user.schemas import UserCreate, UserRead, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user(self, user_id: int) -> UserRead | None:
        return await self.repository.get_by_id(user_id)

    async def get_users(self) -> list[UserRead]:
        return await self.repository.get_all()

    async def get_users_by_ids(self, user_ids: list[int]) -> list[UserRead]:
        return await self.repository.get_by_ids(user_ids)

    async def get_auth_user_by_email(self, email: str) -> AuthUserData | None:
        return await self.repository.get_auth_user_by_email(email)

    async def create_user(self, user_create: UserCreate) -> UserRead | None:
        existing_user = await self.repository.get_by_email(user_create.email)

        if existing_user is not None:
            return None

        return await self.repository.create(user_create)

    async def create_many_users(self, users_in: list[UserCreate]) -> list[UserRead]:
        return await self.repository.create_many(users_in)

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
    ) -> UserRead | None:
        return await self.repository.update(user_id, user_update)

    async def delete_user(self, user_id: int) -> UserRead | None:
        return await self.repository.delete(user_id)
