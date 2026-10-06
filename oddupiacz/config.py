"""
Configuration management for Oddupiacz.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PROTECTED_BRANCHES = ["main", "master"]


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


@dataclass
class MainblockerConfig:
    """Settings for the pre-push confirmation hook."""

    hooks_dir: Path
    protected_branches: list[str]
    exclude_repos: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert MainblockerConfig to dictionary for YAML serialization."""
        data = asdict(self)
        data["hooks_dir"] = self.hooks_dir.as_posix()
        return data


def create_default_mainblocker_config(hooks_dir: Path | None = None) -> MainblockerConfig:
    """
    Create a default mainblocker config.

    Args:
        hooks_dir: Hooks directory to use. Defaults to the global hooks directory.
            Pass the pre-commit config's directory so both hooks stay together.

    Returns:
        MainblockerConfig protecting main and master
    """
    return MainblockerConfig(
        hooks_dir=hooks_dir if hooks_dir is not None else create_default_hooks_dir_path(),
        protected_branches=list(DEFAULT_PROTECTED_BRANCHES),
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


def _read_config_data(config_path: Path) -> dict[str, Any]:
    """
    Read a config file into a dictionary.

    Args:
        config_path: Path to the YAML config file

    Returns:
        Parsed YAML mapping

    Raises:
        CannotLoadConfigError: If the file is missing, unreadable, empty, or not a mapping
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

    return data


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
    data = _read_config_data(config_path=config_path)

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


def load_mainblocker_config(config_path: Path) -> MainblockerConfig:
    """
    Load a mainblocker configuration from YAML.

    Args:
        config_path: Path to the YAML config file

    Returns:
        MainblockerConfig object with loaded values

    Raises:
        CannotLoadConfigError: If config file doesn't exist, has syntax errors,
                               or is missing required fields
    """
    data = _read_config_data(config_path=config_path)

    if "hooks_dir" not in data:
        raise CannotLoadConfigError("Config must contain 'hooks_dir'")

    if "protected_branches" not in data:
        raise CannotLoadConfigError("Config must contain 'protected_branches' key")

    if not isinstance(data["protected_branches"], list):
        raise CannotLoadConfigError("'protected_branches' must be a list")

    if not data["protected_branches"]:
        raise CannotLoadConfigError("'protected_branches' list cannot be empty")

    return MainblockerConfig(
        hooks_dir=Path(data["hooks_dir"]).expanduser().resolve(),
        protected_branches=data["protected_branches"],
        exclude_repos=data.get("exclude_repos", []),
    )
