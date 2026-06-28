import re
from pathlib import Path
from typing import Optional

from .models import ReceiptData, file_name

DATE_PATTERNS = [
    r"\b(\d{2}[./-]\d{2}[./-]\d{4})\b",
    r"\b(\d{4}[./-]\d{2}[./-]\d{2})\b",
    r"\b(\d{2}[./-]\d{2}[./-]\d{2})\b",
]

TOTAL_KEYWORDS = [
    "total", "summe", "betrag", "gesamt", "zu zahlen", "amount", "balance due",
    "всего", "итого", "к оплате", "сумма", "razem", "gesamtbetrag"
]

VAT_KEYWORDS = ["vat", "mwst", "ust", "tax", "ндс", "mehrwertsteuer"]

CURRENCY_PATTERNS = [
    ("EUR", r"€|\bEUR\b"),
    ("USD", r"\$|\bUSD\b"),
    ("GBP", r"£|\bGBP\b"),
    ("RUB", r"\bRUB\b|₽|руб"),
]

AMOUNT_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[ .]\d{3})*[,.]\d{2}|\d+[,.]\d{2})(?!\d)")


def parse_receipt_text(text: str, source_path: str | Path = "") -> ReceiptData:
    normalized = _normalize_text(text)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]

    return ReceiptData(
        file_name=file_name(source_path) if source_path else "",
        vendor=_guess_vendor(lines),
        date=_extract_date(normalized),
        total=_extract_total(lines),
        vat=_extract_vat(lines),
        currency=_extract_currency(normalized),
        raw_text=text,
    )


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _guess_vendor(lines: list[str]) -> Optional[str]:
    skip_words = {"rechnung", "invoice", "receipt", "kassenbon", "tax invoice", "quittung"}
    for line in lines[:10]:
        clean = re.sub(r"[^\w\s&.,'-]", "", line).strip()
        if len(clean) < 3:
            continue
        if clean.lower() in skip_words:
            continue
        if AMOUNT_RE.search(clean):
            continue
        return clean[:120]
    return None


def _extract_date(text: str) -> Optional[str]:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _extract_currency(text: str) -> Optional[str]:
    for code, pattern in CURRENCY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return code
    return None


def _extract_total(lines: list[str]) -> Optional[float]:
    candidates: list[float] = []
    keyword_candidates: list[float] = []

    for line in lines:
        amounts = [_to_float(value) for value in AMOUNT_RE.findall(line)]
        amounts = [value for value in amounts if value is not None]
        if not amounts:
            continue
        candidates.extend(amounts)
        if any(keyword in line.lower() for keyword in TOTAL_KEYWORDS):
            keyword_candidates.extend(amounts)

    if keyword_candidates:
        return max(keyword_candidates)
    if candidates:
        return max(candidates)
    return None


def _extract_vat(lines: list[str]) -> Optional[float]:
    vat_values: list[float] = []
    for line in lines:
        if any(keyword in line.lower() for keyword in VAT_KEYWORDS):
            vat_values.extend(value for value in (_to_float(v) for v in AMOUNT_RE.findall(line)) if value is not None)
    return max(vat_values) if vat_values else None


def _to_float(value: str) -> Optional[float]:
    value = value.strip().replace(" ", "")
    # 1.234,56 -> 1234.56; 1,234.56 -> 1234.56
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    else:
        value = value.replace(",", ".")
    try:
        return round(float(value), 2)
    except ValueError:
        return None
