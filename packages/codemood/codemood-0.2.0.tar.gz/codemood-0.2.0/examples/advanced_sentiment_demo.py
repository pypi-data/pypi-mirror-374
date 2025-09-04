#!/usr/bin/env python3
"""
Advanced Sentiment Analysis Demo
"""

from codemood import analyze_sentiment_advanced, get_optimization_suggestions

# Example 1: Beautiful, elegant code
elegant_code = '''
def fibonacci_generator(n: int):
    """Generate fibonacci sequence up to n terms."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Clean list comprehension
primes = [x for x in range(2, 100) 
          if all(x % i != 0 for i in range(2, int(x**0.5) + 1))]

with open('data.txt', 'r') as f:
    content = f.read()
'''

print("=== ELEGANT CODE SENTIMENT ===")
sentiment = analyze_sentiment_advanced(elegant_code)
print(f"Overall Score: {sentiment.overall_score:.2f}")
print(f"Intensity: {sentiment.intensity.name}")
print(f"Emotional Tone: {sentiment.emotional_tone}")
print(f"Confidence: {sentiment.confidence:.2f}")
print("Reasoning:")
for reason in sentiment.reasoning:
    print(f"  • {reason}")

# Example 2: Problematic code with optimization opportunities
problematic_code = '''
# TODO: Fix this ugly hack later
password = "admin123"  # FIXME: hardcoded password
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):  # Nested loops - bad performance
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# String concatenation in loop - inefficient
result = ""
for i in range(1000):
    result += str(i)

# Linear search in list
def check_membership(item, item_list):
    if item in item_list:  # O(n) search
        return True
    return False

# File handling without context manager
f = open('file.txt', 'r')
data = f.read()
f.close()
'''

print("\n=== PROBLEMATIC CODE SENTIMENT ===")
sentiment = analyze_sentiment_advanced(problematic_code)
print(f"Overall Score: {sentiment.overall_score:.2f}")
print(f"Intensity: {sentiment.intensity.name}")
print(f"Emotional Tone: {sentiment.emotional_tone}")
print(f"Confidence: {sentiment.confidence:.2f}")
print("Reasoning:")
for reason in sentiment.reasoning:
    print(f"  • {reason}")

print("\n=== OPTIMIZATION SUGGESTIONS ===")
suggestions = get_optimization_suggestions(problematic_code)
for suggestion in suggestions:
    print(f"\nLine {suggestion.line_number}: {suggestion.issue_type}")
    print(f"   Problem: {suggestion.explanation}")
    print(f"   Fix: {suggestion.suggested_fix}")
    print(f"   Impact: {suggestion.impact}")
    if suggestion.example:
        print(f"   Example:\n{suggestion.example}")

# Example 3: Mixed quality code
mixed_code = '''
class DataProcessor:
    """A class for processing data."""
    
    def __init__(self):
        self.data = []
    
    def process_items(self, items):
        # Good: uses list comprehension
        processed = [self.transform(item) for item in items if item.is_valid()]
        
        # Bad: magic number
        if len(processed) > 42:
            print("Too many items!")  # TODO: make this configurable
        
        return processed
    
    def transform(self, item):
        return item.value * 2
'''

print("\n=== MIXED QUALITY CODE SENTIMENT ===")
sentiment = analyze_sentiment_advanced(mixed_code)
print(f"Overall Score: {sentiment.overall_score:.2f}")
print(f"Intensity: {sentiment.intensity.name}")
print(f"Emotional Tone: {sentiment.emotional_tone}")
print("Feature Breakdown:")
for feature, score in sentiment.features.items():
    print(f"  • {feature}: {score:.2f}")