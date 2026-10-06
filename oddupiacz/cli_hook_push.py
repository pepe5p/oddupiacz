#!/usr/bin/env python3
"""Blocks pushes to protected branches until the repository name is retyped."""

import sys
from pathlib import Path
from typing import Annotated

import typer

from .config import CannotLoadConfigError, load_mainblocker_config
from .git_utils import find_local_hook_path, get_repo_name, run_local_hook_if_exists
from .mainblocker import find_protected_refs, parse_push_refs
from .models import HookKind
from .ui import confirm_repo_name, NoTerminalError

app = typer.Typer(add_completion=False)


def print_error_with_help(message: str) -> None:
    """
    Print error message with instructions to uninstall or bypass.

    Args:
        message: The error message to display
    """
    typer.secho(f"[ERROR] {message}", fg=typer.colors.RED, err=True)
    typer.secho("[INFO] To uninstall: ./uninstall-mainblocker", fg=typer.colors.YELLOW, err=True)
    typer.secho("[INFO] To bypass: git push --no-verify", fg=typer.colors.YELLOW, err=True)


def chain_local_hook(stdin_text: str, remote_name: str, remote_url: str) -> None:
    """
    Run the repository-local pre-push hook, replaying the ref list git already sent.

    Args:
        stdin_text: Ref list captured from this process's stdin
        remote_name: Remote name git passed to the global hook
        remote_url: Remote URL git passed to the global hook
    """
    hook_path = find_local_hook_path(hook_name=HookKind.PRE_PUSH.value)
    if not run_local_hook_if_exists(
        hook_path=hook_path,
        args=[remote_name, remote_url],
        stdin_data=stdin_text,
    ):
        sys.exit(1)
    sys.exit(0)


@app.command()
def main(
    remote_name: Annotated[str, typer.Argument(help="Name of the remote being pushed to")],
    remote_url: Annotated[str, typer.Argument(help="URL of the remote being pushed to")],
    config_path: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to config.yaml"),
    ] = None,
) -> None:
    """
    Confirm pushes that update a protected branch.

    Git calls this with the remote name and URL, and writes one ref update per line to stdin.
    """
    if config_path is None:
        print_error_with_help("No config file specified")
        sys.exit(1)

    stdin_text = sys.stdin.read()

    try:
        config = load_mainblocker_config(config_path=config_path)
    except CannotLoadConfigError as exc:
        print_error_with_help(str(exc))
        sys.exit(1)

    repo_name = get_repo_name()
    if repo_name and repo_name in config.exclude_repos:
        chain_local_hook(stdin_text=stdin_text, remote_name=remote_name, remote_url=remote_url)

    protected = find_protected_refs(
        refs=parse_push_refs(stdin_text=stdin_text),
        protected_branches=config.protected_branches,
    )
    if not protected:
        chain_local_hook(stdin_text=stdin_text, remote_name=remote_name, remote_url=remote_url)

    if repo_name is None:
        print_error_with_help("Cannot determine repository name")
        sys.exit(1)

    try:
        confirmed = confirm_repo_name(repo_name=repo_name, branches=protected, remote_name=remote_name)
    except NoTerminalError:
        print_error_with_help(f"Refusing to push to {', '.join(protected)} without confirmation (no terminal).")
        sys.exit(1)

    if not confirmed:
        typer.secho("Push aborted.", fg=typer.colors.RED, err=True)
        sys.exit(1)

    chain_local_hook(stdin_text=stdin_text, remote_name=remote_name, remote_url=remote_url)


if __name__ == "__main__":
    app()
