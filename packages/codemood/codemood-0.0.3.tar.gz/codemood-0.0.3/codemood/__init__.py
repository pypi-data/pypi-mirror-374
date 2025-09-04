"""
codemood
========
A fun Code Mood Analyzer that assigns 'moods' to code snippets using AI.

Example
-------
>>> from codemood import analyze_code, CodeMoodAnalyzer, reset_analyzers
>>> mood = analyze_code("for i in range(10): print(i)")
>>> print(mood)
{'label': 'POSITIVE', 'score': 0.98, 'reason': "Model got happy because it saw 'print'"}

>>> # Using a custom model
>>> mood = analyze_code("print('hello')", model="distilbert-base-uncased")

>>> # Reset cache (clear all model analyzers)
>>> reset_analyzers()
"""

from typing import Dict
from .code_mood_analyzer import CodeMoodAnalyzer

# Cache of analyzers by model name
_analyzers: Dict[str, CodeMoodAnalyzer] = {}


def _get_analyzer(model: str) -> CodeMoodAnalyzer:
    """Return a cached CodeMoodAnalyzer for the given model."""
    if model not in _analyzers:
        _analyzers[model] = CodeMoodAnalyzer(model=model)
    return _analyzers[model]


def analyze_code(
    snippet: str,
    model: str = "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
) -> dict:
    """
    Analyze the mood of a code snippet quickly.

    Parameters
    ----------
    snippet : str
        The code snippet to analyze.
    model : str, optional
        Hugging Face model to use (default = distilbert fine-tuned on SST-2).

    Returns
    -------
    dict
        Dictionary containing:
        - label: "POSITIVE" or "NEGATIVE"
        - score: confidence score (float)
        - reason: funny reason for the sentiment
    """
    analyzer = _get_analyzer(model)
    return analyzer.explain_sentiment(snippet)


def reset_analyzers() -> None:
    """
    Clear the cached analyzers.
    Useful if you want to free memory or reload models.
    """
    _analyzers.clear()


# Public API
__all__ = [
    "CodeMoodAnalyzer",
    "analyze_code",
    "reset_analyzers",
]
