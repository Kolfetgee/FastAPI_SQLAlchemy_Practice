from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.project.models import Project
from src.apps.project.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: int) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        stmt = select(Project).order_by(Project.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, project_in: ProjectCreate) -> Project:
        project = Project(**project_in.model_dump())

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def update(
        self,
        project_id: int,
        project_update: ProjectUpdate,
    ) -> Project | None:
        project = await self.get_by_id(project_id)

        if project is None:
            return None

        update_data = project_update.model_dump(exclude_unset=True)

        for field_name, field_value in update_data.items():
            setattr(project, field_name, field_value)

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def delete(self, project_id: int) -> Project | None:
        project = await self.get_by_id(project_id)

        if project is None:
            return None

        await self.session.delete(project)
        await self.session.commit()

        return project
