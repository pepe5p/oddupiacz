"""
Core logic for parsing git diffs and detecting violations.
"""

import re
from dataclasses import dataclass

from .config import Config


@dataclass
class Violation:
    """Represents a single forbidden phrase violation."""

    phrase: str
    file: str
    line: str


def parse_diff_for_violations(diff_content: str, config: Config) -> list[Violation]:
    """
    Parse git diff output and find forbidden phrases in added lines.

    Args:
        diff_content: Git diff output (unified format)
        config: Configuration with forbidden phrases

    Returns:
        List of Violation objects
    """
    if not config.forbidden_phrases:
        return []

    pattern_str = "|".join(map(re.escape, config.forbidden_phrases))
    regex = re.compile(pattern_str, re.IGNORECASE)
    violations = []
    current_file = "unknown_file"

    for line in diff_content.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue

        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            match = regex.search(content)
            if match:
                violations.append(Violation(phrase=match.group(), file=current_file, line=content.strip()))

    return violations
