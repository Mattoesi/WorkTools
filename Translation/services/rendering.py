# services/rendering.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
import json

from docx import Document as DocxDocument

from models.document import Document
from models.chunk import Chunk
from utils.filenames import translated_docx_name, normalize_lang_code


def render_translated_docx(
    source_document: Document,
    translated_chunks: list[Chunk],
    translated_dir: Path,
    target_language: str,
) -> Path:
    translated_dir.mkdir(parents=True, exist_ok=True)

    output_name = translated_docx_name(source_document.source_path, target_language)
    output_path = translated_dir / output_name

    doc = DocxDocument()

    # V1: render chunk texts in order
    for chunk in translated_chunks:
        text = (chunk.translated_text or "").strip()
        if not text:
            continue

        # Split by blank lines to restore rough paragraph boundaries
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        for p in paragraphs:
            doc.add_paragraph(p.strip())

    doc.save(output_path)
    return output_path


def write_metadata_sidecar(
    source_document: Document,
    translated_chunks: list[Chunk],
    output_docx_path: Path,
    qc_score: float,
    qc_passed: bool,
    issues_count: int,
    job_id: str,
    ocr_pages: list[int],
) -> Path:
    metadata = {
        "job_id": job_id,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "source_path": str(source_document.source_path),
        "source_format": source_document.source_format,
        "source_language": source_document.source_language,
        "target_language": normalize_lang_code(source_document.target_language),
        "pages": len(source_document.pages),
        "ocr_pages": ocr_pages,
        "chunks_total": len(translated_chunks),
        "chunks_translated": sum(1 for c in translated_chunks if (c.translated_text or "").strip()),
        "qc_score": qc_score,
        "qc_passed": qc_passed,
        "qc_issues_count": issues_count,
        "output_docx": str(output_docx_path),
    }

    sidecar_path = output_docx_path.with_suffix(".metadata.json")
    sidecar_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return sidecar_path