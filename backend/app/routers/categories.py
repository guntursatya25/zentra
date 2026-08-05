import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user, require_super_admin
from app.models.user import CategoryManager, User
from app.models.document import DocumentCategory
from app.schemas.document import DocumentCategoryCreate, DocumentCategoryOut
from app.services.audit import log_audit

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[DocumentCategoryOut])
async def list_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(DocumentCategory))
    return result.scalars().all()


@router.post("", response_model=DocumentCategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: DocumentCategoryCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    cat = DocumentCategory(name=body.name, description=body.description)
    db.add(cat)
    await log_audit(db, user.id, "create", "category", None, {"name": cat.name}, _ip(request))
    await db.commit()
    await db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=DocumentCategoryOut)
async def update_category(
    category_id: int,
    body: DocumentCategoryCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(
        select(DocumentCategory).where(DocumentCategory.id == category_id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    cat.name = body.name
    cat.description = body.description
    await log_audit(db, user.id, "update", "category", str(cat.id), {"name": cat.name}, _ip(request))
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(
        select(DocumentCategory).where(DocumentCategory.id == category_id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await log_audit(db, user.id, "delete", "category", str(cat.id), {"name": cat.name}, _ip(request))
    await db.delete(cat)
    await db.commit()


@router.post("/{category_id}/managers")
async def assign_manager(
    category_id: int,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    # Validate target user exists (GAP 4)
    target = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    if target.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await db.execute(
        select(CategoryManager).where(
            CategoryManager.category_id == category_id,
            CategoryManager.user_id == uuid.UUID(user_id),
        )
    )
    if result.scalar_one_or_none():
        return {"message": "Already a manager"}

    cm = CategoryManager(category_id=category_id, user_id=uuid.UUID(user_id))
    db.add(cm)
    await log_audit(db, user.id, "assign_manager", "category", str(category_id), {"manager_user_id": user_id}, _ip(request))
    await db.commit()
    return {"message": "Manager assigned"}


@router.delete("/{category_id}/managers/{user_id}")
async def remove_manager(
    category_id: int,
    user_id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(require_super_admin),
    request: Request = None,  # type: ignore[assignment]
):
    # GAP 5: Check if assignment exists first
    result = await db.execute(
        select(CategoryManager).where(
            CategoryManager.category_id == category_id,
            CategoryManager.user_id == uuid.UUID(user_id),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager assignment not found")

    await log_audit(db, user.id, "remove_manager", "category", str(category_id), {"manager_user_id": user_id}, _ip(request))
    await db.execute(
        delete(CategoryManager).where(
            CategoryManager.category_id == category_id,
            CategoryManager.user_id == uuid.UUID(user_id),
        )
    )
    await db.commit()
    return {"message": "Manager removed"}


def _ip(request: Request | None) -> str | None:
    return request.client.host if request and request.client else None
