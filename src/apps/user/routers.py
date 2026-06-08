from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.user.repository import UserRepository
from src.apps.user.schemas import UserCreate, UserRead, UserUpdate
from src.apps.user.services import UserService
from src.db.session import get_db


user_router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(session=db)
    return UserService(repository=repository)


def raise_user_integrity_error(error: IntegrityError) -> None:
    error_message = str(error.orig).lower()

    if "duplicate key" in error_message or "unique constraint" in error_message:
        raise HTTPException(
            status_code=409,
            detail="User with this username or email already exists",
        ) from error

    raise HTTPException(
        status_code=400,
        detail="Database integrity error",
    ) from error


@user_router.get("/by-ids", response_model=list[UserRead])
async def get_users_by_ids(
    user_ids: list[int] = Query(...),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users_by_ids(user_ids)


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    found_user = await service.get_user(user_id)

    if found_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return found_user


@user_router.get("/", response_model=list[UserRead])
async def get_users(
    service: UserService = Depends(get_user_service),
):
    return await service.get_users()


@user_router.post("/", response_model=UserRead)
async def create_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service),
):
    try:
        created_user = await service.create_user(user_create)
    except IntegrityError as error:
        raise_user_integrity_error(error)

    if created_user is None:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    return created_user


@user_router.post("/many", response_model=list[UserRead])
async def create_many_users(
    users_in: list[UserCreate],
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.create_many_users(users_in)
    except IntegrityError as error:
        raise_user_integrity_error(error)


@user_router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    try:
        found_user = await service.update_user(user_id, user_update)
    except IntegrityError as error:
        raise_user_integrity_error(error)

    if found_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return found_user


@user_router.delete("/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    found_user = await service.delete_user(user_id)

    if found_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return found_user
