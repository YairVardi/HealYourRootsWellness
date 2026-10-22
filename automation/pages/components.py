from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect


class NavigationMenu:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.menu_toggle = page.get_by_role("button", name=re.compile("toggle menu", re.I))

    def link(self, name: re.Pattern[str]) -> Locator:
        return self.page.get_by_role("link", name=name).first

    def open_mobile_menu(self) -> None:
        if self.menu_toggle.is_visible():
            self.menu_toggle.click()
            expect(self.menu_toggle).to_have_attribute("aria-expanded", "true")

    def close_mobile_menu(self) -> None:
        if self.menu_toggle.is_visible():
            self.menu_toggle.click()
            expect(self.menu_toggle).to_have_attribute("aria-expanded", "false")


class Header:
    def __init__(self, page: Page) -> None:
        self.root = page.locator("header").first
        self.navigation_menu = NavigationMenu(page)
        self.logo_link = self.root.locator("a").first
        self.find_therapist_menu_button = self.root.get_by_role(
            "button", name=re.compile(r"^Find a Therapist$", re.I)
        )
        self.find_therapist_menu = page.get_by_role(
            "menu", name=re.compile(r"^Find a Therapist$", re.I)
        )
        self.find_therapist_directory_link = self.find_therapist_menu.get_by_role(
            "menuitem", name=re.compile(r"^All providers$", re.I)
        )
        self.login_link = self.root.get_by_role(
            "link", name=re.compile(r"^Therapist Login$", re.I)
        )
        self.join_therapist_link = self.root.get_by_role(
            "link", name=re.compile(r"^Join as a Therapist$", re.I)
        )

    def open_find_therapist_directory(self) -> None:
        expect(self.find_therapist_menu_button).to_be_visible()
        expect(self.find_therapist_menu_button).to_have_attribute("aria-expanded", "false")
        self.find_therapist_menu_button.click()
        expect(self.find_therapist_menu).to_be_visible()
        expect(self.find_therapist_directory_link).to_be_visible()
        self.find_therapist_directory_link.click()

    def expect_visible(self) -> None:
        expect(self.root).to_be_visible()
        expect(self.logo_link).to_be_visible()


class Footer:
    def __init__(self, page: Page) -> None:
        self.root = page.locator("footer").first

    def link(self, name: re.Pattern[str]) -> Locator:
        return self.root.locator("a").filter(has_text=name).first

    def expect_visible(self) -> None:
        expect(self.root).to_be_visible()
