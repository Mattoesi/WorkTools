# app/utils/logging.py
import json
import logging
from pathlib import Path
from datetime import datetime, UTC

def setup_logger(log_dir: Path, job_id: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"tender_translator.{job_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_path = log_dir / f"job_{job_id}.jsonl"
    handler = logging.FileHandler(file_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger

def log_event(logger: logging.Logger, **event: object) -> None:
    payload = {"ts": datetime.now(UTC).isoformat(), **event}
    logger.info(json.dumps(payload, ensure_ascii=False))