import os
import uuid
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.document import Document, DocumentCategory
from app.models.user import CategoryManager, User

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


async def check_category_access(
    db: AsyncSession, user: User, category_id: int | None
) -> None:
    """Super admin can do anything; data_manager must own the category."""
    if user.role.name == "super_admin":
        return
    if user.role.name != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if category_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data managers must assign a category",
        )
    result = await db.execute(
        select(CategoryManager).where(
            CategoryManager.user_id == user.id,
            CategoryManager.category_id == category_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a manager of this category",
        )


async def validate_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    # MINOR 5: Check size by reading file (UploadFile.seek doesn't support whence)
    # Read in chunks to avoid loading entire file at once
    size = 0
    while chunk := await file.read(8192):
        size += len(chunk)
        if size > MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max {settings.max_upload_size_mb}MB",
            )
    await file.seek(0)


async def store_file(file: UploadFile, category_id: int | None, doc_id: uuid.UUID, version: int) -> str:
    """Store uploaded file to disk. Runs sync I/O in thread pool to avoid blocking."""
    import asyncio

    ext = Path(file.filename or "").suffix.lower()
    cat_dir = str(category_id) if category_id else "uncategorized"
    rel_dir = Path(settings.upload_dir) / cat_dir / str(doc_id) / f"v{version}"
    abs_dir = Path(settings.upload_dir) / cat_dir / str(doc_id) / f"v{version}"

    def _write():
        abs_dir.mkdir(parents=True, exist_ok=True)
        dest = abs_dir / f"document{ext}"
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return str(rel_dir / f"document{ext}")

    return await asyncio.to_thread(_write)


async def mark_previous_versions_inactive(
    db: AsyncSession, title: str, uploader: User
) -> None:
    """Mark all active documents with the same title from same category scope as inactive."""
    result = await db.execute(
        select(Document).where(
            Document.title == title,
            Document.is_latest_version == True,
            Document.status.in_(["active", "draft"]),
        )
    )
    for doc in result.scalars().all():
        doc.is_latest_version = False
        doc.status = "inactive"
    # No commit here — caller controls the transaction


async def list_documents(
    db: AsyncSession,
    user: User,
    category_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
) -> list[Document]:
    query = select(Document).options(selectinload(Document.category))

    # Super admin sees all; data_manager sees only their categories
    if user.role.name == "super_admin":
        pass
    elif user.role.name == "data_manager":
        subq = select(CategoryManager.category_id).where(
            CategoryManager.user_id == user.id
        )
        query = query.where(Document.category_id.in_(subq))
    else:
        # Employee — only active documents
        query = query.where(Document.status == "active")

    if category_id is not None:
        query = query.where(Document.category_id == category_id)
    if status is not None:
        query = query.where(Document.status == status)
    if search:
        query = query.where(Document.title.ilike(f"%{search}%"))

    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
