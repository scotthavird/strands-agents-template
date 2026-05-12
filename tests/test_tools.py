"""Unit tests for the custom tools — pure functions, no LLM."""
from __future__ import annotations

from strands_template.tools.custom_tool import _character_count, _word_count
from strands_template.tools.data_analyzer import DataAnalyzer


def test_word_count_simple():
    assert _word_count("hello world") == 2
    assert _word_count("") == 0
    assert _word_count("  one   two   three  ") == 3


def test_character_count_simple():
    assert _character_count("") == 0
    assert _character_count("abc") == 3
    assert _character_count("a b") == 3


def test_sentiment_score_positive():
    analyzer = DataAnalyzer()
    out = analyzer.sentiment_score("Great growth and a strong, promising win.")
    assert out["score"] > 0
    assert out["positive_hits"] >= 3
    assert out["negative_hits"] == 0


def test_sentiment_score_negative():
    analyzer = DataAnalyzer()
    out = analyzer.sentiment_score("This is a poor decline with serious concerning risk.")
    assert out["score"] < 0


def test_sentiment_score_neutral():
    analyzer = DataAnalyzer()
    out = analyzer.sentiment_score("The cat sat on the mat.")
    assert out == {"score": 0.0, "positive_hits": 0, "negative_hits": 0}


def test_top_terms_drops_stopwords():
    analyzer = DataAnalyzer()
    text = "alpha alpha beta beta beta gamma the the the the"
    terms = analyzer.top_terms(text, k=3)
    names = [t["term"] for t in terms]
    assert "the" not in names
    assert names[0] == "beta"
    assert names[1] == "alpha"


def test_key_phrases_returns_repeats_only():
    analyzer = DataAnalyzer()
    text = "machine learning model machine learning model unique once"
    phrases = analyzer.key_phrases(text, k=5)
    assert any("machine learning" in p for p in phrases)
    assert all("once" not in p for p in phrases)
