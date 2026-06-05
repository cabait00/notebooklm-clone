from pathlib import Path

import fitz  # PyMuPDF

SUPPORTED_TYPES = {"pdf", "txt", "md"}


def extract_text(file_path: Path, file_type: str) -> str:
    if file_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {file_type!r}")
    if file_type == "pdf":
        return _extract_pdf(file_path)
    return _extract_plain(file_path)


def _extract_pdf(file_path: Path) -> str:
    doc = fitz.open(str(file_path))
    return "\n".join(page.get_text() for page in doc)


def _extract_plain(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")
