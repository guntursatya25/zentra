import uuid
from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.user import User
from app.services.auth import decode_access_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_role(required_role: str) -> Callable[[User], User]:
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name != required_role and current_user.role.name != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {required_role}",
            )
        return current_user

    return role_checker


def require_super_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.name != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires super_admin role",
        )
    return user


async def require_data_manager(
    category_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> User:
    if user.role.name == "super_admin":
        return user

    if user.role.name != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    from app.models.user import CategoryManager

    result = await db.execute(
        select(CategoryManager).where(
            CategoryManager.user_id == user.id,
            CategoryManager.category_id == category_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a manager of this category",
        )
    return user
