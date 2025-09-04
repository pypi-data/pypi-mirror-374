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

from typing import Dict, List, Any, Optional
from .code_mood_analyzer import CodeMoodAnalyzer
from .unified_analyzer import UnifiedCodeAnalyzer, ComprehensiveAnalysis
from .advanced_analyzer import AdvancedCodeAnalyzer, CodeMood
from .security_analyzer import SecurityAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .sentiment_engine import AdvancedSentimentEngine, AdvancedSentiment
from .optimization_engine import OptimizationEngine, OptimizationSuggestion
from . import model_loader

# Cache of analyzers by model name
_analyzers: Dict[str, CodeMoodAnalyzer] = {}
_unified_analyzer = None


def _get_analyzer(model: str) -> CodeMoodAnalyzer:
    """Return a cached CodeMoodAnalyzer for the given model."""
    if model not in _analyzers:
        _analyzers[model] = CodeMoodAnalyzer(model=model)
    return _analyzers[model]


def analyze_code(
    snippet: str,
    model: str = "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
) -> Dict[str, Any]:
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
    Dict[str, Any]
        Dictionary containing:
        - label: "POSITIVE" or "NEGATIVE"
        - score: confidence score (float)
        - reason: funny reason for the sentiment
    """
    analyzer = _get_analyzer(model)
    return analyzer.explain_sentiment(snippet)


def analyze_comprehensive(
    snippet: str, language: str = "python"
) -> ComprehensiveAnalysis:
    """
    Perform comprehensive code analysis including mood, security, and performance.

    Parameters
    ----------
    snippet : str
        The code snippet to analyze.
    language : str, optional
        Programming language (default = "python").

    Returns
    -------
    ComprehensiveAnalysis
        Complete analysis results including mood, security, and performance metrics.
    """
    global _unified_analyzer
    if _unified_analyzer is None:
        _unified_analyzer = UnifiedCodeAnalyzer()
    return _unified_analyzer.analyze_comprehensive(snippet, language)


def analyze_sentiment_advanced(snippet: str) -> AdvancedSentiment:
    """
    Perform advanced sentiment analysis with detailed emotional tone detection.
    Uses custom model if available, falls back to rule-based analysis.

    Parameters
    ----------
    snippet : str
        The code snippet to analyze.

    Returns
    -------
    AdvancedSentiment
        Detailed sentiment analysis with emotional tone and reasoning.
    """
    # Try custom model first
    custom_result: Optional[Dict[str, Any]] = model_loader.get_custom_model_prediction(
        snippet
    )

    # Always use rule-based for detailed analysis
    engine = AdvancedSentimentEngine()
    rule_result = engine.analyze_sentiment(snippet)
    # Enhance with custom model if available
    if custom_result:
        # Boost confidence if custom model agrees
        if (custom_result["label"] == "POSITIVE" and rule_result.overall_score > 0) or (
            custom_result["label"] == "NEGATIVE" and rule_result.overall_score < 0
        ):
            rule_result.confidence = min(rule_result.confidence + 0.2, 1.0)
            rule_result.reasoning.append(
                f"Custom model confirms: {custom_result['label']}"
            )

    return rule_result


def get_optimization_suggestions(snippet: str) -> List[OptimizationSuggestion]:
    """
    Get specific optimization suggestions for code improvements.

    Parameters
    ----------
    snippet : str
        The code snippet to analyze.

    Returns
    -------
    List[OptimizationSuggestion]
        List of OptimizationSuggestion objects with specific fixes.
    """
    engine = OptimizationEngine()
    return engine.analyze_and_suggest(snippet)


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
    "analyze_comprehensive",
    "analyze_sentiment_advanced",
    "get_optimization_suggestions",
    "reset_analyzers",
    "UnifiedCodeAnalyzer",
    "AdvancedCodeAnalyzer",
    "SecurityAnalyzer",
    "PerformanceAnalyzer",
    "AdvancedSentimentEngine",
    "OptimizationEngine",
    "ComprehensiveAnalysis",
    "AdvancedSentiment",
    "OptimizationSuggestion",
    "CodeMood",
]
