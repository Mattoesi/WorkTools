# services/validation.py
from __future__ import annotations

import re
from dataclasses import dataclass, field

from models.chunk import Chunk


@dataclass
class ValidationIssue:
    code: str
    severity: str  # "warning" | "error"
    message: str


@dataclass
class ValidationReport:
    score: float
    passed: bool
    issues: list[ValidationIssue] = field(default_factory=list)


_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")


def _extract_numbers(text: str) -> list[str]:
    return _NUMBER_RE.findall(text or "")


def validate_translation(chunks: list[Chunk], min_score: float = 0.85) -> ValidationReport:
    issues: list[ValidationIssue] = []

    total = len(chunks)
    if total == 0:
        issues.append(ValidationIssue(
            code="no_chunks",
            severity="error",
            message="No chunks were produced for translation."
        ))
        return ValidationReport(score=0.0, passed=False, issues=issues)

    translated = [c for c in chunks if (c.translated_text or "").strip()]
    if len(translated) != total:
        issues.append(ValidationIssue(
            code="missing_translations",
            severity="error",
            message=f"Translated chunks {len(translated)}/{total}."
        ))

    # Empty translations
    empty_translations = [c.id for c in chunks if not (c.translated_text or "").strip()]
    if empty_translations:
        issues.append(ValidationIssue(
            code="empty_translation_text",
            severity="error",
            message=f"{len(empty_translations)} chunks have empty translated_text."
        ))

    # Numeric consistency (very basic V1)
    numeric_mismatch = 0
    for c in chunks:
        src_nums = _extract_numbers(c.source_text or "")
        tgt_nums = _extract_numbers(c.translated_text or "")
        if src_nums != tgt_nums:
            numeric_mismatch += 1

    if numeric_mismatch > 0:
        issues.append(ValidationIssue(
            code="numeric_mismatch",
            severity="warning",
            message=f"{numeric_mismatch}/{total} chunks have numeric differences."
        ))

    # Scoring (simple weighted penalties)
    score = 1.0
    for i in issues:
        if i.severity == "error":
            score -= 0.30
        elif i.severity == "warning":
            score -= 0.10

    score = max(0.0, round(score, 3))
    passed = score >= min_score and all(i.severity != "error" for i in issues)

    return ValidationReport(score=score, passed=passed, issues=issues)