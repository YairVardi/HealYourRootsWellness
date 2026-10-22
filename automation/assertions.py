from __future__ import annotations

import re
from typing import Iterable

from playwright.sync_api import Locator, Page, expect


ERROR_BOUNDARY_TEXT = re.compile("Something went wrong", re.I)
NOT_FOUND_HEADING = re.compile(r"^404$", re.I)
SERVER_ERROR_TEXT = re.compile(
    r"error code:\s*5\d\d|http error\s*5\d\d|bad gateway|service unavailable", re.I
)


def normalize_whitespace(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def wait_for_app_ready(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded")


def assert_page_healthy(page: Page) -> None:
    expect(page.locator("body")).to_be_visible()
    body_text = normalize_whitespace(page.locator("body").inner_text())
    assert not ERROR_BOUNDARY_TEXT.search(body_text), "The app rendered the global error boundary."
    assert not SERVER_ERROR_TEXT.search(body_text), "The app rendered an upstream/server error page."
    primary_heading = page.get_by_role("heading", level=1).first
    if primary_heading.count() and primary_heading.is_visible():
        assert not NOT_FOUND_HEADING.fullmatch(normalize_whitespace(primary_heading.inner_text()))


def assert_url_matches(page: Page, pattern: re.Pattern[str]) -> None:
    expect(page).to_have_url(pattern)


def assert_https(page: Page) -> None:
    assert page.url.startswith("https://"), f"Expected HTTPS URL, got {page.url}"


def assert_no_horizontal_overflow(page: Page) -> None:
    has_no_overflow = page.evaluate(
        """() => document.documentElement.scrollWidth <= window.innerWidth + 1
          && document.body.scrollWidth <= window.innerWidth + 1"""
    )
    assert has_no_overflow, "The page has unexpected horizontal overflow."


def assert_elements_do_not_overlap(first: Locator, second: Locator) -> None:
    first_box = first.bounding_box()
    second_box = second.bounding_box()
    assert first_box is not None
    assert second_box is not None
    overlaps = not (
        first_box["x"] + first_box["width"] <= second_box["x"]
        or second_box["x"] + second_box["width"] <= first_box["x"]
        or first_box["y"] + first_box["height"] <= second_box["y"]
        or second_box["y"] + second_box["height"] <= first_box["y"]
    )
    assert not overlaps, "The checked elements overlap in the viewport."


def attach_dialog_collector(page: Page) -> list[str]:
    messages: list[str] = []

    def collect(dialog) -> None:
        messages.append(dialog.message)
        dialog.dismiss()

    page.on("dialog", collect)
    return messages


def attach_console_collector(page: Page) -> list[str]:
    messages: list[str] = []
    page.on("console", lambda message: messages.append(normalize_whitespace(message.text)))
    return messages


def assert_no_sensitive_console_leak(messages: Iterable[str], payloads: Iterable[str]) -> None:
    normalized_messages = [message.lower() for message in messages]
    for payload in payloads:
        assert not any(payload.lower() in message for message in normalized_messages), (
            f"Console logs leaked sensitive payload: {payload}"
        )
