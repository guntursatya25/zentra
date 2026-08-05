"""RAG orchestration — builds prompt, calls LLM, parses citations."""

import json
import re
from typing import Any

import httpx

from app.config import settings

SYSTEM_PROMPT = """Anda adalah asisten internal perusahaan yang membantu karyawan memahami kebijakan dan SOP perusahaan.

ATURAN:
1. Jawab ONLY berdasarkan dokumen yang diberikan di bawah ini.
2. Jika informasi tidak ditemukan di dokumen, katakan: "Tidak ditemukan referensi yang relevan dalam dokumen yang tersedia."
3. JANGAN mengarang jawaban atau menggunakan pengetahuan di luar dokumen.
4. Setiap jawaban WAJIB menyertakan sumber dengan format:
   📄 Nama Dokumen — BAB {X}, Pasal {Y}, Ayat (Z)
5. Jika menggunakan lebih dari satu sumber, sebutkan semua sumber secara terpisah.
6. Kutip teks asli yang relevan untuk mendukung jawaban Anda.
7. Gunakan bahasa Indonesia yang baik dan benar."""


async def answer_query(query: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate answer from query + retrieved chunks using real LLM API."""
    if not chunks:
        return {
            "answer": "Tidak ditemukan referensi yang relevan dalam dokumen yang tersedia.",
            "citations": [],
        }

    context = _format_context(chunks)
    user_message = f"---\n{context}\n---\n\nPertanyaan: {query}"  # FIX: no SYSTEM_PROMPT duplication

    if settings.llm_api_url:
        raw_response = await _call_llm_api(user_message)
    else:
        raw_response = _generate_stub_answer(query, chunks)

    return _parse_response(raw_response, chunks)


def _format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a structured context block."""
    parts = []
    for i, ch in enumerate(chunks, 1):
        ref = f"[{i}] Dokumen: {ch['document_title']}"
        if ch.get("bab"):
            ref += f", Bab {ch['bab']}"
        if ch.get("pasal"):
            ref += f", Pasal {ch['pasal']}"
        if ch.get("ayat"):
            ref += f", Ayat ({ch['ayat']})"
        parts.append(f"{ref}\n{ch['teks']}")
    return "\n\n".join(parts)


async def _call_llm_api(prompt: str) -> str:
    """Call internal LLM API. Supports OpenAI-compatible and custom endpoints."""
    url = settings.llm_api_url.rstrip("/")

    # OpenAI-compatible: /v1/chat/completions
    # If URL ends with /v1, append /chat/completions
    # Otherwise try appending /v1/chat/completions
    if url.endswith("/v1"):
        api_url = f"{url}/chat/completions"
    else:
        api_url = f"{url}/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                api_url,
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.3,
                    "stream": False,
                },
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            raw_text = resp.text.strip()

            # Handle SSE format: "data: {...}" or "data: [DONE]"
            if raw_text.startswith("data: "):
                # Take last complete JSON line (skip [DONE])
                lines = [l.strip() for l in raw_text.split("\n") if l.strip().startswith("data: ") and "[DONE]" not in l]
                if lines:
                    raw_text = lines[-1].replace("data: ", "", 1)

            import json as json_lib
            data = json_lib.loads(raw_text)

            # OpenAI format
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                if "text" in choice:
                    return choice["text"]
            # Simple { "response": "..." } format
            if "response" in data:
                return data["response"]
            if isinstance(data, dict):
                return str(data.get("text", data.get("content", str(data))))

            return str(data)

    except Exception as exc:
        print(f"[rag] LLM API call failed: {exc}, falling back to stub answer")
        return _generate_stub_answer(prompt.split("Pertanyaan: ")[-1] if "Pertanyaan: " in prompt else prompt, [])


async def _call_embedding_api(text: str, chunk_count: int) -> str:
    """Fallback: if LLM is chat endpoint, just return stub."""
    return _generate_stub_answer("", [])


def _generate_stub_answer(query: str, chunks: list[dict[str, Any]]) -> str:
    """Generate a structured answer from chunks (dev mode without real LLM)."""
    if not chunks:
        return "Tidak ditemukan referensi yang relevan dalam dokumen yang tersedia."

    best = chunks[0]
    excerpt = best["teks"][:300] + ("..." if len(best["teks"]) > 300 else "")
    doc_ref = f"📄 {best['document_title']}"
    if best.get("bab"):
        doc_ref += f" — BAB {best['bab']}"
    if best.get("pasal"):
        doc_ref += f", Pasal {best['pasal']}"
    if best.get("ayat"):
        doc_ref += f", Ayat ({best['ayat']})"

    multi_source = ""
    extra_refs = []
    for ch in chunks[1:3]:
        if ch.get("pasal") != best.get("pasal") or ch.get("bab") != best.get("bab"):
            ref = f"📄 {ch['document_title']}"
            if ch.get("bab"):
                ref += f" — BAB {ch['bab']}"
            if ch.get("pasal"):
                ref += f", Pasal {ch['pasal']}"
            extra_refs.append(ref)
    if extra_refs:
        multi_source = "\n\nSumber tambahan:\n" + "\n".join(extra_refs)

    return (
        f"Berdasarkan dokumen yang tersedia:\n\n"
        f"{excerpt}\n\n"
        f"Sumber: {doc_ref}"
        f"{multi_source}"
    )


def _parse_response(raw: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Parse LLM response to extract answer and citations."""
    answer = raw.strip()
    citations = []

    # Don't show citations if answer says "not found"
    not_found_indicators = [
        "tidak ditemukan referensi",
        "tidak ditemukan dalam dokumen",
        "tidak tersedia",
    ]
    is_not_found = any(indicator in answer.lower() for indicator in not_found_indicators)

    if is_not_found:
        return {"answer": answer, "citations": []}

    # Extract citations from numbered references in answer
    used_indices = set()
    ref_pattern = re.findall(r'\[(\d+)\]', answer)
    for idx_str in ref_pattern:
        idx = int(idx_str) - 1
        if 0 <= idx < len(chunks) and idx not in used_indices:
            used_indices.add(idx)
            ch = chunks[idx]
            citations.append({
                "document_name": ch["document_title"],
                "bab": ch.get("bab"),
                "pasal": ch.get("pasal"),
                "ayat": ch.get("ayat"),
                "excerpt": ch["teks"][:200] + ("..." if len(ch["teks"]) > 200 else ""),
            })

    # If no numbered references found, use first few chunks as citations
    if not citations and chunks:
        for ch in chunks[:3]:
            citations.append({
                "document_name": ch["document_title"],
                "bab": ch.get("bab"),
                "pasal": ch.get("pasal"),
                "ayat": ch.get("ayat"),
                "excerpt": ch["teks"][:200] + ("..." if len(ch["teks"]) > 200 else ""),
            })
            if len(citations) >= 3:
                break

    return {
        "answer": answer,
        "citations": citations,
    }
