import pytest

from src.apps.user.repository import UserRepository
from src.apps.user.schemas import UserCreate, UserUpdate
from src.db.session import async_session


@pytest.mark.database
async def test_user_repository_create_and_get_by_id():
    async with async_session() as session:
        repository = UserRepository(session=session)

        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            password="hashed_password",
        )

        created_user = await repository.create(user_in)
        found_user = await repository.get_by_id(created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "alice"
        assert found_user.email == "alice@example.com"


@pytest.mark.database
async def test_user_repository_update():
    async with async_session() as session:
        repository = UserRepository(session=session)

        user_in = UserCreate(
            username="bob",
            email="bob@example.com",
            password="hashed_password",
        )
        created_user = await repository.create(user_in)

        user_update = UserUpdate(
            email="newbob@example.com",
        )

        updated_user = await repository.update(created_user.id, user_update)

        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.username == "bob"
        assert updated_user.email == "newbob@example.com"


@pytest.mark.database
async def test_user_repository_delete():
    async with async_session() as session:
        repository = UserRepository(session=session)

        user_in = UserCreate(
            username="charlie",
            email="charlie@example.com",
            password="hashed_password",
        )
        created_user = await repository.create(user_in)

        deleted_user = await repository.delete(created_user.id)
        found_user = await repository.get_by_id(created_user.id)

        assert deleted_user is not None
        assert deleted_user.id == created_user.id
        assert deleted_user.username == "charlie"
        assert found_user is None


@pytest.mark.database
async def test_user_repository_get_by_email_and_auth_user():
    async with async_session() as session:
        repository = UserRepository(session=session)

        user_in = UserCreate(
            username="diana",
            email="diana@example.com",
            password="hashed_password",
        )
        await repository.create(user_in)

        found_user = await repository.get_by_email("diana@example.com")
        auth_user = await repository.get_auth_user_by_email("diana@example.com")

        assert found_user is not None
        assert found_user.username == "diana"
        assert found_user.email == "diana@example.com"

        assert auth_user is not None
        assert auth_user.username == "diana"
        assert auth_user.email == "diana@example.com"
        assert auth_user.password == "hashed_password"