import re
from pathlib import Path
from typing import Optional

from .models import ReceiptData, file_name


DATE_PATTERNS = [
    r"\b(\d{4}[./-]\d{2}[./-]\d{2})\b",
    r"\b(\d{2}[./-]\d{2}[./-]\d{4})\b",
    r"\b(\d{2}[./-]\d{2}[./-]\d{2})\b",
]

TOTAL_KEYWORDS = [
    "total",
    "amount due",
    "balance due",
    "grand total",
    "summe",
    "gesamt",
    "gesamtbetrag",
    "endbetrag",
    "bruttobetrag",
    "rechnungsbetrag",
    "zahlbetrag",
    "zu zahlen",
    "betrag",
    "всего",
    "итого",
    "к оплате",
    "сумма",
    "razem",
]

VAT_KEYWORDS = [
    "vat",
    "tax",
    "mwst",
    "mws t",
    "ust",
    "umsatzsteuer",
    "mehrwertsteuer",
    "ндс",
]

VENDOR_SKIP_WORDS = {
    "rechnung",
    "invoice",
    "receipt",
    "kassenbon",
    "quittung",
    "tax invoice",
    "beleg",
}

CURRENCY_PATTERNS = [
    ("EUR", r"€|\bEUR\b"),
    ("USD", r"\$|\bUSD\b"),
    ("GBP", r"£|\bGBP\b"),
    ("RUB", r"\bRUB\b|₽|руб"),
]

AMOUNT_RE = re.compile(
    r"(?<![\dA-Za-z])"
    r"(?:\d{1,3}(?:[.\s]\d{3})+|\d+)"
    r"(?:[,.]\d{2})"
    r"(?![\dA-Za-z])"
)


def parse_receipt_text(text: str, source_path: str | Path | None = None) -> ReceiptData:
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
    text = text.replace("€", " € ")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _guess_vendor(lines: list[str]) -> Optional[str]:
    vendor_label_patterns = [
        r"\bdatum\b",
        r"\bdate\b",
        r"\btotal\b",
        r"\bsumme\b",
        r"\bgesamt\b",
        r"\bmwst\b",
        r"\bust\b",
        r"\bumsatzsteuer\b",
        r"\bmehrwertsteuer\b",
    ]

    for line in lines[:12]:
        clean = re.sub(r"[^\w\s&.,'-]", "", line).strip()

        if len(clean) < 3:
            continue

        lower = clean.lower()

        if lower in VENDOR_SKIP_WORDS:
            continue

        if any(re.search(pattern, lower) for pattern in vendor_label_patterns):
            continue

        if AMOUNT_RE.search(clean):
            continue

        return clean[:120]

    return None

    for line in lines[:12]:
        clean = re.sub(r"[^\w\s&.,'-]", "", line).strip()

        if len(clean) < 3:
            continue

        lower = clean.lower()

        if lower in VENDOR_SKIP_WORDS:
            continue

        if any(word in lower for word in ["datum", "date", "total", "summe", "gesamt", "mwst", "ust"]):
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
    all_amounts: list[float] = []
    keyword_amounts: list[float] = []

    for line in lines:
        amounts = _extract_amounts_from_line(line)

        if not amounts:
            continue

        all_amounts.extend(amounts)

        lower = line.lower()

        if any(keyword in lower for keyword in TOTAL_KEYWORDS):
            keyword_amounts.extend(amounts)

    if keyword_amounts:
        return max(keyword_amounts)

    if all_amounts:
        return max(all_amounts)

    return None


def _extract_vat(lines: list[str]) -> Optional[float]:
    vat_amounts: list[float] = []

    for line in lines:
        lower = line.lower()

        if any(keyword in lower for keyword in VAT_KEYWORDS):
            vat_amounts.extend(_extract_amounts_from_line(line))

    if vat_amounts:
        return max(vat_amounts)

    return None


def _extract_amounts_from_line(line: str) -> list[float]:
    clean_line = _remove_dates_and_percentages(line)

    values = []
    for value in AMOUNT_RE.findall(clean_line):
        number = _to_float(value)
        if number is not None:
            values.append(number)

    return values


def _remove_dates_and_percentages(line: str) -> str:
    clean_line = line

    for pattern in DATE_PATTERNS:
        clean_line = re.sub(pattern, " ", clean_line)

    clean_line = re.sub(r"\b\d{1,2}\s?%\b", " ", clean_line)

    return clean_line


def _to_float(value: str) -> Optional[float]:
    value = value.strip().replace(" ", "")

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return round(float(value), 2)
    except ValueError:
        return None