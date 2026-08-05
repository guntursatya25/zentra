"""AI-assisted document structure parser — uses LLM to extract Bab/Pasal/Ayat metadata."""

import json
import re
from typing import Any

import httpx

from app.config import settings


PARSE_PROMPT = """Anda adalah parser dokumen hukum/kebijakan Indonesia. Analisis teks berikut dan ekstrak struktur dokumen.

Untuk setiap bagian, tentukan:
- bab: nomor BAB (e.g., "I", "II", "III")
- bab_judul: judul BAB
- pasal: nomor Pasal (e.g., "1", "2", "12A")
- pasal_judul: judul/ringkasan Pasal
- ayat: nomor Ayat (e.g., "1", "2", "3")
- teks: isi teks bagian tersebut

Output HARUS berupa JSON array dengan format:
[
  {
    "bab": "I",
    "bab_judul": "Ketentuan Umum",
    "pasal": "1",
    "pasal_judul": "Definisi",
    "ayat": "1",
    "teks": "Dalam Peraturan ini yang dimaksud dengan..."
  },
  ...
]

Jika tidak ada struktur BAB/Pasal/Ayat yang terdeteksi, kembalikan array dengan 1 objek:
[{"bab": null, "bab_judul": null, "pasal": null, "pasal_judul": null, "ayat": null, "teks": "seluruh teks"}]

PENTING: Output HARUS berupa JSON array yang valid, tanpa teks lain."""


async def parse_with_ai(text: str) -> list[dict[str, Any]] | None:
    """Use LLM to parse document structure from raw text.

    Returns list of sections with metadata, or None if LLM unavailable/fails.
    """
    if not settings.llm_api_url:
        return None

    # Truncate text to avoid exceeding context window
    max_chars = 12000
    truncated = text[:max_chars] if len(text) > max_chars else text
    if len(text) > max_chars:
        truncated += "\n\n[...teks dipotong, hanya menampilkan bagian awal...]"

    url = settings.llm_api_url.rstrip("/")
    if url.endswith("/v1"):
        api_url = f"{url}/chat/completions"
    else:
        api_url = f"{url}/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                api_url,
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": PARSE_PROMPT},
                        {"role": "user", "content": f"Parse dokumen berikut:\n\n{truncated}"},
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.1,  # Low temp for structured output
                    "stream": False,
                },
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            raw = resp.text.strip()

            # Handle SSE format
            if raw.startswith("data: "):
                lines = [l.strip() for l in raw.split("\n") if l.strip().startswith("data: ") and "[DONE]" not in l]
                if lines:
                    raw = lines[-1].replace("data: ", "", 1)

            data = json.loads(raw)

            # Extract content
            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content", choice.get("text", ""))
            elif "response" in data:
                content = data["response"]

            if not content:
                return None

            # Extract JSON from response (may have markdown code blocks)
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                sections = json.loads(json_match.group())
            else:
                sections = json.loads(content)

            # Validate structure
            if not isinstance(sections, list) or len(sections) == 0:
                return None

            # Normalize fields
            normalized = []
            for s in sections:
                normalized.append({
                    "bab": s.get("bab"),
                    "bab_judul": s.get("bab_judul"),
                    "pasal": s.get("pasal"),
                    "pasal_judul": s.get("pasal_judul"),
                    "ayat": s.get("ayat"),
                    "teks": s.get("teks", ""),
                    "halaman": s.get("halaman"),
                })

            return normalized

    except Exception as exc:
        print(f"[ai_parser] AI parsing failed: {exc}")
        return None
