# services/translation.py
from __future__ import annotations

from models.chunk import Chunk, ChunkStatus


def translate_chunks(
    chunks: list[Chunk],
    target_language: str,
) -> list[Chunk]:
    """
    V1 placeholder translator.
    Later replace with OpenAI call + glossary + retry.
    """
    translated: list[Chunk] = []

    for c in chunks:
        # Placeholder behavior:
        # keep structure, simulate translation
        c.translated_text = f"[{target_language}] {c.source_text}"
        c.status = ChunkStatus.TRANSLATED
        translated.append(c)

    return translated