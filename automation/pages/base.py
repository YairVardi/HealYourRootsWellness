from __future__ import annotations

import re

from playwright.sync_api import Page

from automation.assertions import assert_page_healthy, assert_url_matches, wait_for_app_ready
from automation.pages.components import Footer, Header


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.footer = Footer(page)

    def open(self, path: str) -> None:
        self.page.goto(path, wait_until="domcontentloaded")
        wait_for_app_ready(self.page)

    def refresh(self) -> None:
        self.page.reload(wait_until="domcontentloaded")
        wait_for_app_ready(self.page)

    def expect_healthy(self) -> None:
        assert_page_healthy(self.page)

    def expect_path(self, pattern: re.Pattern[str]) -> None:
        assert_url_matches(self.page, pattern)
