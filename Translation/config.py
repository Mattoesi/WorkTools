# app/config.py
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PathConfig(BaseModel):
    original_dir: Path = Path("Original files")
    translated_dir: Path = Path("Translated files")
    logs_dir: Path = Path("logs")
    checkpoints_dir: Path = Path("checkpoints")


class ExtractionConfig(BaseModel):
    pdf_backend: str = "pymupdf"
    min_text_density: float = 0.02
    min_quality_score: float = 0.65


class OCRConfig(BaseModel):
    engine: str = "tesseract"
    dpi: int = 300
    languages: list[str] = ["eng", "deu", "fra", "pol", "ron", "bul", "ces", "slk", "hun", "lit", "lav", "est", "hrv", "srp", "slv", "ukr", "ell"]
    min_confidence: float = 0.70


class ChunkingConfig(BaseModel):
    max_tokens: int = 1200
    overlap_tokens: int = 80


class TranslationConfig(BaseModel):
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    target_language: str = "ENG"
    glossary_path: Path | None = None


class RetryConfig(BaseModel):
    max_attempts: int = 4
    initial_backoff_sec: float = 1.0
    max_backoff_sec: float = 20.0


class ValidationConfig(BaseModel):
    min_qc_score: float = 0.85


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TT_",
        env_nested_delimiter="__",
        extra="ignore"
    )

    paths: PathConfig = Field(default_factory=PathConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)


def load_settings() -> Settings:
    return Settings()