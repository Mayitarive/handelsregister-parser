"""
Utilities to extract register metadata from Handelsregister text.
Example: HRB 2484
"""

import re
from typing import Optional, Tuple


REGISTER_PATTERN = re.compile(r"\b(HRB|HRA)\s*(\d+)", re.IGNORECASE)


def extract_register_metadata(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract register type and number from document text.

    Returns:
        register_type: HRB or HRA
        register_number: numeric part
        register_id: combined string (e.g. "HRB 2484")
    """

    match = REGISTER_PATTERN.search(text)

    if not match:
        return None, None, None

    register_type = match.group(1).upper()
    register_number = match.group(2)

    register_id = f"{register_type} {register_number}"

    return register_type, register_number, register_id