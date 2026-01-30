"""
Unit tests for installer.py module.
"""

from pathlib import Path

from oddupiacz.config_manager import InstallationSettings
from oddupiacz.installer import (
    create_hook_directory,
    generate_shim_content,
    remove_hook_file,
    write_executable_hook,
)


class TestGenerateShimContent:
    """Tests for generate_shim_content function."""

    def test_generate_basic_shim(self) -> None:
        """Test generating a basic shim without config."""
        settings = InstallationSettings(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            oddupiacz_path=Path("/path/to/oddupiacz"),
            config_path=Path("/path/to/config.yaml"),
            python_exec="/usr/bin/python3",
        )

        content = generate_shim_content(settings)

        assert "#!/bin/sh" in content
        assert settings.python_exec in content
        assert "-m oddupiacz.cli_hook" in content
        assert "git diff --cached --unified=0 --no-color" in content
        assert "exit $EXIT_CODE" in content

    def test_generate_shim_with_config(self) -> None:
        """Test generating a shim with a config path."""
        settings = InstallationSettings(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            oddupiacz_path=Path("/path/to/oddupiacz"),
            config_path=Path("/path/to/config.yaml"),
            python_exec="/usr/bin/python3",
        )

        content = generate_shim_content(settings)

        assert settings.python_exec in content
        assert "-m oddupiacz.cli_hook" in content
        assert str(settings.config_path) in content
        assert "--config" in content

    def test_shim_pipes_git_diff_to_python(self) -> None:
        """Test that the shim correctly pipes git diff to python."""
        settings = InstallationSettings(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            oddupiacz_path=Path("/path/to/oddupiacz"),
            config_path=Path("/path/to/config.yaml"),
            python_exec="/usr/bin/python3",
        )
        content = generate_shim_content(settings)

        assert "|" in content
        assert "git diff" in content
        assert content.index("git diff") < content.index("python3")


class TestCreateHookDirectory:
    """Tests for create_hook_directory function."""

    def test_create_new_directory(self, tmp_path: Path) -> None:
        """Test creating a new directory."""
        new_dir = tmp_path / "new_hooks"

        created = create_hook_directory(new_dir)

        assert created is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory(self, tmp_path: Path) -> None:
        """Test with an existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        created = create_hook_directory(existing_dir)

        assert created is False
        assert existing_dir.exists()

    def test_create_nested_directory(self, tmp_path: Path) -> None:
        """Test creating nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "hooks"

        created = create_hook_directory(nested_dir)

        assert created is True
        assert nested_dir.exists()


class TestWriteExecutableHook:
    """Tests for write_executable_hook function."""

    def test_write_hook_creates_file(self, tmp_path: Path) -> None:
        """Test that writing a hook creates the file."""
        hook_path = tmp_path / "pre-commit"
        content = "#!/bin/sh\necho 'test'"

        write_executable_hook(hook_path, content)

        assert hook_path.exists()
        assert hook_path.read_text() == content

    def test_hook_is_executable(self, tmp_path: Path) -> None:
        """Test that the created hook is executable."""
        hook_path = tmp_path / "pre-commit"
        content = "#!/bin/sh\necho 'test'"

        write_executable_hook(hook_path, content)

        import os

        assert os.access(hook_path, os.X_OK)

    def test_overwrite_existing_hook(self, tmp_path: Path) -> None:
        """Test that writing overwrites an existing hook."""
        hook_path = tmp_path / "pre-commit"
        hook_path.write_text("old content")

        new_content = "#!/bin/sh\necho 'new'"
        write_executable_hook(hook_path, new_content)

        assert hook_path.read_text() == new_content


class TestRemoveHookFile:
    """Tests for remove_hook_file function."""

    def test_remove_existing_file(self, tmp_path: Path) -> None:
        """Test removing an existing file."""
        hook_path = tmp_path / "pre-commit"
        hook_path.write_text("content")

        removed = remove_hook_file(hook_path)

        assert removed is True
        assert not hook_path.exists()

    def test_remove_nonexistent_file(self, tmp_path: Path) -> None:
        """Test removing a file that doesn't exist."""
        hook_path = tmp_path / "nonexistent"

        removed = remove_hook_file(hook_path)

        assert removed is False
