from __future__ import annotations

from pathlib import Path
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from models.document import Document
from config import Settings


def _load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=20))
def _cleanup_once(client: OpenAI, model: str, system_prompt: str, source_text: str) -> str:
    prompt = f"{system_prompt}\n\nSOURCE_TEXT:\n{source_text}"
    resp = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=4000,
    )
    return (resp.output_text or "").strip()


def cleanup_document_text(document: Document, settings: Settings) -> Document:
    """
    Clean OCR/noisy text BEFORE translation.
    """
    if not settings.translation.api_key:
        # no API key: skip cleanup safely
        return document

    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "ocr_cleanup.txt"
    system_prompt = _load_prompt(prompt_path)

    client = OpenAI(api_key=settings.translation.api_key)

    for page in document.pages:
        for block in page.blocks:
            if isinstance(block.content, str) and block.content.strip():
                cleaned = _cleanup_once(
                    client=client,
                    model=settings.translation.model,
                    system_prompt=system_prompt,
                    source_text=block.content,
                )
                if cleaned:
                    block.content = cleaned

    return document