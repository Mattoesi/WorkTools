def select_pages_for_ocr(document, min_quality):
    return [p.number for p in document.pages if (p.extraction_confidence or 0) < min_quality]

def run_ocr(document, page_numbers, settings):
    # placeholder: mark pages as OCR-used
    for p in document.pages:
        if p.number in page_numbers:
            p.ocr_used = True
            p.ocr_confidence = 0.80
    return document