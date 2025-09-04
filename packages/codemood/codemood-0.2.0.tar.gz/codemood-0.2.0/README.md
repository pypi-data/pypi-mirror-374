# Codemood

[![PyPI version](https://img.shields.io/pypi/v/codemood.svg?color=blue)](https://pypi.org/project/codemood/)
[![PyPI downloads](https://img.shields.io/pypi/dm/codemood.svg?color=green)](https://pypi.org/project/codemood/)
[![License](https://img.shields.io/github/license/OmkarPalika/codemood.svg?color=yellow)](https://github.com/OmkarPalika/codemood/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/OmkarPalika/codemood/python-package.yml?branch=main)](https://github.com/OmkarPalika/codemood/actions)

**Advanced code analysis platform that combines AI sentiment analysis with comprehensive code quality assessment and custom model training.**

Codemood provides multi-dimensional code analysis including mood detection, security vulnerability scanning, performance bottleneck identification, optimization suggestions, and code quality metrics. Features custom model training pipeline and automatic fallback systems. Built for developers who want actionable insights into their codebase.

## Key Features

### 🧠 **Advanced Sentiment Analysis**
- **12 feature categories**: Elegant patterns, documentation, type hints, code smells
- **AST-based analysis** for Python structure understanding
- **Emotional tone detection**: 7 distinct emotional states from "Delighted" to "Distressed"
- **Custom model training**: Train your own models with provided pipeline
- **Automatic fallback**: Rule-based → Custom model → Hugging Face API

### 🔧 **Optimization Engine**
- **6 optimization categories**: Nested loops, string concatenation, linear searches
- **Specific fix suggestions**: Working code examples for each issue
- **Impact assessment**: High/Medium/Low priority classification
- **Performance improvements**: O(n²) → O(n) optimizations

### 🔒 **Security Analysis**
- **5 vulnerability types**: SQL injection, hardcoded secrets, shell injection
- **Severity classification**: Critical, High, Medium, Low
- **Line-by-line detection** with remediation suggestions

### 📊 **Comprehensive Scoring**
- **Multi-layered analysis**: Sentiment + Security + Performance + Quality
- **Confidence scoring** with reasoning explanations
- **Weighted metrics**: Balanced assessment across all dimensions

## Installation

```bash
pip install codemood
```

## Quick Start

### Advanced Sentiment Analysis
```python
from codemood import analyze_sentiment_advanced

code = '''
def fibonacci_generator(n: int):
    """Generate fibonacci sequence up to n terms."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
'''

sentiment = analyze_sentiment_advanced(code)
print(f"Overall Score: {sentiment.overall_score:.2f}")
print(f"Emotional Tone: {sentiment.emotional_tone}")
print(f"Confidence: {sentiment.confidence:.2f}")
# Output: Score: 7.20, Tone: Delighted - This code sparks joy!
```

### Optimization Suggestions
```python
from codemood import get_optimization_suggestions

problematic_code = '''
result = []
for i in range(len(items)):
    for j in range(len(items)):  # Nested loops - O(n²)
        if items[i] == items[j]:
            result.append(items[i])
'''

suggestions = get_optimization_suggestions(problematic_code)
for suggestion in suggestions:
    print(f"Issue: {suggestion.issue_type}")
    print(f"Fix: {suggestion.suggested_fix}")
    print(f"Impact: {suggestion.impact}")
# Output: Issue: nested_loops, Fix: Use set operations, Impact: High
```

### Custom Model Training
```python
# Train your own sentiment model
cd model_training
python model_trainer.py

# Model automatically integrates with codemood
from codemood import analyze_sentiment_advanced
result = analyze_sentiment_advanced(code)  # Uses your custom model + rules
```

## Advanced Usage

### Individual Analyzers
```python
from codemood import (
    AdvancedCodeAnalyzer,
    SecurityAnalyzer,
    PerformanceAnalyzer
)

# Specialized analysis
security = SecurityAnalyzer()
issues = security.analyze(code)

performance = PerformanceAnalyzer()
bottlenecks = performance.analyze(code)

advanced = AdvancedCodeAnalyzer()
mood_result = advanced.analyze(code)
```

### Custom Model Configuration
```python
from codemood import CodeMoodAnalyzer

# Use custom Hugging Face model
analyzer = CodeMoodAnalyzer(model="your-custom-model")
result = analyzer.analyze(code)
```

## Configuration

### Hugging Face Integration
Codemood works offline by default. For cloud inference:

```bash
export HF_TOKEN="your_hugging_face_token"
```

### Language Support
- **Python**: Full AST analysis with comprehensive metrics
- **Other languages**: Pattern-based analysis with generic scoring

## API Reference

### Core Functions
- `analyze_sentiment_advanced(snippet)` - Advanced sentiment with emotional tone
- `get_optimization_suggestions(snippet)` - Specific code improvements
- `analyze_comprehensive(snippet, language)` - Full analysis suite
- `analyze_code(snippet, model)` - Basic Hugging Face sentiment
- `reset_analyzers()` - Clear cached models

### Analysis Results
```python
@dataclass
class ComprehensiveAnalysis:
    mood_analysis: AdvancedMoodResult
    security_issues: List[SecurityIssue]
    performance_issues: List[PerformanceIssue]
    security_score: float
    performance_score: float
    overall_score: float
    sentiment: Dict[str, Any]
    summary: str
```

## Use Cases

- **Code Reviews**: Automated sentiment analysis with optimization suggestions
- **Developer Education**: Learn from emotional feedback and specific improvements
- **Performance Optimization**: Identify and fix O(n²) algorithms with examples
- **Custom Model Training**: Build domain-specific code quality models
- **CI/CD Integration**: Quality gates with detailed explanations
- **Security Audits**: Vulnerability detection with remediation guidance
- **Technical Debt Analysis**: Emotional understanding of code quality issues

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests for improvements.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Roadmap

### v0.3.0 - Language Expansion
- [ ] JavaScript/TypeScript AST support
- [ ] Java bytecode analysis
- [ ] Go static analysis

### v0.4.0 - Advanced Features
- [ ] Machine learning-based quality prediction
- [ ] Real-time code analysis
- [ ] Custom rule definitions

### v1.0.0 - Production Ready
- [ ] IDE plugins (VS Code, IntelliJ)
- [ ] Team analytics dashboard
- [ ] Enterprise integrations
- [ ] Performance benchmarking