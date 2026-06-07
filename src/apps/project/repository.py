from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.project.models import Project
from src.apps.project.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: int) -> Project | None:
        """
        SQL:
        SELECT
            id,
            name,
            description,
            status,
            create_time,
            start_time,
            complete_time,
            person_in_charge_id
        FROM projects
        WHERE id = :project_id;
        """
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        """
        SQL:
        SELECT
            id,
            name,
            description,
            status,
            create_time,
            start_time,
            complete_time,
            person_in_charge_id
        FROM projects
        ORDER BY id;
        """
        stmt = select(Project).order_by(Project.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, project_in: ProjectCreate) -> Project:
        """
        SQL:
        INSERT INTO projects (
            name,
            description,
            status,
            start_time,
            complete_time,
            person_in_charge_id
        )
        VALUES (
            :name,
            :description,
            :status,
            :start_time,
            :complete_time,
            :person_in_charge_id
        )
        RETURNING
            id,
            name,
            description,
            status,
            create_time,
            start_time,
            complete_time,
            person_in_charge_id;
        """
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
        """
        SQL:
        UPDATE projects
        SET
            name = :name,
            description = :description,
            status = :status,
            start_time = :start_time,
            complete_time = :complete_time,
            person_in_charge_id = :person_in_charge_id
        WHERE id = :project_id
        RETURNING
            id,
            name,
            description,
            status,
            create_time,
            start_time,
            complete_time,
            person_in_charge_id;

        Note:
        In Python code only fields provided in ProjectUpdate are applied.
        """
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
        """
        SQL:
        DELETE FROM projects
        WHERE id = :project_id
        RETURNING
            id,
            name,
            description,
            status,
            create_time,
            start_time,
            complete_time,
            person_in_charge_id;
        """
        project = await self.get_by_id(project_id)

        if project is None:
            return None

        await self.session.delete(project)
        await self.session.commit()

        return project
