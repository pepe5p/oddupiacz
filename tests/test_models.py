"""
Unit tests for models.py module.
"""

from pathlib import Path

from oddupiacz.models import InstallationSettings, Violation


class TestViolation:
    """Tests for Violation dataclass."""

    def test_violation_creation(self) -> None:
        """Test creating a Violation instance."""
        violation = Violation(phrase="TODO", file="test.py", line="# TODO: fix this")

        assert violation.phrase == "TODO"
        assert violation.file == "test.py"
        assert violation.line == "# TODO: fix this"


class TestInstallationSettings:
    """Tests for InstallationSettings dataclass."""

    def test_installation_settings_creation(self) -> None:
        """Test creating an InstallationSettings instance."""
        settings = InstallationSettings(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            oddupiacz_path=Path("/path/to/oddupiacz"),
            config_path=Path("/path/to/config.yaml"),
            python_exec="/usr/bin/python3",
        )

        assert settings.hooks_dir == Path("/tmp/.githooks_global")  # noqa: S108
        assert settings.oddupiacz_path == Path("/path/to/oddupiacz")
        assert settings.config_path == Path("/path/to/config.yaml")
        assert settings.python_exec == "/usr/bin/python3"

    def test_create_exec_command(self) -> None:
        """Test generating execution command from settings."""
        settings = InstallationSettings(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            oddupiacz_path=Path("/path/to/oddupiacz"),
            config_path=Path("/path/to/config.yaml"),
            python_exec="/usr/bin/python3",
        )

        command = settings.create_exec_command()

        assert "/usr/bin/python3" in command
        assert "-m oddupiacz.cli_hook" in command
        assert "--config" in command
        assert str(settings.config_path) in command
        assert "$@" in command
