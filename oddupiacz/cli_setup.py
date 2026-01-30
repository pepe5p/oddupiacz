#!/usr/bin/env python3
"""
Setup CLI for installing/uninstalling Oddupiacz as a global git pre-commit hook.
"""

import subprocess

import typer

from .config import load_config
from .config_io import create_hook_path
from .installer import install_hook, uninstall_hook
from .ui import prompt_config_path, prompt_installation_settings

app = typer.Typer(help="Setup Oddupiacz global git hooks")


@app.command()
def install() -> None:
    """Install Oddupiacz as a global git pre-commit hook (interactive)."""

    try:
        settings = prompt_installation_settings()

        result = install_hook(settings=settings)

        typer.echo()
        typer.secho("✅ Installation successful!", fg=typer.colors.GREEN, bold=True)
        typer.echo()
        if result.dir_created:
            typer.secho(f"  Created hooks directory: {result.hooks_dir}", fg=typer.colors.GREEN)
        typer.echo(f"  Oddupiacz path: {result.oddupiacz_path}")
        typer.echo(f"  Hook installed at: {create_hook_path(hooks_dir=settings.hooks_dir)}")
        typer.echo(f"  Config file: {result.config_path}")
        typer.echo(f"  Python executable: {result.python_exec}")
        typer.echo()
        typer.secho("Oddupiacz is now active for all git repositories!", fg=typer.colors.GREEN)
        typer.echo()
        typer.echo("To bypass on specific commits: git commit --no-verify")
        typer.echo("To uninstall: ./uninstall")

    except FileNotFoundError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Error configuring git: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def uninstall() -> None:
    """Uninstall Oddupiacz global git hooks."""

    config_path = prompt_config_path()
    config = load_config(config_path=config_path)

    typer.echo()
    typer.echo(f"Uninstalling Oddupiacz from: {config.hooks_dir}")
    typer.echo()

    if not typer.confirm("Proceed with uninstall?", default=True):
        typer.secho("Uninstall cancelled.", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    hook_path = create_hook_path(hooks_dir=config.hooks_dir)
    result = uninstall_hook(hook_path=hook_path)

    if result.hook_removed:
        typer.secho(f"✓ Removed hook: {hook_path}", fg=typer.colors.GREEN)

    if result.config_unset:
        typer.secho("✓ Git global hooksPath configuration removed", fg=typer.colors.GREEN)
    else:
        typer.echo("Note: core.hooksPath was not set globally")

    typer.echo()
    typer.secho("✅ Uninstallation successful!", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    app()
