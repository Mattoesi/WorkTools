# app/main.py
from pathlib import Path
import typer

from app.config import load_settings
from app.services.ingestion import discover_inputs, detect_format, create_job
from app.utils.logging import setup_logger, log_event

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

if __name__ == "__main__":
    app()