import re

from playwright.sync_api import Page, expect

from automation.pages.base import BasePage


class ClientPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.directory_heading = page.get_by_role("heading", name=re.compile("Find a Therapist", re.I))
        self.filters_button = page.get_by_role("button", name=re.compile(r"^Filters$", re.I))

    def go_to_route(self, path: str) -> None:
        self.open(path)

    def go_to_directory(self) -> None:
        self.go_to_route("/find-a-therapist")

    def expect_directory_loaded(self) -> None:
        self.expect_healthy()
        expect(self.directory_heading).to_be_visible()
        expect(self.filters_button).to_be_visible()
