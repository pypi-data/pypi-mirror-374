import pytest
from codemood import analyze_comprehensive, CodeMood
from codemood.advanced_analyzer import AdvancedCodeAnalyzer
from codemood.security_analyzer import SecurityAnalyzer
from codemood.performance_analyzer import PerformanceAnalyzer


def test_advanced_mood_analysis():
    code = "def elegant_func(): return [x for x in range(10)]"
    analyzer = AdvancedCodeAnalyzer()
    result = analyzer.analyze(code)
    
    assert result.primary_mood in [mood for mood in CodeMood]
    assert 0 <= result.confidence <= 1
    assert result.quality_score >= 0


def test_security_analysis():
    vulnerable_code = 'password = "secret123"'
    analyzer = SecurityAnalyzer()
    issues = analyzer.analyze(vulnerable_code)
    
    assert len(issues) > 0
    assert issues[0].type == "hardcoded_secrets"


def test_performance_analysis():
    slow_code = '''
for i in range(10):
    for j in range(10):
        print(i, j)
'''
    analyzer = PerformanceAnalyzer()
    issues = analyzer.analyze(slow_code)
    
    assert len(issues) > 0
    assert any(issue.type == "nested_loops" for issue in issues)


def test_comprehensive_analysis():
    code = '''
def test_func():
    password = "admin123"
    for i in range(10):
        for j in range(10):
            print(i + j)
'''
    result = analyze_comprehensive(code)
    
    assert hasattr(result, 'mood_analysis')
    assert hasattr(result, 'security_issues')
    assert hasattr(result, 'performance_issues')
    assert 0 <= result.overall_score <= 1
    assert len(result.summary) > 0