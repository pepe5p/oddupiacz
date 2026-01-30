"""
Unit tests for config.py module.
"""

from pathlib import Path

import pytest

from oddupiacz.config import CannotLoadConfigError, Config, load_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_from_valid_config(self, tmp_path: Path) -> None:
        """Test loading from a valid YAML config."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
hooks_dir: /tmp/.githooks_global
forbidden_phrases:
  - "TODO"
  - "FIXME"
  - "console.log"
exclude_paths:
  - "vendor/"
  - "node_modules/"
""")

        config = load_config(config_file)
        assert config.forbidden_phrases == ["TODO", "FIXME", "console.log"]
        assert config.exclude_paths == ["vendor/", "node_modules/"]

    def test_load_from_nonexistent_config_raises_error(self, tmp_path: Path) -> None:
        """Test that nonexistent config raises error."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        error_msg = str(exc_info.value)
        assert "Config file not found" in error_msg

    def test_load_from_empty_config_raises_error(self, tmp_path: Path) -> None:
        """Test that empty config raises error."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        error_msg = str(exc_info.value)
        assert "Config file is empty" in error_msg

    def test_load_config_without_forbidden_phrases_raises_error(self, tmp_path: Path) -> None:
        """Test that config without forbidden_phrases key raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("hooks_dir: /tmp/.githooks_global\nother_key: value")

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        error_msg = str(exc_info.value)
        assert "'forbidden_phrases'" in error_msg

    def test_invalid_yaml_raises_error(self, tmp_path: Path) -> None:
        """Test that invalid YAML syntax raises error."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("forbidden_phrases:\n  - TODO\n  invalid: - syntax")

        with pytest.raises(CannotLoadConfigError):
            load_config(config_file)

    def test_non_dict_yaml_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dictionary YAML raises error."""
        config_file = tmp_path / "list.yaml"
        config_file.write_text("- item1\n- item2")

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        assert "Config must be a YAML dictionary" in str(exc_info.value)

    def test_non_list_forbidden_phrases_raises_error(self, tmp_path: Path) -> None:
        """Test that non-list forbidden_phrases raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("hooks_dir: /tmp/.githooks_global\nforbidden_phrases: not_a_list")

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        assert "'forbidden_phrases' must be a list" in str(exc_info.value)

    def test_empty_forbidden_phrases_raises_error(self, tmp_path: Path) -> None:
        """Test that empty forbidden_phrases list raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("hooks_dir: /tmp/.githooks_global\nforbidden_phrases: []")

        with pytest.raises(CannotLoadConfigError) as exc_info:
            load_config(config_file)

        assert "'forbidden_phrases' list cannot be empty" in str(exc_info.value)

    def test_config_with_optional_fields(self, tmp_path: Path) -> None:
        """Test config with only required forbidden_phrases field."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
hooks_dir: /tmp/.githooks_global
forbidden_phrases:
  - "TODO"
""")

        config = load_config(config_file)
        assert config.forbidden_phrases == ["TODO"]
        assert config.exclude_paths == []
        assert config.exclude_files == []
        assert config.exclude_extensions == []
        assert config.exclude_repos == []


class TestConfig:
    """Tests for Config dataclass."""

    def test_config_with_all_fields(self) -> None:
        """Test Config with all fields."""
        config = Config(
            hooks_dir=Path("/tmp/.githooks_global"),  # noqa: S108
            forbidden_phrases=["TODO", "FIXME"],
            exclude_paths=["vendor/"],
            exclude_files=["test.py"],
            exclude_extensions=[".log"],
            exclude_repos=["oddupiacz"],
        )
        assert config.forbidden_phrases == ["TODO", "FIXME"]
        assert config.exclude_paths == ["vendor/"]
        assert config.exclude_files == ["test.py"]
        assert config.exclude_extensions == [".log"]
        assert config.exclude_repos == ["oddupiacz"]
