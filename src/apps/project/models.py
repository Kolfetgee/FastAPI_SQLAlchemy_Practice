from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.user.models import User
from src.db.base import Base


class ProjectStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(
            ProjectStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="project_status",
        ),
        default=ProjectStatus.NEW,
        nullable=False,
    )

    create_time: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    start_time: Mapped[datetime | None] = mapped_column(nullable=True)
    complete_time: Mapped[datetime | None] = mapped_column(nullable=True)

    person_in_charge_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    person_in_charge: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
    )
