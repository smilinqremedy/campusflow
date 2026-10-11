"""JSON storage and persistence layer for CampusFlow.

Handles safe loading, saving, corruption detection, and fresh startup.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_STORAGE_PATH = Path("data/tickets.json")


class StorageError(Exception):
    """Raised when storage operations fail or file content is invalid."""
    pass


def load_tickets(filepath: str | Path = DEFAULT_STORAGE_PATH) -> list[dict[str, Any]]:
    """Load tickets from JSON file.

    Rules:
    - If file does not exist, return an empty list (fresh start).
    - If file contains malformed JSON, raise StorageError with details.
    - If file content is not a list, raise StorageError.

    Args:
        filepath: Path to the JSON data file.

    Returns:
        List of ticket dictionaries.

    Raises:
        StorageError: If JSON decoding fails or structure is corrupted.
    """
    path = Path(filepath)
    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
    except json.JSONDecodeError as err:
        raise StorageError(
            f"Storage corruption detected in '{path}': Malformed JSON (line {err.lineno}, col {err.colno})."
        ) from err
    except OSError as err:
        raise StorageError(f"Failed to read storage file '{path}': {err}") from err

    if not isinstance(data, list):
        raise StorageError(
            f"Storage corruption in '{path}': Root element must be a list of tickets, found {type(data).__name__}."
        )

    # Basic schema check: ensure every element is a dictionary
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise StorageError(
                f"Storage corruption in '{path}': Ticket at index {idx} is not a valid dictionary."
            )

    return data


def save_tickets(
    tickets: list[dict[str, Any]],
    filepath: str | Path = DEFAULT_STORAGE_PATH
) -> None:
    """Save tickets collection to JSON file safely.

    Ensures destination directory exists and uses indentation for human-readable inspection.

    Args:
        tickets: List of ticket dictionaries to persist.
        filepath: Target JSON file path.

    Raises:
        StorageError: If saving fails due to filesystem errors.
    """
    path = Path(filepath)
    try:
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
    except (OSError, TypeError) as err:
        raise StorageError(f"Failed to save tickets to '{path}': {err}") from err
