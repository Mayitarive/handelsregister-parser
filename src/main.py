"""
Command line entrypoint for the Handelsregister parser.

This module orchestrates PDF text extraction, register type detection,
and HRB parsing.
"""

import json
import sys
from pathlib import Path

from handelsregister_parser.hrb_parser import parse_hrb_representatives
from handelsregister_parser.pdf_text_extractor import extract_text_from_pdf
from handelsregister_parser.register_type_detector import detect_register_type


def main() -> None:
    """
    Run the parsing pipeline for a single PDF file.
    """
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m handelsregister_parser.main <pdf_path>")

    pdf_path = sys.argv[1]
    text = extract_text_from_pdf(pdf_path)
    register_type = detect_register_type(text)

    output = {
        "register_type": register_type,
        "representatives": [],
    }

    if register_type == "HRB":
        representatives = parse_hrb_representatives(text)
        output["representatives"] = [
            representative.to_dict() for representative in representatives
        ]

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    output_path = out_dir / f"{Path(pdf_path).stem}.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()