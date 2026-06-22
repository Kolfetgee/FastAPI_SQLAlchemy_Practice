import pytest
from unittest.mock import AsyncMock

from src.apps.project.services import ProjectService
from src.apps.project.schemas import ProjectCreate, ProjectUpdate


@pytest.mark.services
async def test_project_service_get_project():
    repository = AsyncMock()
    service = ProjectService(repository=repository)

    fake_project = object()
    repository.get_by_id.return_value = fake_project

    result = await service.get_project(1)

    assert result is fake_project
    repository.get_by_id.assert_awaited_once_with(1)


@pytest.mark.services
async def test_project_service_get_projects():
    repository = AsyncMock()
    service = ProjectService(repository=repository)

    fake_project = object()
    repository.get_all.return_value = ([fake_project], 1)

    projects, total_count = await service.get_projects(
        limit=10,
        offset=0,
    )

    assert projects == [fake_project]
    assert total_count == 1
    repository.get_all.assert_awaited_once_with(
        limit=10,
        offset=0,
        status=None,
        person_in_charge_id=None,
        sort_by="id",
    )


@pytest.mark.services
async def test_project_service_create_project():
    repository = AsyncMock()
    service = ProjectService(repository=repository)

    fake_project = object()
    repository.create.return_value = fake_project

    project_in = ProjectCreate(
        name="Service Project",
        description="Service description",
        person_in_charge_id=1,
    )

    result = await service.create_project(project_in)

    assert result is fake_project
    repository.create.assert_awaited_once_with(project_in)


@pytest.mark.services
async def test_project_service_update_project():
    repository = AsyncMock()
    service = ProjectService(repository=repository)

    fake_project = object()
    repository.update.return_value = fake_project

    project_update = ProjectUpdate(
        name="Updated Service Project",
    )

    result = await service.update_project(1, project_update)

    assert result is fake_project
    repository.update.assert_awaited_once_with(1, project_update)


@pytest.mark.services
async def test_project_service_delete_project():
    repository = AsyncMock()
    service = ProjectService(repository=repository)

    fake_project = object()
    repository.delete.return_value = fake_project

    result = await service.delete_project(1)

    assert result is fake_project
    repository.delete.assert_awaited_once_with(1)