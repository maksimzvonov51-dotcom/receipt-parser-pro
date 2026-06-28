from pathlib import Path
from typing import Iterable

import pdfplumber
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
}


def extract_text(file_path: str | Path, ocr_lang: str = "eng") -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".pdf":
        return extract_text_from_pdf(path, ocr_lang=ocr_lang)

    return extract_text_from_image(path, ocr_lang=ocr_lang)


def extract_text_from_pdf(path: Path, ocr_lang: str = "eng") -> str:
    text_parts: list[str] = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(text)

    return "\n".join(text_parts)


def extract_text_from_image(path: Path, ocr_lang: str = "eng") -> str:
    image = Image.open(path)
    return pytesseract.image_to_string(image, lang=ocr_lang)


def extract_texts_from_files(paths: Iterable[str | Path], ocr_lang: str = "eng") -> dict[str, str]:
    results: dict[str, str] = {}

    for file_path in paths:
        path = Path(file_path)
        try:
            results[path.name] = extract_text(path, ocr_lang=ocr_lang)
        except Exception as exc:
            results[path.name] = f"ERROR: {exc}"

    return results
