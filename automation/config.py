from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping
from urllib.parse import urljoin


DEFAULT_BASE_URL = "https://healyourrootswellness.com"
DELETE_CONFIRMATION = "I_UNDERSTAND_THIS_MAY_DELETE_DATA"


def load_env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        key, separator, value = line.partition("=")
        if separator and key.strip():
            values[key.strip()] = _unquote(value.strip())
    return values


def parse_headers(raw_headers: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_header in raw_headers.split(";"):
        key, separator, value = raw_header.partition("=")
        if separator and key.strip():
            headers[key.strip()] = value.strip()
    return headers


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _first_non_blank(*values: str | None) -> str:
    return next((value.strip() for value in values if value and value.strip()), "")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() == "true"


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value or "")
    except ValueError:
        return default


def normalize_browser(value: str) -> str:
    browser = value.strip().lower()
    if browser == "chrome":
        return "chromium"
    if browser not in {"chromium", "firefox"}:
        raise ValueError(f"Unsupported browser '{value}'. Use chromium or firefox.")
    return browser


def normalize_site_base(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if normalized.lower().endswith("/api"):
        normalized = normalized[:-4]
    return normalized


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_base_url: str
    browser: str
    headless: bool
    default_timeout_ms: int
    expect_timeout_ms: int
    member_test_password: str | None
    member_test_email_domain: str
    member_auth_token: str | None
    member_auth_cookie: str | None
    member_api_headers: Mapping[str, str]
    run_mutating_api_tests: bool
    delete_investigation_enabled: bool
    delete_confirmation: str | None
    delete_candidate: str | None
    delete_account_id: str | None

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        env_file: Path = Path(".env"),
    ) -> "Settings":
        local_values = load_env_values(env_file)
        effective = dict(local_values)
        effective.update(os.environ if environ is None else environ)
        base_url = _first_non_blank(effective.get("BASE_URL"), DEFAULT_BASE_URL)
        api_base_url = normalize_site_base(
            _first_non_blank(effective.get("API_BASE_URL"), effective.get("API_URL"), base_url)
        )
        browser = normalize_browser(_first_non_blank(effective.get("BROWSER"), "chromium"))
        return cls(
            base_url=base_url.rstrip("/"),
            api_base_url=api_base_url,
            browser=browser,
            headless=_as_bool(effective.get("HEADLESS"), True),
            default_timeout_ms=_as_int(effective.get("DEFAULT_TIMEOUT_MS"), 90_000),
            expect_timeout_ms=_as_int(effective.get("EXPECT_TIMEOUT_MS"), 10_000),
            member_test_password=_first_non_blank(effective.get("MEMBER_TEST_PASSWORD")) or None,
            member_test_email_domain=_first_non_blank(
                effective.get("MEMBER_TEST_EMAIL_DOMAIN"), "example.com"
            ).lower(),
            member_auth_token=_first_non_blank(
                effective.get("MEMBER_AUTH_TOKEN"), effective.get("AUTH_TOKEN")
            ) or None,
            member_auth_cookie=_first_non_blank(
                effective.get("MEMBER_AUTH_COOKIE"), effective.get("AUTH_COOKIE")
            ) or None,
            member_api_headers=parse_headers(
                _first_non_blank(effective.get("MEMBER_API_HEADERS"), effective.get("API_HEADERS"))
            ),
            run_mutating_api_tests=_as_bool(effective.get("RUN_MUTATING_API_TESTS")),
            delete_investigation_enabled=_as_bool(
                effective.get("MEMBER_DELETE_INVESTIGATION_ENABLED")
            ),
            delete_confirmation=_first_non_blank(
                effective.get("MEMBER_DELETE_CONFIRMATION")
            ) or None,
            delete_candidate=_first_non_blank(effective.get("MEMBER_DELETE_CANDIDATE")).upper() or None,
            delete_account_id=_first_non_blank(effective.get("MEMBER_DELETE_ACCOUNT_ID")) or None,
        )

    def absolute_url(self, path: str) -> str:
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    @property
    def delete_confirmation_accepted(self) -> bool:
        return self.delete_confirmation == DELETE_CONFIRMATION
