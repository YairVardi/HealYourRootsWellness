import re

from playwright.sync_api import Page, expect

from automation.pages.base import BasePage


class FAQPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.refresh_button = page.get_by_role("button", name=re.compile("Refresh Page", re.I))

    def go_to(self) -> None:
        self.open("/faq")

    def expect_loaded(self) -> None:
        self.expect_healthy()
        expect(
            self.page.get_by_role("heading", name=re.compile("Frequently Asked Questions|FAQ", re.I))
        ).to_be_visible()
