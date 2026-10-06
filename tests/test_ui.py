"""
Unit tests for ui.py module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from oddupiacz.config import Config, MainblockerConfig
from oddupiacz.models import HookKind
from oddupiacz.ui import (
    _find_ancestor_tty,
    confirm_repo_name,
    create_config_interactive,
    create_mainblocker_config_interactive,
    get_config_path_interactive,
    get_mainblocker_config_path_interactive,
    NoTerminalError,
    prompt_config_path,
    prompt_installation_settings,
    prompt_mainblocker_config_path,
)


class TestPromptConfigPath:
    """Tests for prompt_config_path function."""

    @patch("oddupiacz.ui.typer.confirm")
    def test_prompt_config_path_use_default(self, mock_confirm: MagicMock, tmp_path: Path) -> None:
        """Test using default config path."""
        mock_confirm.return_value = True

        result = prompt_config_path()

        assert isinstance(result, Path)
        mock_confirm.assert_called_once()

    @patch("oddupiacz.ui.typer.prompt")
    @patch("oddupiacz.ui.typer.confirm")
    def test_prompt_config_path_custom(self, mock_confirm: MagicMock, mock_prompt: MagicMock, tmp_path: Path) -> None:
        """Test using custom config path."""
        mock_confirm.return_value = False
        custom_path = str(tmp_path / "custom_config.yaml")
        mock_prompt.return_value = custom_path

        result = prompt_config_path()

        assert result == Path(custom_path).expanduser().resolve()
        mock_confirm.assert_called_once()
        mock_prompt.assert_called_once()


class TestGetConfigPathInteractive:
    """Tests for get_config_path_interactive function."""

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.prompt")
    def test_get_config_use_default(self, mock_prompt: MagicMock, mock_save: MagicMock) -> None:
        """Test choosing default configuration (option 1)."""
        mock_prompt.return_value = "1"

        config, config_path = get_config_path_interactive()

        assert isinstance(config, Config)
        assert isinstance(config_path, Path)
        assert config.forbidden_phrases == ["dupa"]
        mock_save.assert_called_once()

    @patch("oddupiacz.ui.load_config")
    @patch("oddupiacz.ui.typer.prompt")
    def test_get_config_existing_file(
        self, mock_prompt: MagicMock, mock_load_config: MagicMock, tmp_path: Path
    ) -> None:
        """Test providing path to existing config file (option 2)."""
        config_file = tmp_path / "existing.yaml"
        config_file.write_text("hooks_dir: /tmp/.githooks\nforbidden_phrases:\n  - TEST\n")

        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["TEST"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        mock_load_config.return_value = mock_config
        mock_prompt.side_effect = ["2", str(config_file)]

        config, config_path = get_config_path_interactive()

        assert config.forbidden_phrases == ["TEST"]
        assert config_path == config_file.expanduser().resolve()

    @patch("oddupiacz.ui.create_config_interactive")
    @patch("oddupiacz.ui.typer.prompt")
    def test_get_config_create_interactive(
        self, mock_prompt: MagicMock, mock_create: MagicMock, tmp_path: Path
    ) -> None:
        """Test creating config interactively (option 3)."""
        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["CUSTOM"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        mock_create.return_value = (mock_config, tmp_path / "config.yaml")
        mock_prompt.return_value = "3"

        config, config_path = get_config_path_interactive()

        assert config.forbidden_phrases == ["CUSTOM"]
        mock_create.assert_called_once()

    @patch("oddupiacz.ui.typer.prompt")
    def test_get_config_invalid_choice(self, mock_prompt: MagicMock) -> None:
        """Test invalid choice raises Exit."""
        mock_prompt.return_value = "99"

        with pytest.raises(typer.Exit):
            get_config_path_interactive()


class TestCreateConfigInteractive:
    """Tests for create_config_interactive function."""

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_create_config_minimal(self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_save: MagicMock) -> None:
        """Test creating minimal config with defaults."""
        # Use default hooks dir
        mock_confirm.side_effect = [
            True,  # Use default hooks dir
            False,  # No exclude paths
            False,  # No exclude files
            False,  # No exclude extensions
            False,  # No exclude repos
        ]
        # No forbidden phrases entered, will use defaults
        mock_prompt.return_value = ""

        config, config_path = create_config_interactive()

        assert isinstance(config, Config)
        assert config.forbidden_phrases == ["TODO", "FIXME", "temp_fix"]
        assert config.exclude_paths == []
        assert config.exclude_files == []
        mock_save.assert_called_once()

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_create_config_with_phrases(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_save: MagicMock
    ) -> None:
        """Test creating config with custom forbidden phrases."""
        mock_confirm.side_effect = [
            True,  # Use default hooks dir
            False,  # No exclude paths
            False,  # No exclude files
            False,  # No exclude extensions
            False,  # No exclude repos
        ]
        # Add two phrases then empty to finish
        mock_prompt.side_effect = ["SECRET", "PASSWORD", ""]

        config, config_path = create_config_interactive()

        assert "SECRET" in config.forbidden_phrases
        assert "PASSWORD" in config.forbidden_phrases
        assert len(config.forbidden_phrases) == 2

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_create_config_with_exclusions(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_save: MagicMock
    ) -> None:
        """Test creating config with exclusions."""
        mock_confirm.side_effect = [
            True,  # Use default hooks dir
            True,  # Add exclude paths
            True,  # Add exclude files
            False,  # No exclude extensions
            False,  # No exclude repos
        ]
        mock_prompt.side_effect = [
            "TODO",  # Forbidden phrase
            "",  # Finish forbidden phrases
            "vendor/",  # Exclude path
            "",  # Finish exclude paths
            "package-lock.json",  # Exclude file
            "",  # Finish exclude files
        ]

        config, config_path = create_config_interactive()

        assert config.forbidden_phrases == ["TODO"]
        assert "vendor/" in config.exclude_paths
        assert "package-lock.json" in config.exclude_files
        assert config.exclude_extensions == []

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_create_config_custom_hooks_dir(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_save: MagicMock, tmp_path: Path
    ) -> None:
        """Test creating config with custom hooks directory."""
        custom_dir = str(tmp_path / "custom_hooks")
        mock_confirm.side_effect = [
            False,  # Don't use default hooks dir
            False,  # No exclude paths
            False,  # No exclude files
            False,  # No exclude extensions
            False,  # No exclude repos
        ]
        mock_prompt.side_effect = [
            custom_dir,  # Custom hooks dir
            "TEST",  # Forbidden phrase
            "",  # Finish forbidden phrases
        ]

        config, config_path = create_config_interactive()

        assert config.hooks_dir == Path(custom_dir).expanduser().resolve()
        assert config.forbidden_phrases == ["TEST"]


class TestPromptInstallationSettings:
    """Tests for prompt_installation_settings function."""

    @patch("oddupiacz.ui.get_config_path_interactive")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_prompt_installation_all_defaults(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test installation with all default settings."""
        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["TODO"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        mock_get_config.return_value = (mock_config, Path("/tmp/config.yaml"))  # noqa: S108
        mock_confirm.side_effect = [
            True,  # Use default oddupiacz path
            True,  # Use default python
            True,  # Proceed with installation
        ]

        settings = prompt_installation_settings()

        assert settings.hooks_dir == Path("/tmp/.githooks")  # noqa: S108
        assert settings.python_exec != ""
        assert settings.oddupiacz_path != Path()

    @patch("oddupiacz.ui.get_config_path_interactive")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_prompt_installation_custom_python(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_get_config: MagicMock, tmp_path: Path
    ) -> None:
        """Test installation with custom Python executable."""
        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["TODO"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        config_path = tmp_path / "config.yaml"
        mock_get_config.return_value = (mock_config, config_path)
        mock_confirm.side_effect = [
            True,  # Use default oddupiacz path
            False,  # Don't use default python
            True,  # Proceed with installation
        ]
        mock_prompt.return_value = "/custom/python"

        settings = prompt_installation_settings()

        assert settings.python_exec == "/custom/python"
        assert settings.config_path == config_path

    @patch("oddupiacz.ui.get_config_path_interactive")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_prompt_installation_custom_oddupiacz_path(
        self, mock_prompt: MagicMock, mock_confirm: MagicMock, mock_get_config: MagicMock, tmp_path: Path
    ) -> None:
        """Test installation with custom Oddupiacz path."""
        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["TODO"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        mock_get_config.return_value = (mock_config, tmp_path / "config.yaml")
        custom_path = str(tmp_path / "custom_oddupiacz")
        mock_confirm.side_effect = [
            False,  # Don't use default oddupiacz path
            True,  # Use default python
            True,  # Proceed with installation
        ]
        mock_prompt.return_value = custom_path

        settings = prompt_installation_settings()

        assert settings.oddupiacz_path == Path(custom_path).expanduser().resolve()

    @patch("oddupiacz.ui.get_config_path_interactive")
    @patch("oddupiacz.ui.typer.confirm")
    def test_prompt_installation_cancelled(self, mock_confirm: MagicMock, mock_get_config: MagicMock) -> None:
        """Test cancelling installation."""
        mock_config = Config(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            forbidden_phrases=["TODO"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )
        mock_get_config.return_value = (mock_config, Path("/tmp/config.yaml"))  # noqa: S108
        mock_confirm.side_effect = [
            True,  # Use default oddupiacz path
            True,  # Use default python
            False,  # Don't proceed with installation
        ]

        with pytest.raises(typer.Exit):
            prompt_installation_settings()


class TestConfirmRepoName:
    """Tests for confirm_repo_name function."""

    @patch("builtins.open")
    def test_matching_answer_confirms(self, mock_open: MagicMock) -> None:
        """Test that retyping the repo name confirms the push."""
        tty = MagicMock()
        tty.readline.return_value = "theseus\n"
        mock_open.return_value = tty

        confirmed = confirm_repo_name(repo_name="theseus", branches=["main"], remote_name="origin")

        assert confirmed is True
        prompt = tty.write.call_args.args[0]
        assert "main" in prompt
        assert "origin" in prompt
        assert "theseus" in prompt

    @patch("builtins.open")
    def test_wrong_answer_rejects(self, mock_open: MagicMock) -> None:
        """Test that a different name rejects the push."""
        tty = MagicMock()
        tty.readline.return_value = "nope\n"
        mock_open.return_value = tty

        confirmed = confirm_repo_name(repo_name="theseus", branches=["master"], remote_name="upstream")

        assert confirmed is False

    @patch("oddupiacz.ui._find_ancestor_tty", return_value=None)
    @patch("oddupiacz.ui.sys.stdout")
    @patch("oddupiacz.ui.sys.stderr")
    @patch("builtins.open", side_effect=OSError("no tty"))
    def test_missing_terminal_raises(
        self,
        mock_open: MagicMock,
        mock_stderr: MagicMock,
        mock_stdout: MagicMock,
        mock_ancestor: MagicMock,
    ) -> None:
        """Test that a missing controlling terminal is reported."""
        mock_stderr.isatty.return_value = False
        mock_stdout.isatty.return_value = False

        with pytest.raises(NoTerminalError):
            confirm_repo_name(repo_name="theseus", branches=["main"], remote_name="origin")

    @patch("oddupiacz.ui.os.ttyname", return_value="/dev/ttys001")
    @patch("oddupiacz.ui.sys.stderr")
    @patch("builtins.open")
    def test_uses_stderr_pty_when_dev_tty_is_unavailable(
        self, mock_open: MagicMock, mock_stderr: MagicMock, mock_ttyname: MagicMock
    ) -> None:
        """Test the zsh case: /dev/tty is missing, but stderr is still the pty."""
        tty = MagicMock()
        tty.readline.return_value = "theseus\n"

        def open_side_effect(path: Path, *args: object, **kwargs: object) -> MagicMock:
            if path == Path("/dev/tty"):
                raise OSError(6, "Device not configured")
            return tty

        mock_open.side_effect = open_side_effect
        mock_stderr.isatty.return_value = True
        mock_stderr.fileno.return_value = 2

        confirmed = confirm_repo_name(repo_name="theseus", branches=["main"], remote_name="origin")

        assert confirmed is True
        mock_ttyname.assert_called_once_with(2)
        assert mock_open.call_args_list[1].args[0] == Path("/dev/ttys001")

    @patch("oddupiacz.ui._find_ancestor_tty", return_value=Path("/dev/ttys007"))
    @patch("oddupiacz.ui.sys.stdout")
    @patch("oddupiacz.ui.sys.stderr")
    @patch("builtins.open")
    def test_uses_ancestor_tty_when_hook_has_none(
        self,
        mock_open: MagicMock,
        mock_stderr: MagicMock,
        mock_stdout: MagicMock,
        mock_ancestor: MagicMock,
    ) -> None:
        """Test that the prompt uses the terminal owned by the process that launched git."""
        tty = MagicMock()
        tty.readline.return_value = "theseus\n"

        def open_side_effect(path: Path, *args: object, **kwargs: object) -> MagicMock:
            if path == Path("/dev/tty"):
                raise OSError(6, "Device not configured")
            return tty

        mock_open.side_effect = open_side_effect
        mock_stderr.isatty.return_value = False
        mock_stdout.isatty.return_value = False

        confirmed = confirm_repo_name(repo_name="theseus", branches=["main"], remote_name="origin")

        assert confirmed is True
        assert mock_open.call_args_list[1].args[0] == Path("/dev/ttys007")


class TestFindAncestorTty:
    """Tests for _find_ancestor_tty function."""

    @patch("oddupiacz.ui.subprocess.check_output")
    @patch("oddupiacz.ui.os.getppid", return_value=20)
    def test_skips_ancestor_without_tty(self, mock_getppid: MagicMock, mock_ps: MagicMock) -> None:
        """Test that a process with no tty is skipped in favor of its parent."""
        mock_ps.side_effect = ["10 ??\n", "1 ttys007\n"]

        assert _find_ancestor_tty() == Path("/dev/ttys007")

    @patch("oddupiacz.ui.subprocess.check_output")
    @patch("oddupiacz.ui.os.getppid", return_value=1)
    def test_stops_at_pid_one(self, mock_getppid: MagicMock, mock_ps: MagicMock) -> None:
        """Test that the walk does not inspect pid 1."""
        assert _find_ancestor_tty() is None
        mock_ps.assert_not_called()

    @patch("oddupiacz.ui.subprocess.check_output", return_value="not-two-fields\n")
    @patch("oddupiacz.ui.os.getppid", return_value=20)
    def test_malformed_ps_output(self, mock_getppid: MagicMock, mock_ps: MagicMock) -> None:
        """Test that unexpected ps output ends the walk."""
        assert _find_ancestor_tty() is None


class TestCreateMainblockerConfigInteractive:
    """Tests for create_mainblocker_config_interactive function."""

    @patch("oddupiacz.ui._user_config_hooks_dir", return_value=None)
    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_empty_branches_fall_back_to_main_and_master(
        self,
        mock_prompt: MagicMock,
        mock_confirm: MagicMock,
        mock_save: MagicMock,
        mock_hooks_dir: MagicMock,
    ) -> None:
        """Test that pressing Enter with no branches uses main and master."""
        mock_confirm.side_effect = [True, False]
        mock_prompt.return_value = ""

        config, _config_path = create_mainblocker_config_interactive()

        assert config.protected_branches == ["main", "master"]
        assert config.exclude_repos == []
        mock_save.assert_called_once()

    @patch("oddupiacz.ui._user_config_hooks_dir", return_value=None)
    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    def test_collects_branches_one_by_one(
        self,
        mock_prompt: MagicMock,
        mock_confirm: MagicMock,
        mock_save: MagicMock,
        mock_hooks_dir: MagicMock,
    ) -> None:
        """Test collecting protected branches until a blank line."""
        mock_confirm.side_effect = [True, False]
        mock_prompt.side_effect = ["release", "main", ""]

        config, _config_path = create_mainblocker_config_interactive()

        assert config.protected_branches == ["release", "main"]

    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui.typer.prompt")
    @patch("oddupiacz.ui._user_config_hooks_dir")
    def test_defaults_hooks_dir_from_precommit_config(
        self,
        mock_hooks_dir: MagicMock,
        mock_prompt: MagicMock,
        mock_confirm: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """Test that the hooks directory prompt starts from the pre-commit config."""
        existing = Path("/tmp/shared-hooks")  # noqa: S108
        mock_hooks_dir.return_value = existing
        mock_confirm.side_effect = [True, False]
        mock_prompt.return_value = ""

        config, _config_path = create_mainblocker_config_interactive()

        assert config.hooks_dir == existing


class TestGetMainblockerConfigPathInteractive:
    """Tests for get_mainblocker_config_path_interactive function."""

    @patch("oddupiacz.ui._user_config_hooks_dir", return_value=None)
    @patch("oddupiacz.ui.save_config")
    @patch("oddupiacz.ui.typer.prompt")
    def test_default_option(self, mock_prompt: MagicMock, mock_save: MagicMock, mock_hooks_dir: MagicMock) -> None:
        """Test choosing the default mainblocker configuration."""
        mock_prompt.return_value = "1"

        config, config_path = get_mainblocker_config_path_interactive()

        assert isinstance(config, MainblockerConfig)
        assert config.protected_branches == ["main", "master"]
        assert isinstance(config_path, Path)
        mock_save.assert_called_once()

    @patch("oddupiacz.ui.load_mainblocker_config")
    @patch("oddupiacz.ui.typer.prompt")
    def test_existing_file(self, mock_prompt: MagicMock, mock_load: MagicMock, tmp_path: Path) -> None:
        """Test pointing at an existing mainblocker config."""
        config_file = tmp_path / "existing.yaml"
        config_file.write_text("hooks_dir: /tmp/.githooks\nprotected_branches:\n  - release\n")
        mock_load.return_value = MainblockerConfig(
            hooks_dir=Path("/tmp/.githooks"),  # noqa: S108
            protected_branches=["release"],
            exclude_repos=[],
        )
        mock_prompt.side_effect = ["2", str(config_file)]

        config, config_path = get_mainblocker_config_path_interactive()

        assert config.protected_branches == ["release"]
        assert config_path == config_file.expanduser().resolve()


class TestPromptMainblockerConfigPath:
    """Tests for prompt_mainblocker_config_path function."""

    @patch("oddupiacz.ui.typer.confirm")
    def test_uses_default_path(self, mock_confirm: MagicMock) -> None:
        """Test accepting the default mainblocker config path."""
        mock_confirm.return_value = True

        result = prompt_mainblocker_config_path()

        assert result.name == "mainblocker_config.yaml"


class TestMainblockerInstallWarnsOnHooksDirMismatch:
    """Tests that installing mainblocker warns when hooks directories disagree."""

    @patch("oddupiacz.ui.typer.secho")
    @patch("oddupiacz.ui.typer.confirm")
    @patch("oddupiacz.ui._user_config_hooks_dir")
    @patch("oddupiacz.ui.get_mainblocker_config_path_interactive")
    def test_warns_when_directories_differ(
        self,
        mock_get_config: MagicMock,
        mock_hooks_dir: MagicMock,
        mock_confirm: MagicMock,
        mock_secho: MagicMock,
    ) -> None:
        """Test a warning when mainblocker would move core.hooksPath."""
        mock_get_config.return_value = (
            MainblockerConfig(
                hooks_dir=Path("/tmp/mainblocker-hooks"),  # noqa: S108
                protected_branches=["main"],
                exclude_repos=[],
            ),
            Path("/tmp/mainblocker.yaml"),  # noqa: S108
        )
        mock_hooks_dir.return_value = Path("/tmp/precommit-hooks")  # noqa: S108
        mock_confirm.side_effect = [True, True, True]

        settings = prompt_installation_settings(hook_kind=HookKind.PRE_PUSH)

        assert settings.hook_kind is HookKind.PRE_PUSH
        messages = " ".join(str(call) for call in mock_secho.call_args_list)
        assert "differs" in messages
