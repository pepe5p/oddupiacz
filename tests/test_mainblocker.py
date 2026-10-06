"""
Unit tests for mainblocker.py module.
"""

from oddupiacz.mainblocker import find_protected_refs, is_confirmed, parse_push_refs
from oddupiacz.models import PushRef


class TestParsePushRefs:
    """Tests for parse_push_refs function."""

    def test_parse_single_ref(self) -> None:
        """Test parsing one well-formed ref line."""
        stdin_text = "refs/heads/feature abc123 refs/heads/feature def456\n"

        refs = parse_push_refs(stdin_text=stdin_text)

        assert refs == [
            PushRef(
                local_ref="refs/heads/feature",
                local_sha="abc123",
                remote_ref="refs/heads/feature",
                remote_sha="def456",
            )
        ]

    def test_parse_branch_deletion(self) -> None:
        """Test parsing a deletion, which uses an all-zero local sha."""
        zero = "0" * 40
        stdin_text = f"(delete) {zero} refs/heads/main abc123\n"

        refs = parse_push_refs(stdin_text=stdin_text)

        assert len(refs) == 1
        assert refs[0].local_ref == "(delete)"
        assert refs[0].local_sha == zero
        assert refs[0].remote_ref == "refs/heads/main"

    def test_skip_blank_and_malformed_lines(self) -> None:
        """Test that blank and short lines are ignored."""
        stdin_text = "\nnot enough tokens\nrefs/heads/a a refs/heads/b b\n"

        refs = parse_push_refs(stdin_text=stdin_text)

        assert len(refs) == 1
        assert refs[0].remote_ref == "refs/heads/b"

    def test_empty_stdin(self) -> None:
        """Test that empty stdin yields no refs."""
        assert parse_push_refs(stdin_text="") == []


class TestFindProtectedRefs:
    """Tests for find_protected_refs function."""

    def test_feature_branch_push_is_not_protected(self) -> None:
        """Test that pushing a feature branch does not require confirmation."""
        refs = [
            PushRef(
                local_ref="refs/heads/feature",
                local_sha="abc",
                remote_ref="refs/heads/feature",
                remote_sha="def",
            )
        ]

        assert find_protected_refs(refs=refs, protected_branches=["main", "master"]) == []

    def test_pushing_feature_onto_main_is_protected(self) -> None:
        """Test that the remote ref, not the local branch, decides protection."""
        refs = [
            PushRef(
                local_ref="refs/heads/feature",
                local_sha="abc",
                remote_ref="refs/heads/main",
                remote_sha="def",
            )
        ]

        assert find_protected_refs(refs=refs, protected_branches=["main", "master"]) == ["main"]

    def test_ignores_non_branch_refs(self) -> None:
        """Test that tag updates are not treated as protected branches."""
        refs = [
            PushRef(
                local_ref="refs/tags/v1",
                local_sha="abc",
                remote_ref="refs/tags/main",
                remote_sha="def",
            )
        ]

        assert find_protected_refs(refs=refs, protected_branches=["main"]) == []

    def test_multiple_protected_branches(self) -> None:
        """Test that every protected remote branch is reported."""
        refs = [
            PushRef(local_ref="refs/heads/main", local_sha="a", remote_ref="refs/heads/main", remote_sha="b"),
            PushRef(local_ref="refs/heads/feature", local_sha="c", remote_ref="refs/heads/feature", remote_sha="d"),
            PushRef(local_ref="refs/heads/master", local_sha="e", remote_ref="refs/heads/master", remote_sha="f"),
        ]

        assert find_protected_refs(refs=refs, protected_branches=["main", "master"]) == ["main", "master"]


class TestIsConfirmed:
    """Tests for is_confirmed function."""

    def test_exact_match(self) -> None:
        """Test that the repository name confirms the push."""
        assert is_confirmed(answer="theseus", repo_name="theseus") is True

    def test_mismatch(self) -> None:
        """Test that any other answer rejects the push."""
        assert is_confirmed(answer="theseus ", repo_name="theseus") is False
        assert is_confirmed(answer="", repo_name="theseus") is False
