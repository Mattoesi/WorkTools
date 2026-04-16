# services/translation.py
from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

from models.chunk import Chunk, ChunkStatus
from config import Settings


def _build_prompt(source_text: str, target_language: str) -> str:
    return f"""
You are a professional tender-document translator.

TASK:
Translate the SOURCE_TEXT into {target_language}.

STRICT RULES:
- Preserve structure and ordering.
- Do NOT summarize.
- Do NOT omit content.
- Preserve numbering, references, legal citations, article numbers.
- Preserve placeholders/tokens exactly if present.
- Keep table-like lines and list markers intact where possible.
- Keep acronyms/codes unless clearly translatable.

Return ONLY translated text.

SOURCE_TEXT:
{source_text}
""".strip()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=20))
def _translate_once(client: OpenAI, model: str, prompt: str, max_output_tokens: int) -> str:
    # Responses API
    resp = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=max_output_tokens,
    )
    return (resp.output_text or "").strip()


def translate_chunks(
    chunks: list[Chunk],
    target_language: str,
    settings: Settings,
) -> list[Chunk]:
    api_key = settings.translation.api_key
    if not api_key:
        # fallback: keep placeholder behavior if key is missing
        for c in chunks:
            c.translated_text = f"[{target_language}] {c.source_text}"
            c.status = ChunkStatus.TRANSLATED
            c.warnings.append("no_api_key_placeholder_translation")
        return chunks

    client = OpenAI(api_key=api_key)

    for c in chunks:
        try:
            prompt = _build_prompt(c.source_text, target_language)
            translated = _translate_once(
                client=client,
                model=settings.translation.model,
                prompt=prompt,
                max_output_tokens=settings.translation.max_output_tokens,
            )

            if not translated:
                c.status = ChunkStatus.FAILED
                c.warnings.append("empty_translation_response")
                c.translated_text = ""
            else:
                c.translated_text = translated
                c.status = ChunkStatus.TRANSLATED

        except Exception as ex:
            c.status = ChunkStatus.FAILED
            c.translated_text = ""
            c.warnings.append(f"translation_error: {type(ex).__name__}: {ex}")

    return chunks