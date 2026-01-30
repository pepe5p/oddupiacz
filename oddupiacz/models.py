"""
Data models for Oddupiacz.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class Violation:
    """Represents a single forbidden phrase violation."""

    phrase: str
    file: str
    line: str


@dataclass
class InstallationSettings:
    """Settings for Oddupiacz installation."""

    HOOK_FILE_NAME: ClassVar[str] = "cli_hook"

    hooks_dir: Path
    oddupiacz_path: Path
    config_path: Path
    python_exec: str

    def create_exec_command(self) -> str:
        """Generate the command to run Oddupiacz with the current settings."""
        return f'"{self.python_exec}" -m oddupiacz.{self.HOOK_FILE_NAME} --config "{self.config_path}" "$@"'


@dataclass
class InstallationResult(InstallationSettings):
    """Result of hook installation, extends InstallationSettings with additional info."""

    dir_created: bool


@dataclass
class UninstallationResult:
    """Result of hook uninstallation."""

    hook_removed: bool
    config_unset: bool
