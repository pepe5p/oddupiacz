"""
Unit tests for checker.py module.
"""

from pathlib import Path

from oddupiacz.checker import (
    parse_diff_for_violations,
    Violation,
)
from oddupiacz.cli_hook import format_violation_message
from oddupiacz.config import Config


def _create_test_config(forbidden_phrases: list[str]) -> Config:
    """Helper to create a test Config object."""
    return Config(
        hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
        forbidden_phrases=forbidden_phrases,
        exclude_paths=[],
        exclude_files=[],
        exclude_extensions=[],
        exclude_repos=[],
    )


class TestParseDiffForViolations:
    """Tests for parse_diff_for_violations function."""

    def test_no_violations_in_empty_diff(self) -> None:
        """Test that empty diff returns no violations."""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations("", config)
        assert violations == []

    def test_no_violations_with_empty_forbidden_list(self) -> None:
        """Test that empty forbidden list returns no violations."""
        diff = "+++ b/test.py\n+print('hello')"
        config = _create_test_config([])
        violations = parse_diff_for_violations(diff, config)
        assert violations == []

    def test_detect_single_violation(self) -> None:
        """Test detecting a single forbidden phrase."""
        diff = """+++ b/test.py
@@ -1,0 +1,1 @@
+# TODO: fix this later
"""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)

        assert len(violations) == 1
        assert violations[0].phrase == "TODO"
        assert violations[0].file == "test.py"
        assert "TODO: fix this later" in violations[0].line

    def test_detect_multiple_violations(self) -> None:
        """Test detecting multiple forbidden phrases."""
        diff = """+++ b/test.py
@@ -1,0 +1,3 @@
+# TODO: fix this
+print('test')
+# FIXME: broken code
"""
        config = _create_test_config(["TODO", "FIXME"])
        violations = parse_diff_for_violations(diff, config)

        assert len(violations) == 2
        assert violations[0].phrase == "TODO"
        assert violations[1].phrase == "FIXME"

    def test_ignore_removed_lines(self) -> None:
        """Test that removed lines (starting with -) are ignored."""
        diff = """+++ b/test.py
@@ -1,1 +1,0 @@
-# TODO: this should be ignored
"""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)
        assert violations == []

    def test_ignore_unchanged_lines(self) -> None:
        """Test that unchanged lines are ignored."""
        diff = """+++ b/test.py
@@ -1,3 +1,3 @@
 # TODO: unchanged line
+print('new line')
"""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)
        assert violations == []

    def test_case_insensitive_matching(self) -> None:
        """Test that matching is case-insensitive."""
        diff = """+++ b/test.py
@@ -1,0 +1,2 @@
+# todo: lowercase
+# TODO: uppercase
"""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)

        assert len(violations) == 2
        assert violations[0].phrase.lower() == "todo"
        assert violations[1].phrase == "TODO"

    def test_track_correct_file(self) -> None:
        """Test that violations are attributed to the correct file."""
        diff = """+++ b/file1.py
@@ -1,0 +1,1 @@
+# TODO: in file1
+++ b/file2.py
@@ -1,0 +1,1 @@
+# FIXME: in file2
"""
        config = _create_test_config(["TODO", "FIXME"])
        violations = parse_diff_for_violations(diff, config)

        assert len(violations) == 2
        assert violations[0].file == "file1.py"
        assert violations[1].file == "file2.py"

    def test_ignore_diff_header_lines(self) -> None:
        """Test that +++ header lines are not treated as added content."""
        diff = """+++ b/TODO.md
@@ -1,0 +1,1 @@
+This is a new line
"""
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)

        # Should not match "TODO" in the filename
        assert violations == []


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


class TestCheckDiffForViolations:
    """Tests for check_diff_for_violations function."""

    def test_returns_success_with_no_violations(self) -> None:
        """Test that function returns success when no violations found."""
        diff = "+++ b/test.py\n+print('hello world')"
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)

        assert len(violations) == 0

    def test_returns_failure_with_violations(self) -> None:
        """Test that function returns failure when violations found."""
        diff = "+++ b/test.py\n+# TODO: fix this"
        config = _create_test_config(["TODO"])
        violations = parse_diff_for_violations(diff, config)

        assert violations is not None
        assert len(violations) == 1
        assert violations[0].phrase == "TODO"
        assert violations[0].file == "test.py"
        assert "TODO: fix this" in violations[0].line
