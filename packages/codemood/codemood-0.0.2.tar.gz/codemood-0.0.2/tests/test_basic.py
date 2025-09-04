import pytest
from codemood import CodeMoodAnalyzer

def test_basic_analysis():
    analyzer = CodeMoodAnalyzer()
    result = analyzer.analyze("for i in range(3): print(i)")
    assert isinstance(result, dict)
    assert "label" in result
    assert "score" in result
