from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.project.repository import ProjectRepository
from src.apps.project.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from src.apps.project.services import ProjectService
from src.db.session import get_db


project_router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    repository = ProjectRepository(session=db)
    return ProjectService(repository=repository)


@project_router.get("/", response_model=list[ProjectRead])
async def get_projects(
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_projects()


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
    return await service.create_project(project_in)


@project_router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    project = await service.update_project(project_id, project_update)

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
