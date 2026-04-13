# app/models/document.py
from __future__ import annotations
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    HEADER = "header"
    FOOTER = "footer"
    IMAGE_PLACEHOLDER = "image_placeholder"
    PAGE_NUMBER = "page_number"


class BBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class BlockStyle(BaseModel):
    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_name: str | None = None
    font_size: float | None = None
    list_level: int | None = None


class Block(BaseModel):
    id: str
    trace_id: str
    type: BlockType
    order: int
    content: str | dict
    bbox: BBox | None = None
    style: BlockStyle = Field(default_factory=BlockStyle)
    confidence: float | None = None


class Page(BaseModel):
    number: int
    width: float | None = None
    height: float | None = None
    blocks: list[Block] = Field(default_factory=list)
    ocr_used: bool = False
    extraction_confidence: float | None = None
    ocr_confidence: float | None = None


class Document(BaseModel):
    id: str
    source_path: Path
    source_format: str
    source_language: str | None = None
    target_language: str
    pages: list[Page] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)