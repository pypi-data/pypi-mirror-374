#!/usr/bin/env python3
"""
Advanced Codemood Usage Examples
"""

from codemood import analyze_comprehensive, CodeMood

# Example 1: Security Issues
vulnerable_code = '''
import os
password = "admin123"  # Hardcoded password
user_input = input("Enter command: ")
os.system(user_input)  # Shell injection risk
'''

print("=== Security Analysis ===")
result = analyze_comprehensive(vulnerable_code)
print(f"Security Score: {result.security_score:.1f}/100")
print(f"Issues Found: {len(result.security_issues)}")
for issue in result.security_issues:
    print(f"  - {issue.type}: {issue.description}")

# Example 2: Performance Issues
slow_code = '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):  # Nested loops O(n²)
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# String concatenation in loop
result = ""
for i in range(1000):
    result += str(i)  # Inefficient
'''

print("\n=== Performance Analysis ===")
result = analyze_comprehensive(slow_code)
print(f"Performance Score: {result.performance_score:.1f}/100")
print(f"Issues Found: {len(result.performance_issues)}")
for issue in result.performance_issues:
    print(f"  - {issue.type}: {issue.description}")

# Example 3: High Quality Code
elegant_code = '''
def fibonacci_generator(n):
    """Generate fibonacci sequence up to n terms."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# List comprehension for filtering
primes = [x for x in range(2, 100) if all(x % i != 0 for i in range(2, int(x**0.5) + 1))]
'''

print("\n=== Quality Code Analysis ===")
result = analyze_comprehensive(elegant_code)
print(f"Overall Score: {result.overall_score:.2f}")
print(f"Primary Mood: {result.mood_analysis.primary_mood.value}")
print(f"Quality Score: {result.mood_analysis.quality_score:.2f}")
print(f"Explanation: {result.mood_analysis.explanation}")
print(f"Summary: {result.summary}")