"""
Helpers for identifying the Handelsregister document type.

This module determines whether a document belongs to HRB or HRA based
on extracted text markers.
"""


def detect_register_type(text: str) -> str:
    """
    Detect the register type from extracted document text.

    Parameters
    ----------
    text : str
        Plain text extracted from a Handelsregister document.

    Returns
    -------
    str
        Detected register type: 'HRB', 'HRA', or 'UNKNOWN'.
    """
    if "Handelsregister B" in text or "Abteilung B" in text:
        return "HRB"

    if "Handelsregister A" in text or "Abteilung A" in text:
        return "HRA"

    return "UNKNOWN"