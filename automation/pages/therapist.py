import re

from playwright.sync_api import Page, expect

from automation.pages.base import BasePage


class TherapistPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.clinician_heading = page.get_by_role(
            "heading", name=re.compile("Community and Tools for Mental Health Providers", re.I)
        )

    def go_to_why_join(self) -> None:
        self.open("/for-clinicians")

    def go_to_join(self) -> None:
        self.open("/join")

    def go_to_group_practice(self) -> None:
        self.open("/group-practice")

    def expect_clinician_landing_loaded(self) -> None:
        self.expect_healthy()
        expect(self.clinician_heading).to_be_visible()
