from pathlib import Path

import pytest

from automation.config import Settings, load_env_values, normalize_browser, normalize_site_base, parse_headers


def test_environment_overrides_dotenv_without_mutating_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("BASE_URL=https://local.example\nHEADLESS=false\n", encoding="utf-8")
    settings = Settings.from_env(
        {"BASE_URL": "https://ci.example", "BROWSER": "firefox"}, env_file=env_file
    )
    assert settings.base_url == "https://ci.example"
    assert settings.browser == "firefox"
    assert not settings.headless
    assert env_file.read_text(encoding="utf-8") == "BASE_URL=https://local.example\nHEADLESS=false\n"


def test_load_env_values_supports_export_quotes_and_literal_values(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# private local settings\nexport TOKEN='literal $VALUE'\nEMPTY=\n", encoding="utf-8"
    )
    assert load_env_values(env_file) == {"TOKEN": "literal $VALUE", "EMPTY": ""}


def test_configuration_parsers_preserve_existing_compatibility() -> None:
    assert normalize_browser("chrome") == "chromium"
    assert normalize_browser("firefox") == "firefox"
    assert normalize_site_base("https://example.com/api/") == "https://example.com"
    assert parse_headers("X-Test-Run=true; X-Source=jenkins;invalid") == {
        "X-Test-Run": "true",
        "X-Source": "jenkins",
    }


def test_unsupported_browser_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="Unsupported browser"):
        normalize_browser("webkit")


def test_delete_investigation_requires_exact_confirmation() -> None:
    accepted = Settings.from_env(
        {
            "MEMBER_DELETE_CONFIRMATION": "I_UNDERSTAND_THIS_MAY_DELETE_DATA",
            "MEMBER_DELETE_INVESTIGATION_ENABLED": "true",
        },
        env_file=Path("does-not-exist"),
    )
    rejected = Settings.from_env(
        {"MEMBER_DELETE_CONFIRMATION": "yes"}, env_file=Path("does-not-exist")
    )
    assert accepted.delete_confirmation_accepted
    assert not rejected.delete_confirmation_accepted
