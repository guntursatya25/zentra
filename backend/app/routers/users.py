import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.middleware.auth import get_current_user, require_super_admin
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.audit import log_audit
from app.services.auth import hash_password, verify_password

router = APIRouter(prefix="/api/admin/users", tags=["admin"])


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    password: str
    role_id: int
    department: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_super_admin),
):
    result = await db.execute(select(User).options(selectinload(User.role)))
    users = result.scalars().all()
    return [
        UserOut(
            id=str(u.id),
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role_name=u.role.name,
            department=u.department,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login,
        )
        for u in users
    ]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    """GAP 1: Create a new user (super_admin only)."""
    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = User(
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role_id=body.role_id,
        department=body.department,
        is_active=True,
    )
    db.add(user)
    ip = request.client.host if request and request.client else None
    await log_audit(db, current_user.id, "create", "user", None, {"username": body.username}, ip)
    await db.commit()
    await db.refresh(user)

    # Eagerly load role for response
    await db.refresh(user, ["role"])
    return UserOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name,
        department=user.department,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    changes = {}
    if body.full_name is not None:
        user.full_name = body.full_name
        changes["full_name"] = body.full_name
    if body.role_id is not None:
        user.role_id = body.role_id
        changes["role_id"] = body.role_id
    if body.department is not None:
        user.department = body.department
        changes["department"] = body.department
    if body.is_active is not None:
        user.is_active = body.is_active
        changes["is_active"] = body.is_active

    ip = request.client.host if request and request.client else None
    await log_audit(db, current_user.id, "update", "user", str(user.id), {"changes": changes}, ip)
    await db.commit()
    await db.refresh(user)

    return UserOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name,
        department=user.department,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )
