# app/utils/language.py
from app.utils.filenames import normalize_lang_code

def detect_language_stub(text: str) -> str:
    # replace with langdetect/fasttext later
    return "UNK"

def normalize_language_code(code: str) -> str:
    return normalize_lang_code(code)