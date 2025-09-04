#!/usr/bin/env python3
"""
AI-Enhanced Analysis Demo
Requires: pip install openai transformers (optional)
Set: OPENAI_API_KEY environment variable
"""

from codemood import analyze_with_ai, analyze_sentiment_advanced

# Test code with optimization opportunities
test_code = '''
def process_data(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j]:
                result.append(items[i])
    return result

# String concatenation issue
output = ""
for item in ["a", "b", "c"]:
    output += item
'''

print("=== STANDARD ADVANCED ANALYSIS ===")
standard_result = analyze_sentiment_advanced(test_code)
print(f"Score: {standard_result.overall_score:.2f}")
print(f"Tone: {standard_result.emotional_tone}")
print(f"Features: {len(standard_result.features)}")

print("\n=== AI-ENHANCED ANALYSIS ===")
try:
    ai_result = analyze_with_ai(test_code)
    
    print(f"Base Score: {ai_result.sentiment.overall_score:.2f}")
    print(f"AI Confidence Boost: +{ai_result.confidence_boost:.2f}")
    print(f"Natural Explanation: {ai_result.natural_explanation}")
    
    print(f"\nOptimization Issues: {len(ai_result.optimizations)}")
    
    if ai_result.ai_generated_fixes:
        print("\n=== AI-GENERATED FIXES ===")
        for line, fix in ai_result.ai_generated_fixes.items():
            print(f"{line}: {fix}")
    else:
        print("\n(No AI fixes - requires OPENAI_API_KEY)")
        
except Exception as e:
    print(f"AI enhancement not available: {e}")
    print("Install: pip install openai transformers")
    print("Set: OPENAI_API_KEY environment variable")

print("\n=== COMPARISON ===")
print("Standard: Rule-based pattern matching")
print("AI-Enhanced: + Code generation + Natural language + Confidence boosting")
print("Best of both: Reliable rules + AI creativity")