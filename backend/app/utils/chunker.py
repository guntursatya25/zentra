"""Chunker service — splits parsed document sections into chunks with overlap."""

from typing import Any


# Default configuration
DEFAULT_CHUNK_SIZE = 800      # characters
DEFAULT_OVERLAP = 100         # characters
MAX_CHUNK_SIZE = 2000
MAX_OVERLAP = 500


def chunk_sections(
    sections: list[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict[str, Any]]:
    """Split parsed sections into overlapping chunks.

    Preserves structural metadata (bab, pasal, ayat) on each chunk.
    Respects natural boundaries: never split mid-ayat unless forced by size.
    """
    if not sections:
        return []

    chunk_size = min(max(chunk_size, 200), MAX_CHUNK_SIZE)
    overlap = min(max(overlap, 0), MAX_OVERLAP)

    chunks: list[dict[str, Any]] = []
    buffer = ""
    current_meta: dict[str, Any] = {}
    chunk_index = 0

    for sec in sections:
        teks = (sec.get("teks") or "").strip()
        if not teks:
            continue

        meta = {
            "bab": sec.get("bab"),
            "bab_judul": sec.get("bab_judul"),
            "pasal": sec.get("pasal"),
            "pasal_judul": sec.get("pasal_judul"),
            "ayat": sec.get("ayat"),
            "halaman": sec.get("halaman"),
        }

        # If starting a new structural unit, flush buffer if non-empty
        if buffer and _structural_boundary(current_meta, meta):
            chunks.append(_make_chunk(buffer, current_meta, chunk_index))
            chunk_index += 1
            buffer = _get_overlap(buffer, overlap)

        current_meta = meta

        # If single section exceeds chunk_size, split it
        if len(teks) > chunk_size:
            if buffer:
                chunks.append(_make_chunk(buffer, current_meta, chunk_index))
                chunk_index += 1
                buffer = ""
            chunks.extend(_split_large_section(teks, current_meta, chunk_size, overlap, chunk_index))
            chunk_index = len(chunks)
            continue

        # If adding this exceeds chunk_size, flush first
        if buffer and len(buffer) + len(teks) + 1 > chunk_size:
            chunks.append(_make_chunk(buffer, current_meta, chunk_index))
            chunk_index += 1
            buffer = _get_overlap(buffer, overlap)

        if buffer:
            buffer += " " + teks
        else:
            buffer = teks

    # Flush remaining
    if buffer:
        chunks.append(_make_chunk(buffer, current_meta, chunk_index))

    return chunks


def _structural_boundary(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """True if the structural unit changed (bab or pasal differs)."""
    return (
        (a.get("bab") is not None and a.get("bab") != b.get("bab"))
        or (a.get("pasal") is not None and a.get("pasal") != b.get("pasal"))
        or (a.get("ayat") is not None and a.get("ayat") != b.get("ayat"))
    )


def _make_chunk(teks: str, meta: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "teks": teks.strip(),
        "bab": meta.get("bab"),
        "bab_judul": meta.get("bab_judul"),
        "pasal": meta.get("pasal"),
        "pasal_judul": meta.get("pasal_judul"),
        "ayat": meta.get("ayat"),
        "halaman": meta.get("halaman"),
        "chunk_index": index,
    }


def _get_overlap(text: str, overlap_chars: int) -> str:
    """Get trailing `overlap_chars` characters from text for the next chunk."""
    if overlap_chars <= 0 or len(text) <= overlap_chars:
        return ""
    # Try to break at a sentence boundary within the overlap region
    overlap_text = text[-overlap_chars:]
    # Find last sentence boundary in the overlap
    for sep in (". ", ".\n", "!\n", "?\n"):
        idx = overlap_text.rfind(sep)
        if idx > 0:
            return overlap_text[idx + 2:]
    return text[-(overlap_chars // 2):]  # fallback: half overlap


def _split_large_section(
    teks: str, meta: dict[str, Any], chunk_size: int, overlap: int, start_index: int
) -> list[dict[str, Any]]:
    """Split a single large section that exceeds chunk_size."""
    chunks = []
    pos = 0
    idx = start_index
    while pos < len(teks):
        end = min(pos + chunk_size, len(teks))
        # Try to break at sentence boundary
        if end < len(teks):
            segment = teks[pos:end + 100]
            for sep in (". ", ".\n", "!", "?"):
                last = segment.rfind(sep, 0, chunk_size)
                if last > chunk_size // 2:
                    end = pos + last + len(sep)
                    break
        chunk_text = teks[pos:end].strip()
        if chunk_text:
            chunks.append({
                "teks": chunk_text,
                "bab": meta.get("bab"),
                "bab_judul": meta.get("bab_judul"),
                "pasal": meta.get("pasal"),
                "pasal_judul": meta.get("pasal_judul"),
                "ayat": meta.get("ayat"),
                "halaman": meta.get("halaman"),
                "chunk_index": idx,
            })
            idx += 1
        pos = end - overlap if end < len(teks) else len(teks)
    return chunks


def chunk_text(
    teks: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict[str, Any]]:
    """Simple text chunker for non-structured content (fallback)."""
    chunk_size = min(max(chunk_size, 200), MAX_CHUNK_SIZE)
    overlap = min(max(overlap, 0), MAX_OVERLAP)

    chunks = []
    pos = 0
    idx = 0
    while pos < len(teks):
        end = min(pos + chunk_size, len(teks))
        chunk_text = teks[pos:end].strip()
        if chunk_text:
            chunks.append({
                "teks": chunk_text,
                "chunk_index": idx,
            })
            idx += 1
        pos = end - overlap if end < len(teks) else len(teks)
    return chunks
