"""Ingestion pipeline: parse → chunk → embed → save to DB."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, DocumentChunk
from app.services.embedding import generate_embedding
from app.utils.ai_parser import parse_with_ai
from app.utils.chunker import chunk_sections
from app.utils.docx_parser import DOCXParser
from app.utils.pdf_parser import PDFParser


async def process_document(
    doc_id: uuid.UUID,
    db: AsyncSession,
    use_ai: bool = False,
) -> int:
    """Run full ingestion pipeline for a document.

    Args:
        doc_id: Document UUID
        db: Database session
        use_ai: If True, use LLM to parse structure (more accurate but slower)

    Returns number of chunks created.
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise ValueError(f"Document {doc_id} not found")

    # 1. Delete existing chunks
    existing = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == doc_id)
    )
    for chunk in existing.scalars().all():
        await db.delete(chunk)
    await db.commit()

    # 2. Parse — choose method
    sections = []
    if use_ai and settings.llm_api_url:
        # AI-assisted parsing: read raw text, send to LLM
        raw_text = _read_raw_text(doc.file_path, doc.file_type)
        if raw_text:
            print(f"[ingestion] Using AI parsing for {doc.title}")
            sections = await parse_with_ai(raw_text)
            if sections:
                print(f"[ingestion] AI parser returned {len(sections)} sections")
            else:
                print("[ingestion] AI parser failed, falling back to regex")

    # Fallback to regex if AI not requested or failed
    if not sections:
        sections = _parse_file(doc.file_path, doc.file_type)

    if not sections:
        sections = [{"teks": _read_raw_text(doc.file_path, doc.file_type)}]

    # 3. Chunk
    chunks = chunk_sections(sections)
    if not chunks:
        return 0

    # 4. Save chunks + generate embeddings
    for i, ch in enumerate(chunks):
        embedding = await generate_embedding(ch["teks"])

        db_chunk = DocumentChunk(
            document_id=doc.id,
            bab=ch.get("bab"),
            bab_judul=ch.get("bab_judul"),
            pasal=ch.get("pasal"),
            pasal_judul=ch.get("pasal_judul"),
            ayat=ch.get("ayat"),
            teks=ch["teks"],
            halaman=ch.get("halaman"),
            chunk_index=ch.get("chunk_index", i),
            embedding=embedding,
        )
        db.add(db_chunk)

    await db.commit()
    return len(chunks)


def _parse_file(file_path: str, file_type: str) -> list[dict]:
    """Route to the correct parser based on file type."""
    if file_type == "pdf":
        parser = PDFParser(file_path)
        return parser.extract_sections()
    elif file_type == "docx":
        parser = DOCXParser(file_path)
        return parser.extract_sections()
    return []


def _read_raw_text(file_path: str, file_type: str) -> str:
    """Fallback: extract whatever text we can without structure parsing."""
    try:
        if file_type == "pdf":
            import fitz
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text("text") for page in doc)
            doc.close()
            return text
        elif file_type == "docx":
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception:
        return ""
