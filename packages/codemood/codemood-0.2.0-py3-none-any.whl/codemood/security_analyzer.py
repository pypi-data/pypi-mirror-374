import re
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class SecuritySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    type: str
    severity: SecuritySeverity
    line: int
    description: str
    suggestion: str


class SecurityAnalyzer:
    def __init__(self):
        self.patterns: Dict[str, Dict[str, Any]] = {
            "sql_injection": {
                "pattern": r'(execute|query|cursor\.execute)\s*\(\s*["\'].*%.*["\']',
                "severity": SecuritySeverity.HIGH,
                "description": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries",
            },
            "hardcoded_secrets": {
                "pattern": r"(password|secret|key|token)\s*=\s*"
                r'["\'][^"\']{8,}["\']',
                "severity": SecuritySeverity.CRITICAL,
                "description": "Hardcoded credentials detected",
                "suggestion": "Use environment variables or secure vaults",
            },
            "eval_usage": {
                "pattern": r"\beval\s*\(",
                "severity": SecuritySeverity.HIGH,
                "description": "Dangerous eval() usage",
                "suggestion": "Avoid eval() or use ast.literal_eval()",
            },
            "shell_injection": {
                "pattern": r"(os\.system|subprocess\.call|subprocess\.run).*"
                r"shell\s*=\s*True",
                "severity": SecuritySeverity.HIGH,
                "description": "Shell injection risk",
                "suggestion": "Avoid shell=True or sanitize inputs",
            },
            "weak_random": {
                "pattern": r"random\.(random|randint|choice)",
                "severity": SecuritySeverity.MEDIUM,
                "description": "Weak random number generation",
                "suggestion": "Use secrets module for cryptographic purposes",
            },
        }

    def analyze(self, code: str) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for issue_type, config in self.patterns.items():
                if re.search(config["pattern"], line, re.IGNORECASE):
                    issues.append(
                        SecurityIssue(
                            type=issue_type,
                            severity=config["severity"],
                            line=line_num,
                            description=config["description"],
                            suggestion=config["suggestion"],
                        )
                    )

        return issues

    def get_security_score(self, issues: List[SecurityIssue]) -> float:
        if not issues:
            return 100.0

        penalty = {
            SecuritySeverity.LOW: 5,
            SecuritySeverity.MEDIUM: 15,
            SecuritySeverity.HIGH: 30,
            SecuritySeverity.CRITICAL: 50,
        }

        total_penalty = sum(penalty[issue.severity] for issue in issues)
        return max(0.0, 100.0 - total_penalty)
