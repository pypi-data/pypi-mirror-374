import re
from typing import List
from dataclasses import dataclass


@dataclass
class PerformanceIssue:
    type: str
    line: int
    impact: str
    description: str
    suggestion: str


class PerformanceAnalyzer:
    def __init__(self):
        self.anti_patterns = {
            "nested_loops": {
                "impact": "high",
                "description": "Nested loops can cause O(n²) complexity",
                "suggestion": "Consider using hash maps or optimized algorithms",
            },
            "string_concatenation": {
                "impact": "medium",
                "description": "String concatenation in loops is inefficient",
                "suggestion": "Use join() or f-strings instead",
            },
            "global_variables": {
                "impact": "low",
                "description": "Global variable access is slower",
                "suggestion": "Pass variables as parameters when possible",
            },
            "inefficient_search": {
                "impact": "medium",
                "description": "Linear search in collections",
                "suggestion": "Use sets or dictionaries for O(1) lookups",
            },
        }

    def analyze(self, code: str) -> List[PerformanceIssue]:
        issues = []
        lines = code.split("\n")

        # Check for nested loops
        loop_depth = 0
        for line_num, line in enumerate(lines, 1):
            if re.search(r"\b(for|while)\b", line):
                loop_depth += 1
                if loop_depth > 1:
                    issues.append(
                        PerformanceIssue(
                            type="nested_loops",
                            line=line_num,
                            impact="high",
                            description=self.anti_patterns["nested_loops"][
                                "description"
                            ],
                            suggestion=self.anti_patterns["nested_loops"]["suggestion"],
                        )
                    )
            elif not line.strip() or line.strip().startswith("#"):
                continue
            else:
                loop_depth = 0

        # Check for string concatenation in loops
        in_loop = False
        for line_num, line in enumerate(lines, 1):
            if re.search(r"\b(for|while)\b", line):
                in_loop = True
            elif in_loop and re.search(r'\w+\s*\+=\s*["\']', line):
                issues.append(
                    PerformanceIssue(
                        type="string_concatenation",
                        line=line_num,
                        impact="medium",
                        description=self.anti_patterns["string_concatenation"][
                            "description"
                        ],
                        suggestion=self.anti_patterns["string_concatenation"][
                            "suggestion"
                        ],
                    )
                )

        # Check for global variables
        for line_num, line in enumerate(lines, 1):
            if re.search(r"\bglobal\s+\w+", line):
                issues.append(
                    PerformanceIssue(
                        type="global_variables",
                        line=line_num,
                        impact="low",
                        description=self.anti_patterns["global_variables"][
                            "description"
                        ],
                        suggestion=self.anti_patterns["global_variables"]["suggestion"],
                    )
                )

        return issues

    def get_performance_score(self, issues: List[PerformanceIssue]) -> float:
        if not issues:
            return 100.0

        penalty = {"high": 25, "medium": 15, "low": 5}
        total_penalty = sum(penalty.get(issue.impact, 10) for issue in issues)
        return max(0.0, 100.0 - total_penalty)
