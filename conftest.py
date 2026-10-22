from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

import pytest
from playwright.sync_api import expect

from automation.config import Settings


def pytest_configure(config: pytest.Config) -> None:
    configured_output = config.getoption("--output")
    if configured_output == "test-results":
        run_id = os.environ.get("TEST_RUN_ID") or datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S-%fZ"
        )
        config.option.output = str(Path("artifacts") / run_id / "playwright")


def pytest_sessionfinish(session: pytest.Session) -> None:
    allure_directory = session.config.getoption("--alluredir")
    if not allure_directory:
        return
    settings = Settings.from_env()
    metadata = "\n".join(
        (
            "Project=HealYourRootsWellness",
            f"BaseURL={session.config.getoption('--base-url') or settings.base_url}",
            f"ApiBaseURL={settings.api_base_url}",
            "Framework=Python Playwright",
            "Language=Python",
            "TestRunner=pytest",
            "",
        )
    )
    result_path = Path(allure_directory)
    result_path.mkdir(parents=True, exist_ok=True)
    (result_path / "environment.properties").write_text(metadata, encoding="utf-8")


@pytest.fixture(scope="session")
def settings() -> Settings:
    configured = Settings.from_env()
    expect.set_options(timeout=configured.expect_timeout_ms)
    return configured


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config, settings: Settings) -> str:
    return pytestconfig.getoption("--base-url") or settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, base_url: str) -> dict:
    return {**browser_context_args, "base_url": base_url, "locale": "en-US"}


@pytest.fixture(autouse=True)
def configure_timeouts(request: pytest.FixtureRequest, settings: Settings) -> None:
    if "page" not in request.fixturenames:
        return
    page = request.getfixturevalue("page")
    page.set_default_timeout(settings.default_timeout_ms)
    page.set_default_navigation_timeout(settings.default_timeout_ms)
