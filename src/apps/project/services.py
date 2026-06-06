from src.apps.project.models import Project
from src.apps.project.repository import ProjectRepository
from src.apps.project.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    async def get_project(self, project_id: int) -> Project | None:
        return await self.repository.get_by_id(project_id)

    async def get_projects(self) -> list[Project]:
        return await self.repository.get_all()

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
