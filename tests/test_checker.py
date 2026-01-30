"""
Unit tests for checker.py module.
"""

from pathlib import Path

from oddupiacz.checker import parse_diff_for_violations
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
