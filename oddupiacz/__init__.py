"""
Oddupiacz - A global pre-commit hook to check for forbidden words in git changes.
"""

__version__ = "0.0.0"

from .checker import parse_diff_for_violations
from .config import CannotLoadConfigError, Config, load_config
from .formatters import format_violation_message
from .git_utils import find_local_hook_path, get_git_diff, get_repo_name, run_local_hook_if_exists
from .installer import install_hook, uninstall_hook
from .models import InstallationResult, InstallationSettings, UninstallationResult, Violation

__all__ = [
    "parse_diff_for_violations",
    "Violation",
    "load_config",
    "Config",
    "CannotLoadConfigError",
    "get_git_diff",
    "get_repo_name",
    "find_local_hook_path",
    "run_local_hook_if_exists",
    "install_hook",
    "uninstall_hook",
    "InstallationSettings",
    "InstallationResult",
    "UninstallationResult",
    "format_violation_message",
]
