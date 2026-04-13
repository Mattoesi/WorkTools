# services/ocr.py
from __future__ import annotations

from models.document import Document
from config import Settings


def select_pages_for_ocr(document: Document, settings: Settings) -> list[int]:
    """
    Select pages for OCR when native extraction quality is below threshold.
    """
    threshold = settings.extraction.min_quality_score
    selected: list[int] = []

    for page in document.pages:
        conf = page.extraction_confidence or 0.0
        no_blocks = len(page.blocks) == 0

        if no_blocks or conf < threshold:
            selected.append(page.number)

    return selected


def run_ocr(document: Document, page_numbers: list[int], settings: Settings) -> Document:
    """
    Placeholder OCR step for now.
    Marks selected pages as OCR-used and assigns baseline OCR confidence.
    """
    selected = set(page_numbers)

    for page in document.pages:
        if page.number in selected:
            page.ocr_used = True
            # placeholder confidence; real OCR engine value later
            page.ocr_confidence = max(settings.ocr.min_confidence, 0.80)

    return document