"""Custom tools for the template's agents.

Two tool patterns ship here:
  1. `@tool` decorator on a plain function (`custom_tool.py`)
  2. Class with `@tool` methods that bundle related capabilities (`data_analyzer.py`)

`serper_search` is a no-key-friendly wrapper around the Serper web-search API —
without `SERPER_API_KEY` it returns a "search disabled" message rather than
crashing, so the template runs out of the box.
"""
from strands_template.tools.custom_tool import character_count, word_count
from strands_template.tools.data_analyzer import DataAnalyzer
from strands_template.tools.serper_search import serper_search

__all__ = [
    "DataAnalyzer",
    "character_count",
    "serper_search",
    "word_count",
]
