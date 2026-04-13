# app/models/chunk.py
from enum import Enum
from pydantic import BaseModel, Field


class ChunkStatus(str, Enum):
    PENDING = "pending"
    TRANSLATED = "translated"
    FAILED = "failed"
    VALIDATED = "validated"


class Chunk(BaseModel):
    id: str
    document_id: str
    block_ids: list[str]
    token_count: int
    source_text: str
    translated_text: str | None = None
    status: ChunkStatus = ChunkStatus.PENDING
    warnings: list[str] = Field(default_factory=list)
    confidence: float | None = None
    protected_spans: list[dict] = Field(default_factory=list)