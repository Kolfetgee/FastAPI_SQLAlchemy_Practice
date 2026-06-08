from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.project.models import Project, ProjectStatus
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

    async def get_all(
        self,
        limit: int,
        offset: int,
        status: ProjectStatus | None = None,
        person_in_charge_id: int | None = None,
        sort_by: str = "id",
    ) -> tuple[list[Project], int]:
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
        WHERE
            (:status IS NULL OR status = :status)
            AND (:person_in_charge_id IS NULL OR person_in_charge_id = :person_in_charge_id)
        ORDER BY :sort_by
        LIMIT :limit
        OFFSET :offset;

        SELECT COUNT(*)
        FROM projects
        WHERE
            (:status IS NULL OR status = :status)
            AND (:person_in_charge_id IS NULL OR person_in_charge_id = :person_in_charge_id);
        """
        stmt = select(Project)
        count_stmt = select(func.count()).select_from(Project)

        if status is not None:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)

        if person_in_charge_id is not None:
            stmt = stmt.where(Project.person_in_charge_id == person_in_charge_id)
            count_stmt = count_stmt.where(Project.person_in_charge_id == person_in_charge_id)

        sort_columns = {
            "id": Project.id,
            "create_time": Project.create_time,
            "start_time": Project.start_time,
            "complete_time": Project.complete_time,
        }
        sort_column = sort_columns.get(sort_by, Project.id)

        stmt = stmt.order_by(sort_column).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        projects = list(result.scalars().all())

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        return projects, total_count

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

        try:
            self.session.add(project)
            await self.session.commit()
            await self.session.refresh(project)
        except Exception:
            await self.session.rollback()
            raise

        return project

    async def create_many(self, projects_in: list[ProjectCreate]) -> list[Project]:
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
        VALUES
            (:name, :description, :status, :start_time, :complete_time, :person_in_charge_id),
            ...
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
        projects = [Project(**project_in.model_dump()) for project_in in projects_in]

        try:
            self.session.add_all(projects)
            await self.session.commit()

            for project in projects:
                await self.session.refresh(project)
        except Exception:
            await self.session.rollback()
            raise

        return projects

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

        try:
            await self.session.commit()
            await self.session.refresh(project)
        except Exception:
            await self.session.rollback()
            raise

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

        try:
            await self.session.delete(project)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return project
