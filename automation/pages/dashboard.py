import re

from playwright.sync_api import Page, expect

from automation.assertions import assert_url_matches
from automation.pages.base import BasePage


class DashboardPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.sign_in_heading = page.get_by_text(
            re.compile("Sign in to your therapist community account", re.I)
        )

    def go_to(self) -> None:
        self.open("/dashboard")

    def expect_protected_redirect(self) -> None:
        assert_url_matches(self.page, re.compile(r"/dashboard/login(?:$|[?#/])", re.I))
        expect(self.sign_in_heading).to_be_visible()
