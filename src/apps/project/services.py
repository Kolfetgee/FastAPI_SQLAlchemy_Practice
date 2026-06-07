from src.apps.project.models import Project, ProjectStatus
from src.apps.project.repository import ProjectRepository
from src.apps.project.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    async def get_project(self, project_id: int) -> Project | None:
        return await self.repository.get_by_id(project_id)

    async def get_projects(
        self,
        limit: int,
        offset: int,
        status: ProjectStatus | None = None,
        person_in_charge_id: int | None = None,
        sort_by: str = "id",
    ) -> tuple[list[Project], int]:
        return await self.repository.get_all(
            limit=limit,
            offset=offset,
            status=status,
            person_in_charge_id=person_in_charge_id,
            sort_by=sort_by,
        )

    async def create_project(self, project_in: ProjectCreate) -> Project:
        return await self.repository.create(project_in)

    async def update_project(
        self,
        project_id: int,
        project_update: ProjectUpdate,
    ) -> Project | None:
        return await self.repository.update(project_id, project_update)

    async def delete_project(self, project_id: int) -> Project | None:
        return await self.repository.delete(project_id)
