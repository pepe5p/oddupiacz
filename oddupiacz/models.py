"""
Data models for Oddupiacz.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


@dataclass
class Violation:
    """Represents a single forbidden phrase violation."""

    phrase: str
    file: str
    line: str


class HookKind(StrEnum):
    """Which global git hook an installation writes."""

    PRE_COMMIT = "pre-commit"
    PRE_PUSH = "pre-push"

    @property
    def module_name(self) -> str:
        """Python module the generated shim executes for this hook."""
        modules = {
            HookKind.PRE_COMMIT: "cli_hook",
            HookKind.PRE_PUSH: "cli_hook_push",
        }
        return modules[self]


@dataclass
class PushRef:
    """One ref update line from a git pre-push hook."""

    local_ref: str
    local_sha: str
    remote_ref: str
    remote_sha: str


@dataclass
class InstallationSettings:
    """Settings for Oddupiacz installation."""

    hooks_dir: Path
    oddupiacz_path: Path
    config_path: Path
    python_exec: str
    hook_kind: HookKind

    def create_exec_command(self) -> str:
        """Generate the command to run Oddupiacz with the current settings."""
        return f'"{self.python_exec}" -m oddupiacz.{self.hook_kind.module_name} --config "{self.config_path}" "$@"'


@dataclass
class InstallationResult(InstallationSettings):
    """Result of hook installation, extends InstallationSettings with additional info."""

    dir_created: bool


@dataclass
class UninstallationResult:
    """Result of hook uninstallation."""

    hook_removed: bool
    config_unset: bool
