"""
Data models used by the Handelsregister parser.

This module defines the structured output produced by the parsing
pipeline.
"""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Representative:
    """
    Represent a legal representative extracted from a document.
    """

    role: str
    last_name: str
    first_name: str
    date_of_birth: Optional[str]
    city: Optional[str]
    authority_raw: Optional[str]

    def to_dict(self) -> dict:
        """
        Convert the representative instance to a dictionary.
        """
        return asdict(self)