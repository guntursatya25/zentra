"""Vector search service — semantic search over document chunks via pgvector."""

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, DocumentChunk
from app.services.embedding import generate_embedding

# MINOR 7: Use single embedding service from services/embedding.py


async def search_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 8,
    category_ids: list[int] | None = None,
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    """Search document chunks by semantic similarity to query."""
    embedding = await generate_embedding(query)

    if embedding is not None:
        return await _vector_search(db, embedding, top_k, category_ids, min_score)
    else:
        return await _keyword_search(db, query, top_k, category_ids)


async def _vector_search(
    db: AsyncSession,
    embedding: list[float],
    top_k: int,
    category_ids: list[int] | None,
    min_score: float,
) -> list[dict[str, Any]]:
    """Perform cosine similarity search via pgvector."""
    embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

    conditions = ["d.status = 'active'"]
    params: dict[str, Any] = {}

    if category_ids:
        param_name = "cat_ids"
        conditions.append(f"d.category_id = ANY(:{param_name})")
        params[param_name] = category_ids

    where_clause = " AND ".join(conditions)

    # FIX: Use CAST() instead of ::vector — asyncpg can't parse :param::type syntax
    sql = text(f"""
        SELECT
            ch.id,
            ch.teks,
            ch.bab,
            ch.bab_judul,
            ch.pasal,
            ch.pasal_judul,
            ch.ayat,
            ch.halaman,
            ch.chunk_index,
            d.id as document_id,
            d.title as document_title,
            d.version as document_version,
            1 - (ch.embedding <=> CAST(:embedding AS vector)) AS score
        FROM document_chunks ch
        JOIN documents d ON d.id = ch.document_id
        WHERE ch.embedding IS NOT NULL
          AND {where_clause}
          AND 1 - (ch.embedding <=> CAST(:embedding AS vector)) > :min_score
        ORDER BY score DESC
        LIMIT :top_k
    """)

    result = await db.execute(
        sql,
        {
            "embedding": embedding_str,
            "top_k": top_k,
            "min_score": min_score,
            **params,
        },
    )

    rows = result.fetchall()
    return [_row_to_chunk(r) for r in rows]


async def _keyword_search(
    db: AsyncSession,
    query: str,
    top_k: int,
    category_ids: list[int] | None,
) -> list[dict[str, Any]]:
    """Fallback keyword search using ILIKE when embedding is unavailable."""
    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.teks,
            DocumentChunk.bab,
            DocumentChunk.bab_judul,
            DocumentChunk.pasal,
            DocumentChunk.pasal_judul,
            DocumentChunk.ayat,
            DocumentChunk.halaman,
            DocumentChunk.chunk_index,
            Document.id,
            Document.title,
            Document.version,
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.status == "active")
        .where(DocumentChunk.teks.ilike(f"%{query}%"))
        .order_by(DocumentChunk.chunk_index)
        .limit(top_k)
    )

    if category_ids:
        stmt = stmt.where(Document.category_id.in_(category_ids))

    result = await db.execute(stmt)
    rows = result.fetchall()

    return [
        {
            "id": str(r[0]),
            "teks": r[1],
            "bab": r[2],
            "bab_judul": r[3],
            "pasal": r[4],
            "pasal_judul": r[5],
            "ayat": r[6],
            "halaman": r[7],
            "chunk_index": r[8],
            "document_id": str(r[9]),
            "document_title": r[10],
            "document_version": r[11],
            "score": 0.0,
        }
        for r in rows
    ]


def _row_to_chunk(row: Any) -> dict[str, Any]:
    """Convert a raw DB row to a chunk dict."""
    return {
        "id": str(row[0]),
        "teks": row[1],
        "bab": row[2],
        "bab_judul": row[3],
        "pasal": row[4],
        "pasal_judul": row[5],
        "ayat": row[6],
        "halaman": row[7],
        "chunk_index": row[8],
        "document_id": str(row[9]),
        "document_title": row[10],
        "document_version": row[11],
        "score": float(row[12]) if len(row) > 12 else 0.0,
    }
