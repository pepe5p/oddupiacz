"""
Interactive UI utilities for configuration and installation.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterator, TextIO

import typer

from .config import (
    CannotLoadConfigError,
    Config,
    create_default_config,
    create_default_hooks_dir_path,
    create_default_mainblocker_config,
    load_config,
    load_mainblocker_config,
    MainblockerConfig,
)
from .config_io import MAINBLOCKER_CONFIG, save_config, USER_CONFIG
from .mainblocker import is_confirmed
from .models import HookKind, InstallationSettings

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
EXAMPLE_CONFIG = CONFIGS_DIR / "example.yaml"
MAINBLOCKER_EXAMPLE = CONFIGS_DIR / "mainblocker.example.yaml"


def _collect_items(section_name: str, examples: str | None = None) -> list[str]:
    """
    Helper function to collect a list of items interactively.

    Args:
        section_name: Name of the section (e.g., "Exclude Paths")
        examples: Optional examples to show (e.g., "vendor/, node_modules/")

    Returns:
        List of collected items
    """
    typer.echo()
    typer.secho(f"{section_name}:", fg=typer.colors.CYAN, bold=True)
    if examples:
        typer.echo(f"Examples: {examples}")
    typer.echo()

    items = []
    while True:
        item = typer.prompt("Add item (or press Enter to finish)", default="", show_default=False)
        if not item:
            break
        items.append(item)
        typer.secho(f"  ✓ Added: {item}", fg=typer.colors.GREEN)

    typer.echo()
    return items


def create_config_interactive() -> tuple[Config, Path]:
    """
    Create a config file interactively.

    Returns:
        Config object and path to the created user_config.yaml
    """
    typer.echo()
    typer.secho("Creating custom configuration...", fg=typer.colors.CYAN)
    typer.echo()

    default_hooks_dir = create_default_hooks_dir_path()
    typer.echo(f"Git hooks directory: {default_hooks_dir}")

    if typer.confirm("Use this directory?", default=True):
        hooks_dir = default_hooks_dir
    else:
        hooks_dir_str = typer.prompt("Enter hooks directory path")
        hooks_dir = Path(hooks_dir_str).expanduser().resolve()

    # Collect forbidden phrases
    typer.secho("Forbidden Phrases:", fg=typer.colors.CYAN, bold=True)
    typer.echo("Enter phrases to block in commits")

    forbidden_phrases = []
    typer.echo()
    while True:
        phrase = typer.prompt(
            "Add forbidden phrase (or press Enter to finish this section)", default="", show_default=False
        )
        if not phrase:
            break
        forbidden_phrases.append(phrase)
        typer.secho(f"  ✓ Added: {phrase}", fg=typer.colors.GREEN)

    if not forbidden_phrases:
        typer.secho("No phrases added. Using defaults: TODO, FIXME, temp_fix", fg=typer.colors.YELLOW)
        forbidden_phrases = ["TODO", "FIXME", "temp_fix"]

    typer.echo()

    exclude_paths = []
    if typer.confirm("Do you want to exclude specific paths?", default=False):
        exclude_paths = _collect_items("Exclude Paths", "vendor/, node_modules/, .venv/")

    exclude_files = []
    if typer.confirm("Do you want to exclude specific files?", default=False):
        exclude_files = _collect_items("Exclude Files", "package-lock.json, yarn.lock")

    exclude_extensions = []
    if typer.confirm("Do you want to exclude specific file extensions?", default=False):
        exclude_extensions = _collect_items("Exclude Extensions", ".min.js, .log, .pyc")

    exclude_repos = []
    if typer.confirm("Do you want to exclude specific repositories?", default=False):
        exclude_repos = _collect_items("Exclude Repos", "my-personal-notes, scratch")

    config = Config(
        hooks_dir=hooks_dir,
        forbidden_phrases=forbidden_phrases,
        exclude_paths=exclude_paths,
        exclude_files=exclude_files,
        exclude_extensions=exclude_extensions,
        exclude_repos=exclude_repos,
    )
    save_config(config=config, config_path=USER_CONFIG)

    typer.secho(f"✓ Config created: {USER_CONFIG}", fg=typer.colors.GREEN)
    typer.echo()
    typer.echo(f"You can edit this file later. See {EXAMPLE_CONFIG} for all available options.")

    return config, USER_CONFIG.expanduser().resolve()


def get_config_path_interactive() -> tuple[Config, Path]:
    """
    Interactively prompt user for config path.

    Returns:
        Config object and path to the config file
    """
    typer.echo()
    typer.secho("📝 Configuration Setup", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    choices = {
        "1": "Use default configuration (dupa)",
        "2": "Provide path to existing config file",
        "3": "Create config interactively",
    }

    for key, description in choices.items():
        typer.echo(f"  {key}. {description}")

    typer.echo()
    choice = typer.prompt("Choose an option", type=str, default="1")

    if choice == "1":
        typer.secho("✓ Using default config", fg=typer.colors.GREEN)
        config = create_default_config()
        config_path = USER_CONFIG.expanduser().resolve()
        save_config(config=config, config_path=config_path)
        return config, config_path

    elif choice == "2":
        config_path_str = typer.prompt("Enter path to config file")
        config_path = Path(config_path_str).expanduser().resolve()

        try:
            config = load_config(config_path=config_path)
        except CannotLoadConfigError:
            typer.secho(f"Error: Cannot load config from {config_path}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

        typer.secho(f"✓ Using config: {config_path}", fg=typer.colors.GREEN)
        return config, config_path

    elif choice == "3":
        return create_config_interactive()

    else:
        typer.secho("Error: Invalid choice", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def _user_config_hooks_dir() -> Path | None:
    """
    Return the hooks directory from the pre-commit config, if that file loads.

    Returns:
        Hooks directory from user_config.yaml, or None when it is missing or invalid
    """
    if not USER_CONFIG.exists():
        return None
    try:
        return load_config(config_path=USER_CONFIG).hooks_dir
    except CannotLoadConfigError:
        return None


def create_mainblocker_config_interactive() -> tuple[MainblockerConfig, Path]:
    """
    Create a mainblocker config file interactively.

    Returns:
        MainblockerConfig object and path to the created mainblocker_config.yaml
    """
    typer.echo()
    typer.secho("Creating mainblocker configuration...", fg=typer.colors.CYAN)
    typer.echo()

    existing_hooks_dir = _user_config_hooks_dir()
    default_hooks_dir = existing_hooks_dir if existing_hooks_dir is not None else create_default_hooks_dir_path()
    typer.echo(f"Git hooks directory: {default_hooks_dir}")
    if existing_hooks_dir is not None:
        typer.echo("Taken from the pre-commit config so both hooks stay in the same directory.")

    if typer.confirm("Use this directory?", default=True):
        hooks_dir = default_hooks_dir
    else:
        hooks_dir_str = typer.prompt("Enter hooks directory path")
        hooks_dir = Path(hooks_dir_str).expanduser().resolve()

    typer.secho("Protected Branches:", fg=typer.colors.CYAN, bold=True)
    typer.echo("Enter branch names that require confirmation before push")

    protected_branches = []
    typer.echo()
    while True:
        branch = typer.prompt(
            "Add protected branch (or press Enter to finish this section)", default="", show_default=False
        )
        if not branch:
            break
        protected_branches.append(branch)
        typer.secho(f"  ✓ Added: {branch}", fg=typer.colors.GREEN)

    if not protected_branches:
        typer.secho("No branches added. Using defaults: main, master", fg=typer.colors.YELLOW)
        protected_branches = ["main", "master"]

    typer.echo()

    exclude_repos = []
    if typer.confirm("Do you want to exclude specific repositories?", default=False):
        exclude_repos = _collect_items("Exclude Repos", "my-personal-notes, scratch")

    config = MainblockerConfig(
        hooks_dir=hooks_dir,
        protected_branches=protected_branches,
        exclude_repos=exclude_repos,
    )
    save_config(config=config, config_path=MAINBLOCKER_CONFIG)

    typer.secho(f"✓ Config created: {MAINBLOCKER_CONFIG}", fg=typer.colors.GREEN)
    typer.echo()
    typer.echo(f"You can edit this file later. See {MAINBLOCKER_EXAMPLE} for options.")

    return config, MAINBLOCKER_CONFIG.expanduser().resolve()


def get_mainblocker_config_path_interactive() -> tuple[MainblockerConfig, Path]:
    """
    Interactively prompt user for a mainblocker config path.

    Returns:
        MainblockerConfig object and path to the config file
    """
    typer.echo()
    typer.secho("📝 mainblocker Configuration Setup", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    choices = {
        "1": "Use default configuration (main, master)",
        "2": "Provide path to existing config file",
        "3": "Create config interactively",
    }

    for key, description in choices.items():
        typer.echo(f"  {key}. {description}")

    typer.echo()
    choice = typer.prompt("Choose an option", type=str, default="1")

    if choice == "1":
        typer.secho("✓ Using default config", fg=typer.colors.GREEN)
        config = create_default_mainblocker_config(hooks_dir=_user_config_hooks_dir())
        config_path = MAINBLOCKER_CONFIG.expanduser().resolve()
        save_config(config=config, config_path=config_path)
        return config, config_path

    elif choice == "2":
        config_path_str = typer.prompt("Enter path to config file")
        config_path = Path(config_path_str).expanduser().resolve()

        try:
            config = load_mainblocker_config(config_path=config_path)
        except CannotLoadConfigError:
            typer.secho(f"Error: Cannot load config from {config_path}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

        typer.secho(f"✓ Using config: {config_path}", fg=typer.colors.GREEN)
        return config, config_path

    elif choice == "3":
        return create_mainblocker_config_interactive()

    else:
        typer.secho("Error: Invalid choice", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def _warn_if_hooks_dir_differs(hooks_dir: Path) -> None:
    """
    Warn when mainblocker would point core.hooksPath somewhere else than the pre-commit hook.

    Args:
        hooks_dir: Hooks directory chosen for mainblocker
    """
    user_hooks_dir = _user_config_hooks_dir()
    if user_hooks_dir is not None and user_hooks_dir != hooks_dir:
        typer.secho(
            f"Warning: hooks directory differs from the pre-commit config ({user_hooks_dir}). "
            "Only the directory set last is active.",
            fg=typer.colors.YELLOW,
        )


class NoTerminalError(Exception):
    """No controlling terminal is available to confirm the push."""


class _PromptTerminal:
    """A terminal opened separately for reading and writing."""

    def __init__(self, reader: TextIO, writer: TextIO) -> None:
        self._reader = reader
        self._writer = writer

    def __enter__(self) -> "_PromptTerminal":
        return self

    def __exit__(self, *args: object) -> None:
        self._reader.close()
        self._writer.close()

    def write(self, text: str) -> None:
        self._writer.write(text)

    def flush(self) -> None:
        self._writer.flush()

    def readline(self) -> str:
        return self._reader.readline()


_MAX_ANCESTORS = 20
_NO_TTY = frozenset({"??", "?"})


def _find_ancestor_tty() -> Path | None:
    """
    Return the terminal device of the nearest ancestor process that has one.

    git push can start a hook without a controlling terminal and with piped
    output. The shell that launched git still owns the terminal.
    """
    pid = os.getppid()
    for _ in range(_MAX_ANCESTORS):
        if pid <= 1:
            return None
        try:
            fields = subprocess.check_output(  # noqa: S603
                ["ps", "-o", "ppid=,tty=", "-p", str(pid)],  # noqa: S607
                text=True,
                stderr=subprocess.DEVNULL,
            ).split()
        except (subprocess.CalledProcessError, OSError):
            return None
        if len(fields) != 2:
            return None
        parent, tty = fields
        if tty not in _NO_TTY:
            return Path("/dev") / tty
        try:
            pid = int(parent)
        except ValueError:
            return None
    return None


def _terminal_candidates() -> Iterator[Path]:
    yield Path("/dev/tty")
    for stream in (sys.stderr, sys.stdout):
        try:
            if stream is not None and stream.isatty():
                yield Path(os.ttyname(stream.fileno()))
        except OSError:
            continue
    ancestor = _find_ancestor_tty()
    if ancestor is not None:
        yield ancestor


def _open_terminal() -> _PromptTerminal:
    """
    Open a terminal the user can type into.

    A read-write open fails because Python seeks the stream and a terminal
    is not seekable. The read end and the write end are opened separately.

    When the hook itself has no terminal, the device is taken from an
    ancestor process.
    """
    for path in _terminal_candidates():
        try:
            reader = open(path, "r", encoding="utf-8", buffering=1)  # noqa: SIM115
        except OSError:
            continue
        try:
            writer = open(path, "w", encoding="utf-8", buffering=1)  # noqa: SIM115
        except OSError:
            reader.close()
            continue
        return _PromptTerminal(reader=reader, writer=writer)
    raise NoTerminalError()


def confirm_repo_name(repo_name: str, *, branches: list[str], remote_name: str) -> bool:
    """
    Ask on the controlling terminal whether a protected push should proceed.

    Args:
        repo_name: Repository name the user must retype
        branches: Protected branch names included in this push
        remote_name: Remote the push targets

    Returns:
        True when the typed name matches the repository name

    Raises:
        NoTerminalError: When no terminal can be opened
    """
    branch_list = ", ".join(branches)
    prompt = f"Pushing to {branch_list} on {remote_name}.\nType the repo name ({repo_name}) to confirm: "
    tty = _open_terminal()

    with tty:
        tty.write(prompt)
        tty.flush()
        answer = tty.readline()

    return is_confirmed(answer=answer.rstrip("\r\n"), repo_name=repo_name)


def prompt_installation_settings(hook_kind: HookKind = HookKind.PRE_COMMIT) -> InstallationSettings:
    """
    Prompt user for all installation settings with defaults.

    Args:
        hook_kind: Which global hook this installation writes

    Returns:
        InstallationSettings with hooks_dir, config_path, and python_exec
    """
    typer.echo()
    title = "mainblocker Installation" if hook_kind is HookKind.PRE_PUSH else "Oddupiacz Installation"
    typer.secho(f"🚀 {title}", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    default_oddupiacz_path = Path(__file__).parent.parent.expanduser().resolve()
    typer.echo(f"Oddupiacz path: {default_oddupiacz_path}")

    if typer.confirm("Use this path? (overriding not recommended)", default=True):
        oddupiacz_path = default_oddupiacz_path
    else:
        oddupiacz_path_str = typer.prompt("Enter Oddupiacz path")
        oddupiacz_path = Path(oddupiacz_path_str).expanduser().resolve()

    config: Config | MainblockerConfig
    config_path: Path
    if hook_kind is HookKind.PRE_PUSH:
        config, config_path = get_mainblocker_config_path_interactive()
        _warn_if_hooks_dir_differs(hooks_dir=config.hooks_dir)
    else:
        config, config_path = get_config_path_interactive()

    default_python = sys.executable
    typer.echo(f"Python executable: {default_python}")

    if typer.confirm("Use this Python?", default=True):
        python_exec = default_python
    else:
        python_exec = typer.prompt("Enter Python executable path")

    typer.echo()
    typer.secho("📋 Installation Summary:", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"  Hooks directory: {config.hooks_dir}")
    typer.echo(f"  Oddupiacz path: {oddupiacz_path}")
    typer.echo(f"  Config file: {config_path}")
    typer.echo(f"  Python: {python_exec}")
    typer.echo()

    if not typer.confirm("Proceed with installation?", default=True):
        typer.secho("Installation cancelled.", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    return InstallationSettings(
        hooks_dir=config.hooks_dir,
        oddupiacz_path=oddupiacz_path,
        config_path=config_path,
        python_exec=python_exec,
        hook_kind=hook_kind,
    )


def prompt_config_path() -> Path:
    """
    Prompt user for config path.

    Returns:
        Path to the config file
    """
    default_user_config_path = USER_CONFIG.expanduser().resolve()
    typer.echo()
    typer.secho("📝 Configuration File Selection", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"Default config path: {default_user_config_path}")
    if typer.confirm("Use this config path?", default=True):
        return default_user_config_path
    else:
        config_path_str = typer.prompt("Enter config file path")
        return Path(config_path_str).expanduser().resolve()


def prompt_mainblocker_config_path() -> Path:
    """
    Prompt user for the mainblocker config path.

    Returns:
        Path to the mainblocker config file
    """
    default_config_path = MAINBLOCKER_CONFIG.expanduser().resolve()
    typer.echo()
    typer.secho("📝 mainblocker Configuration File Selection", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"Default config path: {default_config_path}")
    if typer.confirm("Use this config path?", default=True):
        return default_config_path
    else:
        config_path_str = typer.prompt("Enter config file path")
        return Path(config_path_str).expanduser().resolve()
