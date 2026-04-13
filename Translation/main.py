from pathlib import Path
import typer

from config import load_settings
from services.ingestion import discover_inputs, detect_format, create_job
from services.extraction import extract_document
from utils.logging import setup_logger, log_event

app = typer.Typer()


@app.command()
def translate(
    input_path: str = typer.Option(..., "--input"),
    target: str = typer.Option("ENG", "--target")
):
    settings = load_settings()

    for d in [
        settings.paths.original_dir,
        settings.paths.translated_dir,
        settings.paths.logs_dir,
        settings.paths.checkpoints_dir,
    ]:
        d.mkdir(parents=True, exist_ok=True)

    files = discover_inputs(Path(input_path))
    typer.echo(f"Discovered {len(files)} file(s).")

    for f in files:
        fmt = detect_format(f)
        if fmt == "unsupported":
            typer.echo(f"Skipping unsupported: {f.name}")
            continue

        # 1) Create job + log
        job = create_job(f, target)
        logger = setup_logger(settings.paths.logs_dir, job.id)
        log_event(
            logger,
            event="job_created",
            job_id=job.id,
            document_id=job.document_id,
            input_file=str(f),
            format=fmt,
            target_language=target,
        )
        typer.echo(f"[QUEUED] {f.name} -> job={job.id}")

        # 2) Extract native content
        document = extract_document(Path(f), target, settings)

        # 3) OCR candidate pages (quality-based)
        ocr_candidate_pages = [
            p.number
            for p in document.pages
            if (p.extraction_confidence or 0.0) < settings.extraction.min_quality_score
        ]

        avg_conf = 0.0
        if document.pages:
            avg_conf = sum((p.extraction_confidence or 0.0) for p in document.pages) / len(document.pages)

        typer.echo(
            f"[EXTRACTED] {f.name} | pages={len(document.pages)} "
            f"| ocr_candidates={ocr_candidate_pages} | avg_conf={avg_conf:.3f}"
        )


if __name__ == "__main__":
    app()