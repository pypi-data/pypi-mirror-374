# Test file for sentiment and optimization features
from codemood import analyze_sentiment_advanced, get_optimization_suggestions
from codemood.sentiment_engine import SentimentIntensity


def test_advanced_sentiment_positive():
    elegant_code = '''
    def clean_function(items: List[int]) -> List[int]:
        """Process items efficiently."""
        return [x * 2 for x in items if x > 0]
    '''
    
    sentiment = analyze_sentiment_advanced(elegant_code)
    assert sentiment.overall_score > 0
    assert sentiment.intensity in [SentimentIntensity.POSITIVE, SentimentIntensity.VERY_POSITIVE]
    assert sentiment.confidence > 0
    assert len(sentiment.reasoning) > 0


def test_advanced_sentiment_negative():
    bad_code = '''
    # TODO: fix this hack
    password = "admin123"
    def ugly_function():
        global x
        exec("print('bad')")
        return 12345  # magic number
    '''
    
    sentiment = analyze_sentiment_advanced(bad_code)
    assert sentiment.overall_score < 0
    assert sentiment.intensity in [SentimentIntensity.NEGATIVE, SentimentIntensity.VERY_NEGATIVE]
    assert "Contains code smells" in str(sentiment.reasoning)


def test_optimization_suggestions():
    inefficient_code = '''
    result = []
    for i in range(10):
        for j in range(10):
            result.append(i * j)
    
    text = ""
    for item in items:
        text += str(item)
    '''
    
    suggestions = get_optimization_suggestions(inefficient_code)
    assert len(suggestions) > 0
    
    # Check for nested loop detection
    nested_loop_found = any(s.issue_type == "nested_loops" for s in suggestions)
    assert nested_loop_found
    
    # Check for string concatenation detection
    string_concat_found = any(s.issue_type == "string_concatenation" for s in suggestions)
    assert string_concat_found


def test_sentiment_features():
    code_with_features = '''
    """Well documented function."""
    def process_data(items: List[str]) -> Dict[str, int]:
        # Clean implementation
        return {item: len(item) for item in items}
    '''
    
    sentiment = analyze_sentiment_advanced(code_with_features)
    assert "documentation" in sentiment.features
    assert "type_hints" in sentiment.features
    assert sentiment.features["documentation"] > 0


def test_optimization_examples():
    code_with_issues = '''
    if key in my_dict.keys():
        print("found")
    
    f = open('file.txt', 'r')
    content = f.read()
    f.close()
    '''
    
    suggestions = get_optimization_suggestions(code_with_issues)
    
    # Should detect dict.keys() inefficiency
    dict_issue = any(s.issue_type == "dict_keys" for s in suggestions)
    assert dict_issue
    
    # Should detect file handling issue
    file_issue = any(s.issue_type == "file_handling" for s in suggestions)
    assert file_issue