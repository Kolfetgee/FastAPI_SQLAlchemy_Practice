import pytest

from src.apps.project.repository import ProjectRepository
from src.apps.project.schemas import ProjectCreate, ProjectUpdate
from src.apps.user.models import User
from src.db.session import async_session


@pytest.mark.database
@pytest.mark.asyncio
async def test_project_repository_create_and_get_by_id():
    async with async_session() as session:
        user = User(
            username="owner",
            email="owner@example.com",
            password="hashed_password",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        repository = ProjectRepository(session=session)

        project_in = ProjectCreate(
            name="Test Project",
            description="Test description",
            person_in_charge_id=user.id,
        )

        created_project = await repository.create(project_in)

        found_project = await repository.get_by_id(created_project.id)

        assert found_project is not None
        assert found_project.id == created_project.id
        assert found_project.name == "Test Project"
        assert found_project.description == "Test description"
        assert found_project.person_in_charge_id == user.id

@pytest.mark.database
async def test_project_repository_update():
    async with async_session() as session:
        user = User(
            username="owner",
            email="owner@example.com",
            password="hashed_password",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        repository = ProjectRepository(session=session)

        project_in = ProjectCreate(
            name="Old Project",
            description="Old description",
            person_in_charge_id=user.id,
        )

        created_project = await repository.create(project_in)

        project_update = ProjectUpdate(
            name="Updated Project",
            description="Updated description",
        )

        updated_project = await repository.update(
            created_project.id,
            project_update,
        )

        assert updated_project is not None
        assert updated_project.id == created_project.id
        assert updated_project.name == "Updated Project"
        assert updated_project.description == "Updated description"


@pytest.mark.database
async def test_project_repository_delete():
    async with async_session() as session:
        user = User(
            username="owner",
            email="owner@example.com",
            password="hashed_password",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        repository = ProjectRepository(session=session)

        project_in = ProjectCreate(
            name="Project To Delete",
            description="Delete me",
            person_in_charge_id=user.id,
        )

        created_project = await repository.create(project_in)

        deleted_project = await repository.delete(created_project.id)
        found_project = await repository.get_by_id(created_project.id)

        assert deleted_project is not None
        assert deleted_project.id == created_project.id
        assert found_project is None