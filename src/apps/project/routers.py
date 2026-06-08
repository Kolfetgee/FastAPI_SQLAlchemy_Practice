from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.project.models import ProjectStatus
from src.apps.project.repository import ProjectRepository
from src.apps.project.schemas import (
    ProjectCreate,
    ProjectListResponse,
    ProjectRead,
    ProjectUpdate,
)
from src.apps.project.services import ProjectService
from src.db.session import get_db


project_router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    repository = ProjectRepository(session=db)
    return ProjectService(repository=repository)


def raise_integrity_error(error: IntegrityError) -> None:
    error_message = str(error.orig).lower()

    if "duplicate key" in error_message or "unique constraint" in error_message:
        raise HTTPException(
            status_code=409,
            detail="Project with this name already exists",
        ) from error

    if "foreign key" in error_message or "violates foreign key constraint" in error_message:
        raise HTTPException(
            status_code=400,
            detail="Person in charge not found",
        ) from error

    raise HTTPException(
        status_code=400,
        detail="Database integrity error",
    ) from error


@project_router.get("/", response_model=ProjectListResponse)
async def get_projects(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: ProjectStatus | None = None,
    person_in_charge_id: int | None = Query(default=None, ge=1),
    sort_by: str = Query(default="id"),
    service: ProjectService = Depends(get_project_service),
):
    allowed_sort_fields = {"id", "create_time", "start_time", "complete_time"}

    if sort_by not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")

    projects, total_count = await service.get_projects(
        limit=limit,
        offset=offset,
        status=status,
        person_in_charge_id=person_in_charge_id,
        sort_by=sort_by,
    )

    return ProjectListResponse(
        items=projects,
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_prev=offset > 0,
        has_next=offset + limit < total_count,
    )


@project_router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@project_router.post("/", response_model=ProjectRead)
async def create_project(
    project_in: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    try:
        return await service.create_project(project_in)
    except IntegrityError as error:
        raise_integrity_error(error)


@project_router.post("/many", response_model=list[ProjectRead])
async def create_many_projects(
    projects_in: list[ProjectCreate],
    service: ProjectService = Depends(get_project_service),
):
    try:
        return await service.create_many_projects(projects_in)
    except IntegrityError as error:
        raise_integrity_error(error)


@project_router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    try:
        project = await service.update_project(project_id, project_update)
    except IntegrityError as error:
        raise_integrity_error(error)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@project_router.delete("/{project_id}", response_model=ProjectRead)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    project = await service.delete_project(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
