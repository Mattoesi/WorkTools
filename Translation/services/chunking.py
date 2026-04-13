# services/chunking.py
from __future__ import annotations

from uuid import uuid4

from models.document import Document, BlockType, Block
from models.chunk import Chunk


def _estimate_tokens(text: str) -> int:
    # Simple heuristic: ~1.3 tokens per word
    words = len(text.split())
    return max(1, int(words * 1.3))


def _block_to_text(block: Block) -> str:
    if isinstance(block.content, str):
        return block.content.strip()

    # table or structured content
    if isinstance(block.content, dict) and "rows" in block.content:
        lines = []
        for row in block.content["rows"]:
            lines.append(" | ".join(str(c) for c in row))
        return "\n".join(lines).strip()

    return str(block.content).strip()


def chunk_document(document: Document, max_tokens: int, overlap_tokens: int = 0) -> list[Chunk]:
    """
    V1 chunker:
    - Preserves page and block order
    - Prefers heading boundaries
    - Avoids splitting table blocks
    """
    chunks: list[Chunk] = []
    current_block_ids: list[str] = []
    current_text_parts: list[str] = []
    current_tokens = 0

    def flush_chunk():
        nonlocal current_block_ids, current_text_parts, current_tokens, chunks
        if not current_block_ids:
            return

        source_text = "\n\n".join(current_text_parts).strip()
        chunks.append(
            Chunk(
                id=str(uuid4()),
                document_id=document.id,
                block_ids=current_block_ids.copy(),
                token_count=_estimate_tokens(source_text),
                source_text=source_text,
            )
        )

        # V1: no overlap yet (kept param for future)
        current_block_ids = []
        current_text_parts = []
        current_tokens = 0

    for page in document.pages:
        for block in page.blocks:
            block_text = _block_to_text(block)
            if not block_text:
                continue

            block_tokens = _estimate_tokens(block_text)

            # If heading starts and we already have content, flush first.
            if block.type == BlockType.HEADING and current_block_ids:
                flush_chunk()

            # If adding block would exceed max, flush first.
            if current_tokens > 0 and (current_tokens + block_tokens > max_tokens):
                flush_chunk()

            # If single block itself is huge, put it alone.
            if block_tokens > max_tokens:
                flush_chunk()
                chunks.append(
                    Chunk(
                        id=str(uuid4()),
                        document_id=document.id,
                        block_ids=[block.id],
                        token_count=block_tokens,
                        source_text=block_text,
                        warnings=["oversized_single_block"],
                    )
                )
                continue

            current_block_ids.append(block.id)
            current_text_parts.append(block_text)
            current_tokens += block_tokens

    flush_chunk()
    return chunks