"""
Configuration file I/O operations.
"""

from pathlib import Path

import yaml

from .config import Config, MainblockerConfig
from .models import HookKind

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
USER_CONFIG = CONFIGS_DIR / "user_config.yaml"
MAINBLOCKER_CONFIG = CONFIGS_DIR / "mainblocker_config.yaml"


def save_config(config: Config | MainblockerConfig, config_path: Path) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Config object to save
        config_path: Path where to save the config
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def create_hook_path(hooks_dir: Path, hook_kind: HookKind = HookKind.PRE_COMMIT) -> Path:
    """
    Get the full path to a global hook file.

    Args:
        hooks_dir: Path to the hooks directory
        hook_kind: Which hook file to point at

    Returns:
        Path to the hook file
    """
    return hooks_dir / hook_kind.value
