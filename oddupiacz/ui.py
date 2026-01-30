"""
Interactive UI utilities for configuration and installation.
"""

import sys
from pathlib import Path

import typer

from .config import CannotLoadConfigError, Config, create_default_config, create_default_hooks_dir_path, load_config
from .config_io import save_config, USER_CONFIG
from .models import InstallationSettings

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
EXAMPLE_CONFIG = CONFIGS_DIR / "example.yaml"


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


def prompt_installation_settings() -> InstallationSettings:
    """
    Prompt user for all installation settings with defaults.

    Returns:
        InstallationSettings with hooks_dir, config_path, and python_exec
    """
    typer.echo()
    typer.secho("🚀 Oddupiacz Installation", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    default_oddupiacz_path = Path(__file__).parent.parent.expanduser().resolve()
    typer.echo(f"Oddupiacz path: {default_oddupiacz_path}")

    if typer.confirm("Use this path? (overriding not recommended)", default=True):
        oddupiacz_path = default_oddupiacz_path
    else:
        oddupiacz_path_str = typer.prompt("Enter Oddupiacz path")
        oddupiacz_path = Path(oddupiacz_path_str).expanduser().resolve()

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
