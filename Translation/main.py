from pathlib import Path
import typer

from config import load_settings
from services.ingestion import discover_inputs, detect_format, create_job
from services.extraction import extract_document
from services.ocr import select_pages_for_ocr, run_ocr
from services.chunking import chunk_document
from utils.logging import setup_logger, log_event
from services.translation import translate_chunks
from services.validation import validate_translation
from services.rendering import render_translated_docx, write_metadata_sidecar
from services.reconstruction import cleanup_document_text

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

        # 3) OCR decision
        ocr_candidate_pages = select_pages_for_ocr(document, settings)
        document = run_ocr(document, ocr_candidate_pages, settings)

        avg_conf = 0.0
        if document.pages:
            avg_conf = sum((p.extraction_confidence or 0.0) for p in document.pages) / len(document.pages)

        typer.echo(
            f"[EXTRACTED] {f.name} | pages={len(document.pages)} "
            f"| ocr_candidates={ocr_candidate_pages} | avg_conf={avg_conf:.3f}"
        )

        ocr_used_pages = [p.number for p in document.pages if p.ocr_used]
        typer.echo(f"[OCR] {f.name} | used_on_pages={ocr_used_pages}")

        typer.echo(f"[RECONSTRUCTION] {f.name} | status=started")
        document = cleanup_document_text(document, settings)
        typer.echo(f"[RECONSTRUCTION] {f.name} | status=done")

        # 4) Chunking
        chunks = chunk_document(
            document=document,
            max_tokens=settings.chunking.max_tokens,
            overlap_tokens=settings.chunking.overlap_tokens,
        )

        if chunks:
            avg_chunk_tokens = sum(c.token_count for c in chunks) / len(chunks)
            max_chunk_tokens = max(c.token_count for c in chunks)
        else:
            avg_chunk_tokens = 0.0
            max_chunk_tokens = 0

        typer.echo(
            f"[CHUNKING] {f.name} | chunks={len(chunks)} "
            f"| avg_tokens={avg_chunk_tokens:.1f} | max_tokens={max_chunk_tokens}"
        )

        translated_chunks = translate_chunks(
            chunks=chunks,
            target_language=target,
            settings=settings,
        )

        translated_count = sum(1 for c in translated_chunks if c.status.value == "translated")
        typer.echo(
            f"[TRANSLATION] {f.name} | translated_chunks={translated_count}/{len(translated_chunks)}"
        )

        report = validate_translation(
            chunks=translated_chunks,
            min_score=settings.validation.min_qc_score,
        )

        typer.echo(
            f"[VALIDATION] {f.name} | score={report.score:.3f} "
            f"| passed={report.passed} | issues={len(report.issues)}"
        )

        for issue in report.issues:
            typer.echo(f"  - [{issue.severity.upper()}] {issue.code}: {issue.message}")

        # 5) Render output DOCX
        output_docx = render_translated_docx(
            source_document=document,
            translated_chunks=translated_chunks,
            translated_dir=settings.paths.translated_dir,
            target_language=target,
        )

        # 6) Metadata sidecar
        ocr_used_pages = [p.number for p in document.pages if p.ocr_used]
        sidecar = write_metadata_sidecar(
            source_document=document,
            translated_chunks=translated_chunks,
            output_docx_path=output_docx,
            qc_score=report.score,
            qc_passed=report.passed,
            issues_count=len(report.issues),
            job_id=job.id,
            ocr_pages=ocr_used_pages,
        )

        typer.echo(f"[RENDER] {f.name} | output={output_docx}")
        typer.echo(f"[METADATA] {f.name} | sidecar={sidecar}")

if __name__ == "__main__":
    app()