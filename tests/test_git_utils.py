"""
Unit tests for git_utils.py module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from oddupiacz.git_utils import (
    configure_git_hooks_path,
    find_local_hook_path,
    get_repo_name,
    run_local_hook_if_exists,
)


class TestGetRepoName:
    """Tests for get_repo_name function."""

    @patch("subprocess.check_output")
    def test_get_repo_name_success(self, mock_check_output: MagicMock) -> None:
        """Test getting repo name from git."""
        mock_check_output.return_value = "/home/user/projects/myrepo\n"

        result = get_repo_name()

        assert result == "myrepo"
        mock_check_output.assert_called_once()

    @patch("subprocess.check_output")
    def test_get_repo_name_not_in_git_repo(self, mock_check_output: MagicMock) -> None:
        """Test behavior when not in a git repo."""
        from subprocess import CalledProcessError

        mock_check_output.side_effect = CalledProcessError(128, "git")

        result = get_repo_name()

        assert result is None


class TestFindLocalHookPath:
    """Tests for find_local_hook_path function."""

    @patch("subprocess.check_output")
    @patch("oddupiacz.git_utils.os.access")
    @patch("pathlib.Path.exists")
    def test_find_existing_executable_hook(
        self, mock_exists: MagicMock, mock_access: MagicMock, mock_check_output: MagicMock
    ) -> None:
        """Test finding an existing executable hook."""
        mock_check_output.return_value = "/home/user/repo/.git\n"
        mock_exists.return_value = True
        mock_access.return_value = True

        result = find_local_hook_path()

        assert result is not None
        assert result.name == "pre-commit"

    @patch("subprocess.check_output")
    def test_find_local_hook_not_in_repo(self, mock_check_output: MagicMock) -> None:
        """Test behavior when not in a git repo."""
        from subprocess import CalledProcessError

        mock_check_output.side_effect = CalledProcessError(128, "git")

        result = find_local_hook_path()

        assert result is None


class TestRunLocalHookIfExists:
    """Tests for run_local_hook_if_exists function."""

    def test_run_local_hook_none_path(self) -> None:
        """Test with None hook path returns True."""
        result = run_local_hook_if_exists(None, [])

        assert result is True

    @patch("subprocess.run")
    def test_run_local_hook_success(self, mock_run: MagicMock) -> None:
        """Test running a successful local hook."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        hook_path = Path("/tmp/hooks/pre-commit")  # noqa: S108
        result = run_local_hook_if_exists(hook_path, ["arg1", "arg2"])

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_local_hook_failure(self, mock_run: MagicMock) -> None:
        """Test running a failing local hook."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        hook_path = Path("/tmp/hooks/pre-commit")  # noqa: S108
        result = run_local_hook_if_exists(hook_path, [])

        assert result is False


class TestConfigureGitHooksPath:
    """Tests for configure_git_hooks_path function."""

    @patch("subprocess.run")
    def test_configure_git_hooks_path(self, mock_run: MagicMock) -> None:
        """Test configuring git hooks path."""
        hooks_dir = Path("/tmp/.githooks_global")  # noqa: S108

        configure_git_hooks_path(hooks_dir)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "config" in call_args
        assert "--global" in call_args
        assert "core.hooksPath" in call_args
        assert str(hooks_dir) in call_args
