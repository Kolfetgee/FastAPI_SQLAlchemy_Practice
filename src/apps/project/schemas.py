from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.apps.project.models import ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.NEW
    person_in_charge_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    create_time: datetime
    start_time: datetime | None = None
    complete_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    status: ProjectStatus | None = None
    start_time: datetime | None = None
    complete_time: datetime | None = None
    person_in_charge_id: int | None = None
