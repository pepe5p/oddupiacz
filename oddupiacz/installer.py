"""
Hook installation and management utilities.
"""

import stat
from pathlib import Path

from .config_io import create_hook_path
from .git_utils import configure_git_hooks_path, unset_git_hooks_path
from .models import InstallationResult, InstallationSettings, UninstallationResult


def generate_shim_content(settings: InstallationSettings) -> str:
    """
    Generate the shell script content for the pre-commit hook shim.

    Args:
        settings: InstallationSettings object

    Returns:
        Shell script content as a string
    """
    return f"""#!/bin/sh
# This is a generated shim by Oddupiacz.
# It runs git diff and pipes the output to the main script.

export PYTHONPATH="{settings.oddupiacz_path}:$PYTHONPATH"
git diff --cached --unified=0 --no-color | {settings.create_exec_command()}
EXIT_CODE=$?

exit $EXIT_CODE
"""


def create_hook_directory(hooks_dir: Path) -> bool:
    """
    Create the hooks directory if it doesn't exist.

    Args:
        hooks_dir: Path to the hooks directory

    Returns:
        True if directory was created, False if it already existed
    """
    if hooks_dir.exists():
        return False

    hooks_dir.mkdir(parents=True, exist_ok=True)
    return True


def write_executable_hook(hook_path: Path, content: str) -> None:
    """
    Write hook content to file and make it executable.

    Args:
        hook_path: Path where the hook should be written
        content: Content of the hook script
    """
    hook_path.write_text(content)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)


def remove_hook_file(hook_path: Path) -> bool:
    """
    Remove the hook file if it exists.

    Args:
        hook_path: Path to the hook file

    Returns:
        True if file was removed, False if it didn't exist
    """
    if not hook_path.exists():
        return False

    hook_path.unlink()
    return True


def install_hook(settings: InstallationSettings) -> InstallationResult:
    """
    Install Oddupiacz as a global git pre-commit hook.

    Args:
        settings: InstallationSettings object

    Returns:
        InstallationResult with installation details

    Raises:
        FileNotFoundError: If main script is not found
        subprocess.CalledProcessError: If git config fails
    """
    dir_created = create_hook_directory(hooks_dir=settings.hooks_dir)
    shim_content = generate_shim_content(settings=settings)
    hook_path = create_hook_path(hooks_dir=settings.hooks_dir)
    write_executable_hook(hook_path=hook_path, content=shim_content)
    configure_git_hooks_path(hooks_dir=settings.hooks_dir)

    return InstallationResult(
        hooks_dir=settings.hooks_dir,
        oddupiacz_path=settings.oddupiacz_path,
        config_path=settings.config_path,
        python_exec=settings.python_exec,
        dir_created=dir_created,
    )


def uninstall_hook(hook_path: Path) -> UninstallationResult:
    """
    Uninstall Oddupiacz global git hooks.

    Args:
        hook_path: Path to the hooks directory

    Returns:
        UninstallationResult with uninstallation details
    """
    hook_removed = remove_hook_file(hook_path=hook_path)
    config_unset = unset_git_hooks_path()
    return UninstallationResult(hook_removed=hook_removed, config_unset=config_unset)
