"""
Utilities for extracting plain text from Handelsregister PDF files.

This module is responsible only for reading a PDF and returning its
text content.
"""

from pathlib import Path

import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract plain text from a digitally generated PDF.

    Parameters
    ----------
    pdf_path : str
        Path to the input PDF file.

    Returns
    -------
    str
        Extracted text from all pages joined together.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_chunks: list[str] = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    return "\n".join(text_chunks)