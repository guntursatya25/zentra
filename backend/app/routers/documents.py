import uuid
from datetime import datetime, timezone
from pathlib import Path as FilePath

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.document import Document, DocumentCategory, DocumentChunk
from app.models.user import User
from app.schemas.document import (
    ChunkOutWithDoc,
    ChunkUpdate,
    DocumentListOut,
    DocumentOut,
    DocumentCategoryOut,
)
from app.services.audit import log_audit
from app.services.document import (
    check_category_access,
    list_documents,
    mark_previous_versions_inactive,
    store_file,
    validate_file,
)
from app.services.ingestion import process_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentListOut])
async def get_documents(
    category_id: int | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    docs = await list_documents(db, user, category_id, status, search)
    result = []
    for d in docs:
        cat_name = d.category.name if d.category else None
        result.append(
            DocumentListOut(
                id=str(d.id),
                title=d.title,
                category_id=d.category_id,
                category_name=cat_name,
                file_type=d.file_type,
                version=d.version,
                status=d.status,
                created_at=d.created_at,
            )
        )
    return result


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentOut(
        id=str(doc.id),
        title=doc.title,
        description=doc.description,
        category_id=doc.category_id,
        file_type=doc.file_type,
        file_size=doc.file_size,
        version=doc.version,
        status=doc.status,
        is_latest_version=doc.is_latest_version,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


async def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    category_id: int | None = Form(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    await validate_file(file)
    await check_category_access(db, user, category_id)

    # Determine version: if same title + category exists, bump version
    version = 1
    existing = await db.execute(
        select(Document).where(
            Document.title == title,
            Document.category_id == category_id,
            Document.is_latest_version == True,
        )
    )
    latest = existing.scalar_one_or_none()
    if latest:
        version = latest.version + 1

    file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "bin"
    doc_id = uuid.uuid4()
    file_path = await store_file(file, category_id, doc_id, version)

    doc = Document(
        id=doc_id,
        title=title,
        description=description,
        category_id=category_id,
        file_path=file_path,
        file_type=file_type,
        file_size=file.size,
        version=version,
        status="draft",
        uploaded_by=user.id,
        is_latest_version=True,
    )
    db.add(doc)

    # Mark older versions inactive
    if version > 1:
        await mark_previous_versions_inactive(db, title, user)

    await db.commit()
    await db.refresh(doc)

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "upload", "document", str(doc.id), {"title": doc.title, "version": doc.version}, ip)

    return DocumentOut(
        id=str(doc.id),
        title=doc.title,
        description=doc.description,
        category_id=doc.category_id,
        file_type=doc.file_type,
        file_size=doc.file_size,
        version=doc.version,
        status=doc.status,
        is_latest_version=doc.is_latest_version,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.put("/{doc_id}", response_model=DocumentOut)
async def update_document_metadata(
    doc_id: uuid.UUID,
    title: str | None = Form(None),
    description: str | None = Form(None),
    category_id: int | None = Form(None),
    status: str | None = Form(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Permission: super admin or data_manager of this category
    if user.role.name != "super_admin":
        if user.role.name != "data_manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        from app.models.user import CategoryManager

        check = await db.execute(
            select(CategoryManager).where(
                CategoryManager.user_id == user.id,
                CategoryManager.category_id == (category_id or doc.category_id),
            )
        )
        if check.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your category")

    if title is not None:
        doc.title = title
    if description is not None:
        doc.description = description
    if category_id is not None:
        if category_id == -1:
            doc.category_id = None
        else:
            doc.category_id = category_id
    if status is not None:
        if status not in ("draft", "active", "inactive", "archived"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        doc.status = status

    doc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(doc)

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "update", "document", str(doc.id), {"status": doc.status}, ip)

    return DocumentOut(
        id=str(doc.id),
        title=doc.title,
        description=doc.description,
        category_id=doc.category_id,
        file_type=doc.file_type,
        file_size=doc.file_size,
        version=doc.version,
        status=doc.status,
        is_latest_version=doc.is_latest_version,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if user.role.name != "super_admin":
        if user.role.name != "data_manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        from app.models.user import CategoryManager

        check = await db.execute(
            select(CategoryManager).where(
                CategoryManager.user_id == user.id,
                CategoryManager.category_id == doc.category_id,
            )
        )
        if check.scalar_one_or_none() is None:
            raise HTTPException(  # noqa: SIM115 — error message differs from above
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your category"
            )

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "delete", "document", str(doc.id), {"title": doc.title}, ip)

    # GAP 10: Remove file from disk
    import os
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass  # non-fatal

    await db.delete(doc)
    await db.commit()


@router.get("/{doc_id}/file")
async def download_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    path = FilePath(doc.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    media_type = "application/pdf" if doc.file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path, media_type=media_type, filename=f"{doc.title}.{doc.file_type}")


@router.get("/{doc_id}/versions", response_model=list[DocumentOut])
async def get_document_versions(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    # Get the base document to find its title-group
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    versions = await db.execute(
        select(Document).where(
            Document.title == doc.title,
            Document.category_id == doc.category_id,
        ).order_by(Document.version.desc())
    )
    return [
        DocumentOut(
            id=str(v.id), title=v.title, description=v.description,
            category_id=v.category_id, file_type=v.file_type,
            file_size=v.file_size, version=v.version, status=v.status,
            is_latest_version=v.is_latest_version,
            created_at=v.created_at, updated_at=v.updated_at,
        )
        for v in versions.scalars().all()
    ]


@router.post("/{doc_id}/versions", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_new_version(
    doc_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    """Upload a new version of an existing document."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    old_doc = result.scalar_one_or_none()
    if not old_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if user.role.name != "super_admin":
        if user.role.name != "data_manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        from app.models.user import CategoryManager

        check = await db.execute(
            select(CategoryManager).where(
                CategoryManager.user_id == user.id,
                CategoryManager.category_id == old_doc.category_id,
            )
        )
        if check.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your category")

    await validate_file(file)
    file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "bin"
    new_version = old_doc.version + 1
    new_id = uuid.uuid4()
    file_path = await store_file(file, old_doc.category_id, new_id, new_version)

    new_doc = Document(
        id=new_id,
        title=old_doc.title,
        description=old_doc.description,
        category_id=old_doc.category_id,
        file_path=file_path,
        file_type=file_type,
        file_size=file.size,
        version=new_version,
        status="draft",
        uploaded_by=user.id,
        is_latest_version=True,
    )
    db.add(new_doc)

    old_doc.is_latest_version = False
    old_doc.status = "archived"
    old_doc.updated_at = datetime.now(timezone.utc)

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "upload_version", "document", str(new_doc.id), {"title": old_doc.title, "version": new_version}, ip)
    await db.commit()
    await db.refresh(new_doc)

    return DocumentOut(
        id=str(new_doc.id),
        title=new_doc.title,
        description=new_doc.description,
        category_id=new_doc.category_id,
        file_type=new_doc.file_type,
        file_size=new_doc.file_size,
        version=new_doc.version,
        status=new_doc.status,
        is_latest_version=new_doc.is_latest_version,
        created_at=new_doc.created_at,
        updated_at=new_doc.updated_at,
    )


# ── Chunk endpoints (Sprint 2 — Document Parsing) ──


@router.get("/{doc_id}/chunks", response_model=list[ChunkOutWithDoc])
async def get_document_chunks(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """List all chunks for a document with editable metadata."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks_result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == doc_id)
        .order_by(DocumentChunk.chunk_index)
    )

    # If no chunks yet, process the document first
    chunks = list(chunks_result.scalars().all())
    if not chunks:
        try:
            count = await process_document(doc_id, db)
            if count > 0:
                chunks_result = await db.execute(
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == doc_id)
                    .order_by(DocumentChunk.chunk_index)
                )
                chunks = list(chunks_result.scalars().all())
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {exc}",
            )

    return [
        ChunkOutWithDoc(
            id=str(c.id),
            bab=c.bab,
            bab_judul=c.bab_judul,
            pasal=c.pasal,
            pasal_judul=c.pasal_judul,
            ayat=c.ayat,
            teks=c.teks,
            halaman=c.halaman,
            chunk_index=c.chunk_index,
            document_title=doc.title,
        )
        for c in chunks
    ]


@router.put("/chunks/{chunk_id}", response_model=ChunkOutWithDoc)
async def update_chunk_metadata(
    chunk_id: uuid.UUID,
    body: ChunkUpdate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    """Edit chunk metadata (Bab/Pasal/Ayat correction)."""
    result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.id == chunk_id)
    )
    chunk = result.scalar_one_or_none()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")

    # Get document for permission check
    doc_result = await db.execute(
        select(Document).where(Document.id == chunk.document_id)
    )
    doc = doc_result.scalar_one_or_none()

    if user.role.name != "super_admin":
        if user.role.name != "data_manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        from app.models.user import CategoryManager

        check = await db.execute(
            select(CategoryManager).where(
                CategoryManager.user_id == user.id,
                CategoryManager.category_id == doc.category_id,
            )
        )
        if check.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your category")

    if body.bab is not None:
        chunk.bab = body.bab
    if body.bab_judul is not None:
        chunk.bab_judul = body.bab_judul
    if body.pasal is not None:
        chunk.pasal = body.pasal
    if body.pasal_judul is not None:
        chunk.pasal_judul = body.pasal_judul
    if body.ayat is not None:
        chunk.ayat = body.ayat

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "update_chunk", "chunk", str(chunk.id), {"document_id": str(chunk.document_id)}, ip)
    await db.commit()
    await db.refresh(chunk)

    return ChunkOutWithDoc(
        id=str(chunk.id),
        bab=chunk.bab,
        bab_judul=chunk.bab_judul,
        pasal=chunk.pasal,
        pasal_judul=chunk.pasal_judul,
        ayat=chunk.ayat,
        teks=chunk.teks,
        halaman=chunk.halaman,
        chunk_index=chunk.chunk_index,
        document_title=doc.title if doc else None,
    )


@router.post("/{doc_id}/reparse")
async def reparse_document(
    doc_id: uuid.UUID,
    use_ai: bool = Query(False, description="Use AI-assisted parsing for better accuracy"),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    """Re-parse and re-chunk a document (regenerates all chunks + embeddings).

    Args:
        use_ai: If true, use LLM to parse structure (more accurate but slower, requires LLM_API_URL)
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if user.role.name != "super_admin":
        if user.role.name != "data_manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        from app.models.user import CategoryManager

        check = await db.execute(
            select(CategoryManager).where(
                CategoryManager.user_id == user.id,
                CategoryManager.category_id == doc.category_id,
            )
        )
        if check.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your category")

    try:
        count = await process_document(doc_id, db, use_ai=use_ai)
        ip = request.client.host if request and request.client else None
        await log_audit(db, user.id, "reparse", "document", str(doc.id), {"title": doc.title, "chunks_created": count, "use_ai": use_ai}, ip)
        await db.commit()
        return {"message": f"Reparsed successfully", "chunks_created": count, "ai_used": use_ai}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reparse failed: {exc}",
        )
