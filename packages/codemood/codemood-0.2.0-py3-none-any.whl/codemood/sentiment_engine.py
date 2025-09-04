import ast
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class SentimentIntensity(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class SentimentFeature:
    name: str
    weight: float
    pattern: str
    description: str


@dataclass
class AdvancedSentiment:
    overall_score: float
    intensity: SentimentIntensity
    confidence: float
    features: Dict[str, float]
    reasoning: List[str]
    emotional_tone: str


class AdvancedSentimentEngine:
    def __init__(self):
        self.features = {
            # Positive sentiment features
            "elegant_patterns": SentimentFeature(
                "elegant_patterns",
                0.8,
                r"(list comprehension|generator|with\s+\w+|yield|lambda)",
                "Uses elegant Python patterns",
            ),
            "good_naming": SentimentFeature(
                "good_naming",
                0.6,
                r"(def\s+[a-z_]+[a-z0-9_]*|class\s+[A-Z][a-zA-Z]*)",
                "Follows naming conventions",
            ),
            "documentation": SentimentFeature(
                "documentation",
                0.7,
                r'(""".*?"""|\'\'\'.*?\'\'\'|#\s+\w+)',
                "Has documentation/comments",
            ),
            "type_hints": SentimentFeature(
                "type_hints", 0.5, r"(:\s*\w+|->|\btyping\b)", "Uses type annotations"
            ),
            "clean_structure": SentimentFeature(
                "clean_structure",
                0.4,
                r"(return\s+\w+|if\s+__name__|class\s+\w+)",
                "Well-structured code",
            ),
            # Negative sentiment features
            "code_smells": SentimentFeature(
                "code_smells",
                -0.9,
                r"(global\s+\w+|exec\s*\(|eval\s*\()",
                "Contains code smells",
            ),
            "magic_numbers": SentimentFeature(
                "magic_numbers", -0.4, r"\b(?!0|1)\d{2,}\b", "Uses magic numbers"
            ),
            "long_lines": SentimentFeature(
                "long_lines", -0.3, r".{120,}", "Has very long lines"
            ),
            "todo_fixme": SentimentFeature(
                "todo_fixme",
                -0.6,
                r"(TODO|FIXME|XXX|HACK)",
                "Has unfinished work markers",
            ),
            "nested_complexity": SentimentFeature(
                "nested_complexity", -0.7, r"(\s{12,}|\t{3,})", "Deeply nested code"
            ),
            # Emotional indicators
            "positive_words": SentimentFeature(
                "positive_words",
                0.5,
                r"(success|complete|valid|good|clean|optimize|improve)",
                "Contains positive language",
            ),
            "negative_words": SentimentFeature(
                "negative_words",
                -0.5,
                r"(error|fail|bad|ugly|hack|broken|deprecated)",
                "Contains negative language",
            ),
        }

    def analyze_sentiment(self, code: str) -> AdvancedSentiment:
        feature_scores: Dict[str, float] = {}
        reasoning: List[str] = []

        # Analyze each feature
        for feature_name, feature in self.features.items():
            matches = len(re.findall(feature.pattern, code, re.IGNORECASE | re.DOTALL))
            if matches > 0:
                score = feature.weight * min(matches, 3)  # Cap at 3 matches
                feature_scores[feature_name] = score
                reasoning.append(f"{feature.description} ({matches} " "occurrences)")

        # AST-based analysis for Python
        try:
            tree = ast.parse(code)
            ast_score, ast_reasoning = self._analyze_ast_sentiment(tree)
            feature_scores["ast_structure"] = ast_score
            reasoning.extend(ast_reasoning)
        except SyntaxError:
            pass

        # Calculate overall sentiment
        overall_score = sum(feature_scores.values())
        confidence = min(len(feature_scores) / 10.0, 1.0)

        # Determine intensity and emotional tone
        intensity = self._calculate_intensity(overall_score)
        emotional_tone = self._determine_emotional_tone(feature_scores, overall_score)

        return AdvancedSentiment(
            overall_score=overall_score,
            intensity=intensity,
            confidence=confidence,
            features=feature_scores,
            reasoning=reasoning,
            emotional_tone=emotional_tone,
        )

    def _analyze_ast_sentiment(self, tree: ast.AST) -> Tuple[float, List[str]]:
        # Use a class to hold mutable state for Python 3.8 compatibility
        class Analysis:
            def __init__(self) -> None:
                self.score = 0.0
                self.reasoning: List[str] = []

        analysis = Analysis()

        class SentimentVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                # Short, focused functions are positive
                if len(node.body) <= 10:
                    analysis.score += 0.3
                    analysis.reasoning.append("Contains concise functions")
                elif len(node.body) > 30:
                    analysis.score -= 0.5
                    analysis.reasoning.append("Contains very long functions")

                # Docstrings are positive
                if node.body and isinstance(node.body[0], ast.Expr):
                    try:
                        # Check for string constants (docstrings)
                        is_string = isinstance(
                            node.body[0].value, ast.Constant
                        ) and isinstance(node.body[0].value.value, str)
                    except AttributeError:
                        # Fallback for older Python versions
                        is_string = hasattr(ast, "Str") and isinstance(
                            node.body[0].value, getattr(ast, "Str", type(None))
                        )

                    if is_string:
                        analysis.score += 0.4
                        analysis.reasoning.append("Functions have docstrings")

                self.generic_visit(node)

            def visit_ListComp(self, node: ast.ListComp) -> None:
                analysis.score += 0.6
                analysis.reasoning.append("Uses list comprehensions")
                self.generic_visit(node)

            def visit_With(self, node: ast.With) -> None:
                analysis.score += 0.5
                analysis.reasoning.append("Uses context managers")
                self.generic_visit(node)

        visitor = SentimentVisitor()
        visitor.visit(tree)

        return analysis.score, analysis.reasoning

    def _calculate_intensity(self, score: float) -> SentimentIntensity:
        if score >= 2.0:
            return SentimentIntensity.VERY_POSITIVE
        elif score >= 0.5:
            return SentimentIntensity.POSITIVE
        elif score <= -2.0:
            return SentimentIntensity.VERY_NEGATIVE
        elif score <= -0.5:
            return SentimentIntensity.NEGATIVE
        else:
            return SentimentIntensity.NEUTRAL

    def _determine_emotional_tone(
        self, features: Dict[str, float], score: float
    ) -> str:
        if score > 1.5:
            return "Delighted - This code sparks joy!"
        elif score > 0.8:
            return "Happy - Clean and well-crafted code"
        elif score > 0.2:
            return "Content - Decent code with room for improvement"
        elif score > -0.5:
            return "Neutral - Standard code, nothing special"
        elif score > -1.0:
            return "Concerned - Code has some issues"
        elif score > -2.0:
            return "Frustrated - Multiple problems detected"
        else:
            return "Distressed - Code needs significant attention"
