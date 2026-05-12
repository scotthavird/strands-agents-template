"""Lightweight `@tool` decorator examples.

Function-style custom tools — pick this when the tool is a one-liner with
no shared state. For class-style with bundled methods, see `data_analyzer.py`.

The plain `_word_count` / `_character_count` callables are kept exported so
unit tests can call them directly without the decorator wrapper in the way.
"""
from __future__ import annotations

from strands import tool


def _word_count(text: str) -> int:
    return len(text.split())


def _character_count(text: str) -> int:
    return len(text)


@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words in `text`.

    Args:
        text: The string to count words in.

    Returns:
        The number of whitespace-separated tokens.
    """
    return _word_count(text)


@tool
def character_count(text: str) -> int:
    """Count characters (including whitespace) in `text`.

    Args:
        text: The string to count characters in.

    Returns:
        The total character length.
    """
    return _character_count(text)
