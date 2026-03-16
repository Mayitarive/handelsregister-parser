"""Utility helpers for file handling and serialisation."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    """
    Ensure that a directory exists.

    Parameters
    ----------
    path : str | Path
        Directory path to create if missing.

    Returns
    -------
    Path
        Normalised Path object.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def to_serialisable(data: Any) -> Any:
    """
    Convert dataclasses and nested containers into JSON-serialisable objects.

    Parameters
    ----------
    data : Any
        Object to serialise.

    Returns
    -------
    Any
        JSON-serialisable representation.
    """
    if is_dataclass(data):
        return asdict(data)

    if isinstance(data, dict):
        return {key: to_serialisable(value) for key, value in data.items()}

    if isinstance(data, list):
        return [to_serialisable(item) for item in data]

    return data


def save_json(path: str | Path, data: Any) -> None:
    """
    Save data to a JSON file.

    Parameters
    ----------
    path : str | Path
        Output JSON path.
    data : Any
        Data to save.
    """
    output_path = Path(path)
    ensure_dir(output_path.parent)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            to_serialisable(data),
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_json(path: str | Path) -> Any:
    """
    Load data from a JSON file.

    Parameters
    ----------
    path : str | Path
        Input JSON path.

    Returns
    -------
    Any
        Parsed JSON content.
    """
    input_path = Path(path)

    with input_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_text(path: str | Path, text: str) -> None:
    """
    Save plain text to a file.

    Parameters
    ----------
    path : str | Path
        Output text file path.
    text : str
        Text content to save.
    """
    output_path = Path(path)
    ensure_dir(output_path.parent)

    with output_path.open("w", encoding="utf-8") as file:
        file.write(text)


def write_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """
    Write rows to a CSV file.

    Parameters
    ----------
    path : str | Path
        Output CSV path.
    rows : list[dict[str, Any]]
        Rows to write.
    fieldnames : list[str]
        Ordered CSV columns.
    """
    output_path = Path(path)
    ensure_dir(output_path.parent)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)