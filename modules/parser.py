# this file defines the text extraction module for PDF and DOCX files.
# It provides functions to extract text from these formats and
# dispatches based on file extension.
# The module uses pdfplumber for PDF extraction and python-docx for DOCX extraction.
# It raises appropriate errors if extraction fails or if no extractable text is found.

"""
Text extraction from PDF and DOCX.

Dispatches on file extension. Both formats are treated as first-class --
neither is a fallback. If you add more formats later (e.g. .txt), add a
new extractor function and register it in EXTRACTORS, don't special-case
it inline in the UI.
"""

import os
from typing import Callable
from streamlit.runtime.uploaded_file_manager import UploadedFile
import pdfplumber as pdfs
from docx import Document


def extract_text_from_pdf(file: UploadedFile) -> str:
    text_chunks: list[str] = []
    try:
        with pdfs.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")

    full_text = "\n".join(text_chunks).strip()
    if not full_text:
        raise ValueError(
            "No extractable text found in PDF. This may be a scanned image "
            "(would need OCR, not implemented) or corrupted."
        )
    return full_text


def extract_text_from_docx(file: UploadedFile) -> str:
    try:
        document = Document(file)
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX: {e}")

    text_chunks: list[str] = []

    # Paragraphs
    for para in document.paragraphs:
        if para.text.strip():
            text_chunks.append(para.text)

    # Tables -- many resumes put skills/experience in table layouts.
    # Skipping tables silently would quietly drop real content.
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip()
                                  for cell in row.cells if cell.text.strip())
            if row_text:
                text_chunks.append(row_text)

    full_text = "\n".join(text_chunks).strip()
    if not full_text:
        raise ValueError("No extractable text found in DOCX file.")
    return full_text


EXTRACTORS: dict[str, Callable[[UploadedFile], str]] = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
}


def extract_text(file: UploadedFile, filename: str | None = None) -> str:
    """
    Unified entry point. `filename` is required to determine format when
    `file` is a stream without a reliable .name (e.g. some upload objects) --
    but Streamlit's UploadedFile does expose .name, so we fall back to that.
    """
    name = filename or getattr(file, "name", None)
    if not name:
        raise ValueError("Cannot determine file type: no filename provided.")

    ext = os.path.splitext(name)[1].lower()
    extractor: Callable[[UploadedFile], str] | None = EXTRACTORS.get(ext)
    if extractor is None:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {list(EXTRACTORS.keys())}"
        )
    return extractor(file)
