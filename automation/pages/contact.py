import re

from playwright.sync_api import Page, expect

from automation.pages.base import BasePage


class ContactPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", name=re.compile(r"^Contact$", re.I))
        self.form_heading = page.get_by_role(
            "heading", name=re.compile("Heal Your Roots Wellness Contact Us Form", re.I)
        )
        self.book_now_link = page.get_by_role("link", name=re.compile(r"^Book Now$", re.I))

    def go_to(self) -> None:
        self.open("/contact")

    def expect_loaded(self) -> None:
        self.expect_healthy()
        expect(self.heading).to_be_visible()
        expect(self.form_heading).to_be_visible()
        expect(self.book_now_link).to_be_visible()

    def open_consultation(self) -> None:
        self.book_now_link.click()
