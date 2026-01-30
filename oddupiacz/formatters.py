"""
Output formatting utilities.
"""

from .models import Violation


def format_violation_message(violations: list[Violation]) -> str:
    """
    Format violation messages for display.

    Args:
        violations: List of Violation objects

    Returns:
        Formatted error message string (plain text, styling applied at display time)
    """
    lines = []
    for violation in violations:
        lines.append(f"[BLOCKED] Forbidden phrase found: '{violation.phrase}'")
        lines.append(f"  File: {violation.file}")
        lines.append(f"  Line: {violation.line}")
        lines.append("-" * 40)

    if violations:
        lines.append("Commit aborted.")

    return "\n".join(lines)
