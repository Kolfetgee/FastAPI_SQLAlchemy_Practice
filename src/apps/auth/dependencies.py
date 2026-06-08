from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.schemas import AuthUserData
from src.apps.auth.utils import decode_token
from src.apps.user.repository import UserRepository
from src.apps.user.services import UserService
from src.db.session import get_db


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthUserData:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    repository = UserRepository(session=db)
    user_service = UserService(repository=repository)

    auth_user = await user_service.get_auth_user_by_email(email)
    if auth_user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return auth_user
