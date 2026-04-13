# app/services/ingestion.py
from __future__ import annotations
from pathlib import Path
from uuid import uuid4

from app.models.job import TranslationJob


SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}


def detect_format(path: Path) -> str:
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        return "unsupported"
    return ext.lstrip(".")


def discover_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]

    files: list[Path] = []
    for p in input_path.iterdir():
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            files.append(p)
    return sorted(files)


def create_job(file_path: Path, target_language: str) -> TranslationJob:
    doc_id = str(uuid4())
    job_id = str(uuid4())
    return TranslationJob(
        id=job_id,
        document_id=doc_id,
        input_path=file_path,
        target_language=target_language,
    )