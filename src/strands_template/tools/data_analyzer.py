"""Class-style custom tools — pick this when you want bundled, related
capabilities sharing helper methods or instance state.

Each method decorated with `@tool` is exposed to the agent as a separate
tool. The instance methods are kept thin and deterministic so they're
easy to unit-test without an LLM.
"""
from __future__ import annotations

import re
from collections import Counter

from strands import tool

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in",
    "on", "at", "for", "by", "with", "as", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "from",
    "we", "you", "they", "i", "he", "she", "them", "their", "our",
})

_POSITIVE = frozenset({
    "good", "great", "excellent", "positive", "improve", "improved",
    "growth", "strong", "robust", "promising", "win", "advantage",
    "success", "successful", "leading", "best", "innovative",
})

_NEGATIVE = frozenset({
    "bad", "poor", "weak", "negative", "decline", "declined", "loss",
    "risk", "risky", "concern", "concerning", "fail", "failure", "worst",
    "problem", "problematic", "vulnerable", "threat",
})


class DataAnalyzer:
    """Heuristic text analytics. Cheap, deterministic, no LLM required."""

    @tool
    def sentiment_score(self, text: str) -> dict:
        """Return a coarse sentiment score in [-1, 1] based on keyword counts.

        Args:
            text: The text to score.

        Returns:
            A dict with `score`, `positive_hits`, and `negative_hits` keys.
        """
        tokens = self._tokenize(text)
        pos = sum(1 for t in tokens if t in _POSITIVE)
        neg = sum(1 for t in tokens if t in _NEGATIVE)
        denom = pos + neg
        score = 0.0 if denom == 0 else (pos - neg) / denom
        return {"score": round(score, 3), "positive_hits": pos, "negative_hits": neg}

    @tool
    def top_terms(self, text: str, k: int = 10) -> list[dict]:
        """Return the top-`k` most frequent non-stopword terms.

        Args:
            text: The text to analyze.
            k: How many top terms to return.

        Returns:
            A list of `{term, count}` dicts, sorted by count descending.
        """
        tokens = [t for t in self._tokenize(text) if t not in _STOPWORDS and len(t) > 2]
        counts = Counter(tokens).most_common(k)
        return [{"term": term, "count": count} for term, count in counts]

    @tool
    def key_phrases(self, text: str, k: int = 5) -> list[str]:
        """Return up to `k` repeated 2-3 word phrases.

        Args:
            text: The text to analyze.
            k: How many phrases to return.

        Returns:
            A list of phrase strings, sorted by frequency descending.
        """
        tokens = self._tokenize(text)
        bigrams = Counter(zip(tokens, tokens[1:]))
        trigrams = Counter(zip(tokens, tokens[1:], tokens[2:]))
        ngrams = bigrams + trigrams
        ranked = [
            " ".join(gram)
            for gram, count in ngrams.most_common()
            if count > 1 and not all(t in _STOPWORDS for t in gram)
        ]
        return ranked[:k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[A-Za-z][A-Za-z'-]*", text.lower())
