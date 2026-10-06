"""
Unit tests for config_io.py module.
"""

from pathlib import Path

from oddupiacz.config import Config, MainblockerConfig
from oddupiacz.config_io import create_hook_path, save_config
from oddupiacz.models import HookKind


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_creates_file(self, tmp_path: Path) -> None:
        """Test that save_config creates a config file."""
        config = Config(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            forbidden_phrases=["TODO", "FIXME"],
            exclude_paths=["vendor/"],
            exclude_files=["package-lock.json"],
            exclude_extensions=[".log"],
            exclude_repos=["test-repo"],
        )

        config_path = tmp_path / "test_config.yaml"
        save_config(config, config_path)

        assert config_path.exists()
        content = config_path.read_text()
        assert "TODO" in content
        assert "FIXME" in content
        assert "vendor/" in content

    def test_save_config_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test that save_config creates parent directories if needed."""
        config = Config(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            forbidden_phrases=["TODO"],
            exclude_paths=[],
            exclude_files=[],
            exclude_extensions=[],
            exclude_repos=[],
        )

        config_path = tmp_path / "nested" / "dir" / "config.yaml"
        save_config(config, config_path)

        assert config_path.exists()
        assert config_path.parent.exists()

    def test_save_mainblocker_config(self, tmp_path: Path) -> None:
        """Test that save_config writes a mainblocker config."""
        config = MainblockerConfig(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            protected_branches=["main", "master"],
            exclude_repos=["oddupiacz"],
        )

        config_path = tmp_path / "mainblocker_config.yaml"
        save_config(config=config, config_path=config_path)

        content = config_path.read_text()
        assert "main" in content
        assert "master" in content
        assert "protected_branches" in content


class TestCreateHookPath:
    """Tests for create_hook_path function."""

    def test_create_hook_path(self) -> None:
        """Test that create_hook_path returns correct path."""
        hooks_dir = Path("/tmp/.githooks_global")  # noqa: S108
        hook_path = create_hook_path(hooks_dir)

        assert hook_path == hooks_dir / "pre-commit"
        assert hook_path.name == "pre-commit"

    def test_create_pre_push_hook_path(self) -> None:
        """Test that create_hook_path can point at the mainblocker hook."""
        hooks_dir = Path("/tmp/.githooks_global")  # noqa: S108
        hook_path = create_hook_path(hooks_dir=hooks_dir, hook_kind=HookKind.PRE_PUSH)

        assert hook_path == hooks_dir / "pre-push"
