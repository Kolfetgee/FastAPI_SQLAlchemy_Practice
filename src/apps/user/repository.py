from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.schemas import AuthUserData
from src.apps.project.models import Project  # noqa: F401
from src.apps.user.models import User
from src.apps.user.schemas import UserCreate, UserRead, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> UserRead | None:
        """
        SQL:
        SELECT id, username, email, password
        FROM users
        WHERE id = :user_id;
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserRead(id=user.id, username=user.username, email=user.email)

    async def get_auth_user_by_email(self, email: str) -> AuthUserData | None:
        """
        SQL:
        SELECT id, username, email, password
        FROM users
        WHERE email = :email;
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return AuthUserData(
            id=user.id,
            username=user.username,
            email=user.email,
            password=user.password,
        )

    async def get_all(self) -> list[UserRead]:
        """
        SQL:
        SELECT id, username, email, password
        FROM users
        ORDER BY id;
        """
        stmt = select(User).order_by(User.id)
        result = await self.session.execute(stmt)
        users = result.scalars().all()

        return [
            UserRead(id=user.id, username=user.username, email=user.email)
            for user in users
        ]

    async def create(self, user_in: UserCreate) -> UserRead:
        """
        SQL:
        INSERT INTO users (username, email, password)
        VALUES (:username, :email, :password)
        RETURNING id, username, email;
        """
        user = User(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
        )

        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return UserRead(id=user.id, username=user.username, email=user.email)

    async def update(self, user_id: int, user_update: UserUpdate) -> UserRead | None:
        """
        SQL:
        UPDATE users
        SET username = :username,
            email = :email,
            password = :password
        WHERE id = :user_id
        RETURNING id, username, email;
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        for field_name, field_value in update_data.items():
            setattr(user, field_name, field_value)

        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return UserRead(id=user.id, username=user.username, email=user.email)

    async def delete(self, user_id: int) -> UserRead | None:
        """
        SQL:
        DELETE FROM users
        WHERE id = :user_id
        RETURNING id, username, email;
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        deleted_user = UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
        )

        try:
            await self.session.delete(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return deleted_user

    async def get_by_ids(self, user_ids: list[int]) -> list[UserRead]:
        """
        SQL:
        SELECT id, username, email, password
        FROM users
        WHERE id IN (:user_ids)
        ORDER BY id;
        """
        stmt = select(User).where(User.id.in_(user_ids)).order_by(User.id)
        result = await self.session.execute(stmt)
        users = result.scalars().all()

        return [
            UserRead(id=user.id, username=user.username, email=user.email)
            for user in users
        ]

    async def create_many(self, users_in: list[UserCreate]) -> list[UserRead]:
        """
        SQL:
        INSERT INTO users (username, email, password)
        VALUES
            (:username, :email, :password),
            ...
        RETURNING id, username, email;
        """
        users = [
            User(
                username=user_in.username,
                email=user_in.email,
                password=user_in.password,
            )
            for user_in in users_in
        ]

        try:
            self.session.add_all(users)
            await self.session.commit()

            for user in users:
                await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return [
            UserRead(id=user.id, username=user.username, email=user.email)
            for user in users
        ]

    async def get_by_email(self, user_email: str) -> UserRead | None:
        """
        SQL:
        SELECT id, username, email, password
        FROM users
        WHERE email = :user_email;
        """
        stmt = select(User).where(User.email == user_email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserRead(id=user.id, username=user.username, email=user.email)
