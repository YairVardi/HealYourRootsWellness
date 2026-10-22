import re

from playwright.sync_api import Page, expect

from automation.assertions import normalize_whitespace
from automation.pages.base import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.email_input = page.get_by_placeholder("your@email.com")
        self.password_input = page.get_by_placeholder("Your password")
        self.email_sign_in_button = page.get_by_role(
            "button", name=re.compile("sign in with email", re.I)
        )
        self.google_button = page.get_by_role("button", name=re.compile("continue with google", re.I))
        self.replit_button = page.get_by_role("button", name=re.compile("continue with replit", re.I))
        self.create_account_link = page.get_by_role(
            "link", name=re.compile("create a free account", re.I)
        )
        self.login_failure_message = page.get_by_text(re.compile("login failed", re.I)).first

    def go_to(self) -> None:
        self.open("/dashboard/login")

    def expect_loaded(self) -> None:
        expect(self.email_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.email_sign_in_button).to_be_visible()
        expect(self.google_button).to_be_visible()
        expect(self.replit_button).to_be_visible()

    def sign_in_with_email(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.email_sign_in_button.click()

    def expect_login_failure_rendered(self) -> None:
        expect(self.login_failure_message).to_be_visible()

    def visible_body_text(self) -> str:
        return normalize_whitespace(self.page.locator("body").text_content())
