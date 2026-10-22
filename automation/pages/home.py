import re

from playwright.sync_api import Page, expect

from automation.pages.base import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.hero_heading = page.get_by_role(
            "heading", name=re.compile("A therapist directory and community, built by clinicians", re.I)
        )
        self.primary_client_cta = page.get_by_role(
            "link", name="FIND A THERAPIST", exact=True
        ).first
        self.primary_therapist_cta = page.get_by_role(
            "link", name="I'm a therapist", exact=True
        ).first
        self.schedule_consult_link = page.get_by_role(
            "link", name=re.compile("schedule a consult", re.I)
        ).first

    def go_to(self) -> None:
        self.open("/")

    def expect_loaded(self) -> None:
        self.expect_healthy()
        self.header.expect_visible()
        expect(self.hero_heading).to_be_visible()
        expect(self.primary_client_cta).to_be_visible()
        expect(self.primary_therapist_cta).to_be_visible()
        self.footer.expect_visible()
