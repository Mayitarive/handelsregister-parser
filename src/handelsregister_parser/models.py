"""Data models used across the Handelsregister parser pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Representative:
    """Represents a legal representative extracted from the document."""

    role: str
    last_name: str
    first_name: str
    city: Optional[str] = None
    date_of_birth: Optional[str] = None
    authority_raw: Optional[str] = None


@dataclass
class ParsedDocument:
    """Represents the result of parsing a Handelsregister document."""

    source_file: str

    register_type: Optional[str] = None
    register_number: Optional[str] = None
    register_id: Optional[str] = None

    parse_status: str = "success"
    error_reason: str = "none"

    block_found: bool = False
    authority_found: bool = False

    representatives: List[Representative] = field(default_factory=list)