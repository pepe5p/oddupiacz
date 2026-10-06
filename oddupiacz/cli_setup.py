#!/usr/bin/env python3
"""
Setup CLI for installing and uninstalling Oddupiacz global git hooks.
"""

import subprocess
from pathlib import Path

import typer

from .config import Config, load_config, load_mainblocker_config, MainblockerConfig
from .config_io import create_hook_path
from .installer import install_hook, uninstall_hook
from .models import HookKind
from .ui import prompt_config_path, prompt_installation_settings, prompt_mainblocker_config_path

app = typer.Typer(help="Setup Oddupiacz global git hooks")


def _install(hook_kind: HookKind) -> None:
    label = "Oddupiacz" if hook_kind is HookKind.PRE_COMMIT else "mainblocker"
    bypass = "git commit --no-verify" if hook_kind is HookKind.PRE_COMMIT else "git push --no-verify"
    uninstall_cmd = "./uninstall" if hook_kind is HookKind.PRE_COMMIT else "./uninstall-mainblocker"

    try:
        settings = prompt_installation_settings(hook_kind=hook_kind)
        result = install_hook(settings=settings)

        typer.echo()
        typer.secho("✅ Installation successful!", fg=typer.colors.GREEN, bold=True)
        typer.echo()
        if result.dir_created:
            typer.secho(f"  Created hooks directory: {result.hooks_dir}", fg=typer.colors.GREEN)
        typer.echo(f"  Oddupiacz path: {result.oddupiacz_path}")
        typer.echo(f"  Hook installed at: {create_hook_path(hooks_dir=settings.hooks_dir, hook_kind=hook_kind)}")
        typer.echo(f"  Config file: {result.config_path}")
        typer.echo(f"  Python executable: {result.python_exec}")
        typer.echo()
        typer.secho(f"{label} is now active for all git repositories!", fg=typer.colors.GREEN)
        typer.echo()
        typer.echo(f"To bypass: {bypass}")
        typer.echo(f"To uninstall: {uninstall_cmd}")

    except FileNotFoundError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Error configuring git: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def _report_hooks_path(config_unset: bool, hooks_dir: Path) -> None:
    if config_unset:
        typer.secho("✓ Git global hooksPath configuration removed", fg=typer.colors.GREEN)
        return

    if any((hooks_dir / kind.value).exists() for kind in HookKind):
        typer.echo("Note: core.hooksPath left in place because another Oddupiacz hook is still installed")
        return

    typer.echo("Note: core.hooksPath was not set globally")


def _uninstall(hook_kind: HookKind) -> None:
    label = "Oddupiacz" if hook_kind is HookKind.PRE_COMMIT else "mainblocker"
    config: Config | MainblockerConfig
    if hook_kind is HookKind.PRE_PUSH:
        config_path = prompt_mainblocker_config_path()
        config = load_mainblocker_config(config_path=config_path)
    else:
        config_path = prompt_config_path()
        config = load_config(config_path=config_path)

    typer.echo()
    typer.echo(f"Uninstalling {label} from: {config.hooks_dir}")
    typer.echo()

    if not typer.confirm("Proceed with uninstall?", default=True):
        typer.secho("Uninstall cancelled.", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    hook_path = create_hook_path(hooks_dir=config.hooks_dir, hook_kind=hook_kind)
    result = uninstall_hook(hook_path=hook_path)

    if result.hook_removed:
        typer.secho(f"✓ Removed hook: {hook_path}", fg=typer.colors.GREEN)

    _report_hooks_path(config_unset=result.config_unset, hooks_dir=config.hooks_dir)

    typer.echo()
    typer.secho("✅ Uninstallation successful!", fg=typer.colors.GREEN, bold=True)


@app.command()
def install() -> None:
    """Install Oddupiacz as a global git pre-commit hook (interactive)."""
    _install(hook_kind=HookKind.PRE_COMMIT)


@app.command()
def install_mainblocker() -> None:
    """Install mainblocker as a global git pre-push hook (interactive)."""
    _install(hook_kind=HookKind.PRE_PUSH)


@app.command()
def uninstall() -> None:
    """Uninstall the Oddupiacz global pre-commit hook."""
    _uninstall(hook_kind=HookKind.PRE_COMMIT)


@app.command()
def uninstall_mainblocker() -> None:
    """Uninstall the mainblocker global pre-push hook."""
    _uninstall(hook_kind=HookKind.PRE_PUSH)


if __name__ == "__main__":
    app()
