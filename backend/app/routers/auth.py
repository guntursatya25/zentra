from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.audit import log_audit
from app.services.auth import authenticate_user, create_access_token, hash_password, update_last_login, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    await update_last_login(db, user)
    token = create_access_token(str(user.id), user.role.name)

    await log_audit(
        db,
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=str(user.id),
        details={"username": user.username},
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.name,
            department=user.department,
            is_active=user.is_active,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name,
        department=current_user.department,
        is_active=current_user.is_active,
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    body: PasswordChange,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    """GAP 2: Allow any authenticated user to change their own password."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(body.new_password)
    ip = request.client.host if request and request.client else None
    await log_audit(db, current_user.id, "change_password", "user", str(current_user.id), None, ip)
    await db.commit()
    return {"message": "Password changed successfully"}
