"""Batch runner for HRB document parsing."""

from __future__ import annotations

from pathlib import Path

from .hrb_parser import parse_hrb_document
from .pdf_text_extractor import extract_text_from_pdf
from .utils import ensure_dir, save_json, save_text


def run_hrb_batch(
    input_dir: str = "samples/hrb",
    extracted_text_dir: str = "extracted_text/hrb",
    parsed_output_dir: str = "out/parsed/hrb",
) -> list[dict]:
    """
    Run HRB parsing in batch mode over all PDFs in the input directory.

    Parameters
    ----------
    input_dir : str
        Directory containing HRB PDF samples.
    extracted_text_dir : str
        Directory where extracted plain text files will be stored.
    parsed_output_dir : str
        Directory where parsed JSON outputs will be stored.

    Returns
    -------
    list[dict]
        Simple run summary per processed document.
    """
    input_path = Path(input_dir)
    extracted_text_path = ensure_dir(extracted_text_dir)
    parsed_output_path = ensure_dir(parsed_output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    pdf_files = sorted(input_path.glob("*.pdf"))

    results: list[dict] = []

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")

        try:
            text = extract_text_from_pdf(str(pdf_file))

            text_output_file = extracted_text_path / f"{pdf_file.stem}.txt"
            save_text(text_output_file, text)

            parsed_document = parse_hrb_document(
                text=text,
                source_file=pdf_file.name,
            )

            json_output_file = parsed_output_path / f"{pdf_file.stem}.json"
            save_json(json_output_file, parsed_document)

            results.append(
                {
                    "source_file": pdf_file.name,
                    "register_id": parsed_document.register_id,
                    "parse_status": parsed_document.parse_status,
                    "error_reason": parsed_document.error_reason,
                    "representative_count": len(parsed_document.representatives),
                    "block_found": parsed_document.block_found,
                    "authority_found": parsed_document.authority_found,
                }
            )

        except Exception as exc:
            print(f"ERROR while processing {pdf_file.name}: {exc}")

            results.append(
                {
                    "source_file": pdf_file.name,
                    "register_id": None,
                    "parse_status": "fail",
                    "error_reason": "parser_exception",
                    "representative_count": 0,
                    "block_found": False,
                    "authority_found": False,
                }
            )

    return results