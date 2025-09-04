import re
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class OptimizationSuggestion:
    issue_type: str
    line_number: int
    original_code: str
    suggested_fix: str
    explanation: str
    impact: str
    example: Optional[str] = None


class OptimizationEngine:
    def __init__(self):
        self.optimizations: List[OptimizationSuggestion] = []

    def analyze_and_suggest(self, code: str) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []
        lines = code.split("\n")

        # Analyze different optimization opportunities
        suggestions.extend(self._detect_nested_loops(code, lines))
        suggestions.extend(self._detect_string_concatenation(code, lines))
        suggestions.extend(self._detect_inefficient_searches(code, lines))
        suggestions.extend(self._detect_list_operations(code, lines))
        suggestions.extend(self._detect_file_operations(code, lines))
        suggestions.extend(self._detect_dict_operations(code, lines))

        return suggestions

    def _detect_nested_loops(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        # Find nested for loops
        for i, line in enumerate(lines):
            if re.search(r"^\s*for\s+\w+\s+in\s+", line):
                # Check if next few lines have another for loop
                for j in range(i + 1, min(i + 10, len(lines))):
                    if re.search(r"^\s{4,}for\s+\w+\s+in\s+", lines[j]):
                        suggestions.append(
                            OptimizationSuggestion(
                                issue_type="nested_loops",
                                line_number=i + 1,
                                original_code=line.strip(),
                                suggested_fix="Use list comprehension or "
                                "vectorized operations",
                                explanation="Nested loops can be O(n²). Consider "
                                "using sets, dicts, or numpy for better "
                                "performance.",
                                impact="High - Can improve from O(n²) to O(n)",
                                example="""# Instead of:
result = []
for i in items1:
    for j in items2:
        if i == j:
            result.append(i)

# Use:
result = list(set(items1) & set(items2))""",
                            )
                        )
                        break

        return suggestions

    def _detect_string_concatenation(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        for i, line in enumerate(lines):
            # String concatenation in loops
            if re.search(r"\w+\s*\+=\s*", line) and any(
                re.search(r"for\s+\w+\s+in", prev_line)
                for prev_line in lines[max(0, i - 5) : i + 1]
            ):
                suggestions.append(
                    OptimizationSuggestion(
                        issue_type="string_concatenation",
                        line_number=i + 1,
                        original_code=line.strip(),
                        suggested_fix="Use join() or f-strings",
                        explanation="String concatenation in loops creates new "
                        "objects each time, causing O(n²) behavior.",
                        impact="Medium - Significant improvement for large strings",
                        example="""# Instead of:
result = ""
for item in items:
    result += str(item)

# Use:
result = "".join(str(item) for item in items)""",
                    )
                )

        return suggestions

    def _detect_inefficient_searches(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        for i, line in enumerate(lines):
            # Linear search in lists
            if re.search(r"if\s+\w+\s+in\s+\w+\s*:", line) and "list" in code:
                suggestions.append(
                    OptimizationSuggestion(
                        issue_type="linear_search",
                        line_number=i + 1,
                        original_code=line.strip(),
                        suggested_fix="Convert list to set for O(1) lookups",
                        explanation="Searching in lists is O(n). Sets provide "
                        "O(1) average lookup time.",
                        impact="High - From O(n) to O(1) for lookups",
                        example="""# Instead of:
items = [1, 2, 3, 4, 5]
if x in items:  # O(n)

# Use:
items_set = {1, 2, 3, 4, 5}
if x in items_set:  # O(1)""",
                    )
                )

        return suggestions

    def _detect_list_operations(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        for i, line in enumerate(lines):
            # Inefficient list operations
            if re.search(r"\.append\(.*\)", line) and any(
                re.search(r"for\s+\w+\s+in", code_line)
                for code_line in lines[max(0, i - 3) : i + 1]
            ):
                suggestions.append(
                    OptimizationSuggestion(
                        issue_type="list_comprehension",
                        line_number=i + 1,
                        original_code=line.strip(),
                        suggested_fix="Use list comprehension",
                        explanation="List comprehensions are faster and more "
                        "readable than append() in loops.",
                        impact="Medium - Better performance and readability",
                        example="""# Instead of:
result = []
for item in items:
    result.append(item * 2)

# Use:
result = [item * 2 for item in items]""",
                    )
                )

        return suggestions

    def _detect_file_operations(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        for i, line in enumerate(lines):
            # File operations without context manager
            if re.search(r"open\s*\(", line) and "with" not in line:
                suggestions.append(
                    OptimizationSuggestion(
                        issue_type="file_handling",
                        line_number=i + 1,
                        original_code=line.strip(),
                        suggested_fix="Use context manager (with statement)",
                        explanation="Context managers ensure proper file closure "
                        "and better resource management.",
                        impact="Low - Better resource management and error " "handling",
                        example="""# Instead of:
f = open('file.txt', 'r')
content = f.read()
f.close()

# Use:
with open('file.txt', 'r') as f:
    content = f.read()""",
                    )
                )

        return suggestions

    def _detect_dict_operations(
        self, code: str, lines: List[str]
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        for i, line in enumerate(lines):
            # Inefficient dict key checking
            if re.search(r"if\s+\w+\s+in\s+\w+\.keys\(\)", line):
                suggestions.append(
                    OptimizationSuggestion(
                        issue_type="dict_keys",
                        line_number=i + 1,
                        original_code=line.strip(),
                        suggested_fix="Check key directly in dict",
                        explanation="Checking 'key in dict' is faster than "
                        "'key in dict.keys()'.",
                        impact="Low - Minor performance improvement",
                        example="""# Instead of:
if key in my_dict.keys():

# Use:
if key in my_dict:""",
                    )
                )

        return suggestions

    def generate_optimization_report(
        self, suggestions: List[OptimizationSuggestion]
    ) -> str:
        if not suggestions:
            return (
                "🎉 No optimization opportunities found! " "Your code looks efficient."
            )

        report = f"🔧 Found {len(suggestions)} optimization " f"opportunities:\n\n"

        # Group by impact
        high_impact = [s for s in suggestions if s.impact.startswith("High")]
        medium_impact = [s for s in suggestions if s.impact.startswith("Medium")]
        low_impact = [s for s in suggestions if s.impact.startswith("Low")]

        categories = [
            ("High Impact", high_impact),
            ("Medium Impact", medium_impact),
            ("Low Impact", low_impact),
        ]
        for category, items in categories:
            if items:
                report += f"### {category} ({len(items)} issues)\n"
                for suggestion in items:
                    report += (
                        f"**Line {suggestion.line_number}**: "
                        f"{suggestion.explanation}\n"
                    )
                    report += f"💡 **Fix**: {suggestion.suggested_fix}\n\n"

        return report
