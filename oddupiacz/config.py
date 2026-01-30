"""
Configuration management for Oddupiacz.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    hooks_dir: Path
    forbidden_phrases: list[str]
    exclude_paths: list[str]
    exclude_files: list[str]
    exclude_extensions: list[str]
    exclude_repos: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert Config to dictionary for YAML serialization."""
        data = asdict(self)
        data["hooks_dir"] = self.hooks_dir.as_posix()
        return data


def create_default_config() -> Config:
    """Create a default Config object with empty forbidden phrases."""
    return Config(
        hooks_dir=create_default_hooks_dir_path(),
        forbidden_phrases=["dupa"],
        exclude_paths=[],
        exclude_files=[],
        exclude_extensions=[],
        exclude_repos=["oddupiacz"],
    )


def create_default_hooks_dir_path() -> Path:
    """Get the default hooks directory path."""
    return (Path.home() / ".githooks_global").expanduser().resolve()


class CannotLoadConfigError(Exception):
    """Custom exception for configuration loading errors."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__()
        self.message = message
        self.base_message = "Cannot load configuration"

    def __str__(self) -> str:
        if self.__cause__:
            return f"{self.base_message}: {self.__cause__}"
        else:
            return f"{self.base_message}: {self.message}"


def load_config(config_path: Path) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML config file

    Returns:
        Config object with loaded values

    Raises:
        CannotLoadConfigError: If config file doesn't exist, has syntax errors,
                               or is missing required fields
    """
    if not config_path.exists():
        raise CannotLoadConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise CannotLoadConfigError(f"Invalid YAML syntax in config file: {exc}") from exc
    except (IOError, OSError) as exc:
        raise CannotLoadConfigError(f"Cannot read config file: {exc}") from exc

    if data is None:
        raise CannotLoadConfigError("Config file is empty")

    if not isinstance(data, dict):
        raise CannotLoadConfigError("Config must be a YAML dictionary")

    if "hooks_dir" not in data:
        raise CannotLoadConfigError("Config must contain 'hooks_dir'")

    if "forbidden_phrases" not in data:
        raise CannotLoadConfigError("Config must contain 'forbidden_phrases' key")

    if not isinstance(data["forbidden_phrases"], list):
        raise CannotLoadConfigError("'forbidden_phrases' must be a list")

    if not data["forbidden_phrases"]:
        raise CannotLoadConfigError("'forbidden_phrases' list cannot be empty")

    return Config(
        hooks_dir=Path(data["hooks_dir"]).expanduser().resolve(),
        forbidden_phrases=data["forbidden_phrases"],
        exclude_paths=data.get("exclude_paths", []),
        exclude_files=data.get("exclude_files", []),
        exclude_extensions=data.get("exclude_extensions", []),
        exclude_repos=data.get("exclude_repos", []),
    )
