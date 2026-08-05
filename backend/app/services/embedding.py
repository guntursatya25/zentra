"""Embedding service — calls internal LLM API for text embeddings."""

import math
import random

import httpx

from app.config import settings

_random = random.Random(42)  # dev fallback


async def generate_embedding(text: str) -> list[float] | None:
    """Generate embedding vector for text via internal LLM API.

    Falls back to deterministic random vector if API not configured.
    Returns a plain Python list (pgvector accepts list for VECTOR column).
    """
    if not settings.llm_api_url:
        dim = settings.embedding_dimension
        vec = [_random.random() for _ in range(dim)]
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.llm_api_url}/embeddings",
                json={"input": text, "model": "text-embedding-3-small"},
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["embedding"]  # already a list
            if "embedding" in data:
                return data["embedding"]  # already a list
    except Exception as exc:
        print(f"[embedding] API call failed: {exc}, falling back to random vector")
        dim = settings.embedding_dimension
        vec = [_random.random() for _ in range(dim)]
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec]
