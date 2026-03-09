"""
Parser for extracting Geschäftsführer entries from HRB documents.

This module handles only HRB representative extraction. It expects
plain text that has already been extracted from a PDF.
"""

import re
from typing import List

from handelsregister_parser.models import Representative


SECTION_END_RE = re.compile(
    r"(?im)^\s*5\.?\s*Prokura|^\s*6\.?\s*a\)?\s*Rechtsform"
)

PERSON_RE = re.compile(
    r"(?P<last_name>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+),\s+"
    r"(?P<first_name>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-\s]+)"
    r"(?:,\s+(?P<extra>[^,\n]+))?"
    r"(?:,\s+\*(?P<dob>\d{2}\.\d{2}\.\d{4}))?"
    r"(?:,\s+(?P<city>[A-Za-zÄÖÜäöüß\-\s]+))?"
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
    start_markers = [
        "b) Vorstand, Leitungsorgan",
        "4.b)",
        "4. b)",
        "Geschäftsführer:",
        "Geschäftsführer:",
    ]

    start_index = -1

    for marker in start_markers:
        start_index = text.find(marker)
        if start_index != -1:
            break

    if start_index == -1:
        return ""

    remaining_text = text[start_index:]

    print("\n--- DEBUG: HRB BLOCK START ---\n")
    print(remaining_text[:1000])
    print("\n--- DEBUG: HRB BLOCK END ---\n")

    end_match = SECTION_END_RE.search(remaining_text)

    if end_match:
        return remaining_text[: end_match.start()]

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

    gf_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "Geschäftsführer:" in line or "Geschäftsführer:" in line
        ),
        None,
    )

    if gf_index is None:
        return None

    # Case 1: authority lines appear after the Geschäftsführer label.
    authority_lines_after: list[str] = []

    for line in lines[gf_index + 1 :]:
        if PERSON_RE.search(line):
            break
        authority_lines_after.append(line)

    if authority_lines_after:
        return " ".join(authority_lines_after).strip()

    # Case 2: authority line appears immediately before the label.
    if gf_index > 0:
        previous_line = lines[gf_index - 1]

        if not PERSON_RE.search(previous_line):
            return previous_line.strip()

    # Case 3: authority and representative may be inline on the same line.
    current_line = lines[gf_index]
    label_parts = current_line.split(":", 1)

    if len(label_parts) == 2:
        remainder = label_parts[1].strip()
        if remainder and not PERSON_RE.search(remainder):
            return remainder

    return None

def extract_representative_lines(block: str) -> str:
    """
    Extract only the text that contains representative entries.

    The function removes the HRB section heading and keeps only the
    content starting from the Geschäftsführer label.

    Parameters
    ----------
    block : str
        Representative block extracted from the document.

    Returns
    -------
    str
        Text segment containing representative entries.
    """
    marker_options = [
        "Geschäftsführer:",
        "Geschäftsführer:",
    ]

    start_index = -1

    for marker in marker_options:
        start_index = block.find(marker)
        if start_index != -1:
            start_index += len(marker)
            break

    if start_index == -1:
        return ""

    return block[start_index:].strip()

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

    representative_text = extract_representative_lines(block)

    print("\n--- DEBUG: REPRESENTATIVE TEXT ---\n")
    print(representative_text[:1000])
    print("\n--- END REPRESENTATIVE TEXT ---\n")

    for line in representative_text.splitlines():

        line = line.strip()

        if not line:
            continue

        match = PERSON_RE.search(line)

        if not match:
            continue

        print("MATCH FOUND:", match.groupdict())

        extra = match.group("extra")
        city = match.group("city")

        if city is None and extra:
            city = extra
            extra = None

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