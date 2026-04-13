# app/utils/filenames.py
from pathlib import Path

LANG_ALIASES = {
    # Core Western/Northern
    "EN": "ENG", "ENG": "ENG",
    "FR": "FRA", "FRA": "FRA",
    "DE": "DEU", "DEU": "DEU",
    "IT": "ITA", "ITA": "ITA",
    "ES": "SPA", "SPA": "SPA",
    "PT": "POR", "POR": "POR",
    "NL": "NLD", "NLD": "NLD",
    "SV": "SWE", "SWE": "SWE",
    "DA": "DAN", "DAN": "DAN",
    "FI": "FIN", "FIN": "FIN",
    "NO": "NOR", "NOR": "NOR",
    "IS": "ISL", "ISL": "ISL",
    "GA": "GLE", "GLE": "GLE",
    "MT": "MLT", "MLT": "MLT",

    # Central / Eastern Europe
    "PL": "POL", "POL": "POL",
    "CS": "CES", "CZ": "CES", "CES": "CES",
    "SK": "SLK", "SLK": "SLK",
    "HU": "HUN", "HUN": "HUN",
    "RO": "RON", "RON": "RON",
    "BG": "BUL", "BUL": "BUL",
    "UK": "UKR", "UKR": "UKR",
    "BE": "BEL", "BEL": "BEL",
    "RU": "RUS", "RUS": "RUS",

    # Baltics
    "LT": "LIT", "LIT": "LIT",
    "LV": "LAV", "LAV": "LAV",
    "ET": "EST", "EST": "EST",

    # Balkans / SE Europe
    "HR": "HRV", "HRV": "HRV",
    "SR": "SRP", "SRP": "SRP",
    "BS": "BOS", "BOS": "BOS",
    "SL": "SLV", "SLV": "SLV",
    "MK": "MKD", "MKD": "MKD",
    "SQ": "ALB", "AL": "ALB", "ALB": "ALB",
    "EL": "ELL", "GR": "ELL", "ELL": "ELL",
    "TR": "TUR", "TUR": "TUR",

}

def normalize_lang_code(code: str) -> str:
    return LANG_ALIASES.get(code.strip().upper(), code.strip().upper())

def translated_docx_name(source_file: Path, target_lang: str) -> str:
    lang = normalize_lang_code(target_lang)
    return f"{source_file.stem}_{lang}.docx"