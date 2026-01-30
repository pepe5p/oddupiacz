"""
Configuration file I/O operations.
"""

from pathlib import Path

import yaml

from .config import Config

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
USER_CONFIG = CONFIGS_DIR / "user_config.yaml"


def save_config(config: Config, config_path: Path) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Config object to save
        config_path: Path where to save the config
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def create_hook_path(hooks_dir: Path) -> Path:
    """
    Get the full path to the pre-commit hook file.

    Args:
        hooks_dir: Path to the hooks directory

    Returns:
        Path to the pre-commit hook file
    """
    return hooks_dir / "pre-commit"
