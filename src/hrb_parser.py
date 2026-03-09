"""
Parser for extracting Geschäftsführer entries from HRB documents.

This module handles only HRB representative extraction. It expects
plain text that has already been extracted from a PDF.
"""

import re
from typing import List

from handelsregister_parser.models import Representative


SECTION_END_RE = re.compile(
    r"(?m)^\s*5\.\s*Prokura|^\s*6\.\s*a\)\s*Rechtsform"
)

PERSON_RE = re.compile(
    r"(?P<last_name>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+),\s+"
    r"(?P<first_name>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-\s]+),\s+"
    r"(?:(?P<city_before>[A-Za-zÄÖÜäöüß\-\s]+),\s+)?"
    r"\*(?P<dob>\d{2}\.\d{2}\.\d{4})"
    r"(?:,\s+(?P<city_after>[A-Za-zÄÖÜäöüß\-\s]+))?"
)


def extract_hrb_block(text: str) -> str:
    """
    Extract the HRB representative block.

    The function starts at section 4.b and stops before the Prokura
    or Rechtsform section.

    Parameters
    ----------
    text : str
        Plain text extracted from the document.

    Returns
    -------
    str
        Extracted HRB representative block, or an empty string if no
        block is found.
    """
    start_marker = "b) Vorstand, Leitungsorgan"

    start_index = text.find(start_marker)
    if start_index == -1:
        return ""

    remaining_text = text[start_index:]
    end_match = SECTION_END_RE.search(remaining_text)

    if end_match:
        return remaining_text[:end_match.start()]

    return remaining_text


def extract_authority_text(block: str) -> str | None:
    """
    Extract raw authority text from an HRB representative block.

    Parameters
    ----------
    block : str
        Representative block extracted from the document.

    Returns
    -------
    str | None
        Raw authority text if found, otherwise None.
    """
    lines = [line.strip() for line in block.splitlines() if line.strip()]

    if "Geschäftsführer:" not in block:
        return None

    gf_index = next(
        (index for index, line in enumerate(lines) if "Geschäftsführer" in line),
        None,
    )

    if gf_index is None:
        return None

    authority_lines: list[str] = []

    for line in lines[gf_index + 1 :]:
        if PERSON_RE.search(line):
            break
        authority_lines.append(line)

    if not authority_lines:
        return None

    return " ".join(authority_lines).strip()


def parse_hrb_representatives(text: str) -> List[Representative]:
    """
    Parse Geschäftsführer representatives from an HRB document.

    Parameters
    ----------
    text : str
        Plain text extracted from an HRB document.

    Returns
    -------
    List[Representative]
        Extracted representatives.
    """
    block = extract_hrb_block(text)
    if not block:
        return []

    authority_raw = extract_authority_text(block)
    representatives: list[Representative] = []

    for match in PERSON_RE.finditer(block):
        city = match.group("city_before") or match.group("city_after")

        representatives.append(
            Representative(
                role="geschaeftsfuehrer",
                last_name=match.group("last_name").strip(),
                first_name=match.group("first_name").strip(),
                date_of_birth=match.group("dob"),
                city=city.strip() if city else None,
                authority_raw=authority_raw,
            )
        )

    return representatives