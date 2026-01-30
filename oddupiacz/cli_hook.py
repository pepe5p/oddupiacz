#!/usr/bin/env python3
"""
Pre-commit hook CLI to check for forbidden phrases in git diffs.
"""

import sys
from pathlib import Path
from typing import Annotated

import typer

from .checker import parse_diff_for_violations, Violation
from .config import CannotLoadConfigError, load_config
from .git_utils import find_local_hook_path, get_git_diff, get_repo_name, run_local_hook_if_exists

app = typer.Typer(add_completion=False)


def print_error_with_help(message: str) -> None:
    """
    Print error message with instructions to uninstall or bypass.

    Args:
        message: The error message to display
    """
    typer.secho(f"[ERROR] {message}", fg=typer.colors.RED, err=True)
    typer.secho("[INFO] To uninstall: ./uninstall", fg=typer.colors.YELLOW, err=True)
    typer.secho("[INFO] To bypass: git commit --no-verify", fg=typer.colors.YELLOW, err=True)


@app.command()
def main(
    config_path: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to config.yaml with forbidden phrases"),
    ] = None,
) -> None:
    """
    Check git diff for forbidden phrases.

    This command reads git diff output from stdin and checks for forbidden phrases.
    Typically called by the pre-commit hook shim.
    """
    if config_path is None:
        print_error_with_help("No config file specified")
        typer.secho(
            "[INFO] Oddupiacz requires a config file with 'forbidden_phrases'", fg=typer.colors.YELLOW, err=True
        )
        sys.exit(1)

    diff_input = sys.stdin.read()

    if not diff_input:
        try:
            diff_input = get_git_diff(cached=True)
        except Exception:
            sys.exit(0)

    try:
        config = load_config(config_path)
    except CannotLoadConfigError as e:
        print_error_with_help(str(e))
        sys.exit(1)

    repo_name = get_repo_name()
    if repo_name and repo_name in config.exclude_repos:
        sys.exit(0)

    violations = parse_diff_for_violations(diff_input, config)

    if violations:
        error_message = format_violation_message(violations)
        typer.secho(error_message, fg=typer.colors.RED, err=True)
        sys.exit(1)

    hook_path = find_local_hook_path()
    if not run_local_hook_if_exists(hook_path, sys.argv[1:]):
        sys.exit(1)

    sys.exit(0)


def format_violation_message(violations: list[Violation]) -> str:
    """
    Format violation messages for display.

    Args:
        violations: List of Violation objects

    Returns:
        Formatted error message string (plain text, styling applied at display time)
    """
    lines = []
    for violation in violations:
        lines.append(f"[BLOCKED] Forbidden phrase found: '{violation.phrase}'")
        lines.append(f"  File: {violation.file}")
        lines.append(f"  Line: {violation.line}")
        lines.append("-" * 40)

    if violations:
        lines.append("Commit aborted.")

    return "\n".join(lines)


if __name__ == "__main__":
    app()
