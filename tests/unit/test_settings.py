"""Unit tests for the config/settings module."""

from pathlib import Path

import pytest

from portfolio_manager.config.settings import (
    AppConfig,
    DatabaseConfig,
    SessionConfig,
    Settings,
    load_settings,
    save_settings,
)
from portfolio_manager.exceptions import ConfigError


class TestDatabaseConfig:
    def test_resolved_path_expands_tilde(self):
        cfg = DatabaseConfig(path="~/.portfolio_manager/portfolio.db")
        resolved = cfg.resolved_path
        assert not str(resolved).startswith("~")
        assert "portfolio_manager" in str(resolved)

    def test_resolved_path_memory(self):
        cfg = DatabaseConfig(path=":memory:")
        assert cfg.resolved_path == Path(":memory:")


class TestLoadSettings:
    def test_loads_defaults_when_no_file(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        settings = load_settings(cfg_file)
        assert settings.app.log_level == "INFO"
        assert settings.session.weekly_budget_hours == 12
        assert settings.session.default_duration_minutes == 90

    def test_creates_file_if_missing(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        load_settings(cfg_file)
        assert cfg_file.exists()

    def test_reads_custom_values(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        cfg_file.write_text(
            '[app]\nlog_level = "DEBUG"\ntheme = "dark"\n'
            "[session]\ndefault_duration_minutes = 60\nweekly_budget_hours = 8\n"
            '[database]\npath = "~/custom.db"\n',
            encoding="utf-8",
        )
        settings = load_settings(cfg_file)
        assert settings.app.log_level == "DEBUG"
        assert settings.app.theme == "dark"
        assert settings.session.default_duration_minutes == 60
        assert settings.session.weekly_budget_hours == 8

    def test_invalid_toml_raises_config_error(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        cfg_file.write_text("NOT VALID TOML ][", encoding="utf-8")
        with pytest.raises(ConfigError):
            load_settings(cfg_file)


class TestSaveSettings:
    def test_save_roundtrip(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        settings = Settings(
            app=AppConfig(log_level="DEBUG", theme="dark"),
            session=SessionConfig(default_duration_minutes=120, weekly_budget_hours=16),
            database=DatabaseConfig(path="~/test.db"),
        )
        save_settings(settings, cfg_file)
        loaded = load_settings(cfg_file)
        assert loaded.app.log_level == "DEBUG"
        assert loaded.app.theme == "dark"
        assert loaded.session.default_duration_minutes == 120
        assert loaded.session.weekly_budget_hours == 16
