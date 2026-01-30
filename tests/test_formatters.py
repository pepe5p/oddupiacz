"""
Unit tests for formatters.py module.
"""

from oddupiacz.formatters import format_violation_message
from oddupiacz.models import Violation


class TestFormatViolationMessage:
    """Tests for format_violation_message function."""

    def test_format_empty_violations(self) -> None:
        """Test formatting with no violations."""
        message = format_violation_message([])
        assert message == ""

    def test_format_single_violation(self) -> None:
        """Test formatting a single violation."""
        violations = [Violation(phrase="TODO", file="test.py", line="TODO: fix this")]

        message = format_violation_message(violations)

        assert "TODO" in message
        assert "test.py" in message
        assert "TODO: fix this" in message
        assert "Commit aborted" in message

    def test_format_multiple_violations(self) -> None:
        """Test formatting multiple violations."""
        violations = [
            Violation(phrase="TODO", file="test1.py", line="TODO: fix"),
            Violation(phrase="FIXME", file="test2.py", line="FIXME: broken"),
        ]

        message = format_violation_message(violations)

        assert "TODO" in message
        assert "FIXME" in message
        assert "test1.py" in message
        assert "test2.py" in message
        assert message.count("BLOCKED") == 2
