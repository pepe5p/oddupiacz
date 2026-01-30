"""
Unit tests for ui.py module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from oddupiacz.config import Config
from oddupiacz.ui import (
    create_config_interactive,
    get_config_path_interactive,
    prompt_config_path,
    prompt_installation_settings,
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
