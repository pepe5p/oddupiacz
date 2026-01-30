"""
Git integration utilities.
"""

import os
import subprocess
from pathlib import Path


def get_repo_name() -> str | None:
    """
    Get the name of the current git repository.

    Returns:
        Repository name (directory name) or None if not in a git repo
    """
    try:
        repo_root = subprocess.check_output(  # noqa: S603
            ["git", "rev-parse", "--show-toplevel"],  # noqa: S607
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return Path(repo_root).name
    except subprocess.CalledProcessError:
        return None


def get_git_diff(cached: bool = True, unified: int = 0) -> str:
    """
    Get git diff output.

    Args:
        cached: If True, get staged changes; if False, get working directory changes
        unified: Number of context lines (0 to focus on changes only)

    Returns:
        Git diff output as string

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    cmd = ["git", "diff", f"--unified={unified}", "--no-color"]
    if cached:
        cmd.insert(2, "--cached")

    result = subprocess.run(  # noqa: S603
        cmd, capture_output=True, text=True, errors="replace", check=True
    )
    return result.stdout


def find_local_hook_path() -> Path | None:
    """
    Find the local pre-commit hook path for the current repository.

    Returns:
        Path to local pre-commit hook if it exists and is executable, None otherwise
    """
    try:
        git_common_dir = subprocess.check_output(  # noqa: S603
            ["git", "rev-parse", "--git-common-dir"],  # noqa: S607
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return None

    local_hook_path = Path(git_common_dir) / "hooks" / "pre-commit"

    if local_hook_path.exists() and os.access(local_hook_path, os.X_OK):
        return local_hook_path

    return None


def run_local_hook_if_exists(hook_path: Path | None, args: list[str]) -> bool:
    """
    Execute a local pre-commit hook if it exists.

    Args:
        hook_path: Path to the hook script
        args: Additional arguments to pass to the hook

    Returns:
        True if hook succeeded or doesn't exist, False if hook failed
    """
    if hook_path is None:
        return True

    result = subprocess.run([str(hook_path)] + args)  # noqa: S603
    return result.returncode == 0


def configure_git_hooks_path(hooks_dir: Path) -> None:
    """
    Configure Git to use the specified hooks directory globally.

    Args:
        hooks_dir: Path to the hooks directory

    Raises:
        subprocess.CalledProcessError: If git config command fails
    """
    subprocess.run(  # noqa: S603
        ["git", "config", "--global", "core.hooksPath", str(hooks_dir)],  # noqa: S607
        check=True,
        capture_output=True,
    )


def unset_git_hooks_path() -> bool:
    """
    Remove the global Git hooks path configuration.

    Returns:
        True if config was unset, False if it wasn't set
    """
    try:
        subprocess.run(  # noqa: S603
            ["git", "config", "--global", "--unset", "core.hooksPath"],  # noqa: S607
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
