from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from automation.models import ConsultationData
from automation.pages.base import BasePage


class ConsultationPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.consultation_heading = page.get_by_role(
            "heading", name=re.compile("Schedule Your Free Consultation", re.I)
        )
        self.next_button = page.get_by_role("button", name=re.compile(r"^Next$", re.I))
        self.previous_button = page.get_by_role("button", name=re.compile(r"^Previous$", re.I))
        self.schedule_button = page.get_by_role(
            "button", name=re.compile("Schedule Consultation", re.I)
        )
        self.first_name_input = page.get_by_label("First Name")
        self.last_name_input = page.get_by_label("Last Name")
        self.email_input = page.get_by_label("Email Address")
        self.phone_input = page.get_by_label("Phone Number")

    def go_to(self) -> None:
        self.open("/consultation")

    def expect_loaded(self) -> None:
        self.expect_healthy()
        expect(self.consultation_heading).to_be_visible()

    def go_next(self) -> None:
        self.next_button.click()

    def go_previous(self) -> None:
        self.previous_button.click()

    def select_service_type(self, service_type_label: str) -> None:
        option = self.page.get_by_role("radio", name=service_type_label, exact=True)
        option.click(force=True)
        expect(option).to_have_attribute("aria-checked", "true")

    def expect_service_type_selected(self, service_type_label: str) -> None:
        option = self.page.get_by_role("radio", name=service_type_label, exact=True)
        expect(option).to_have_attribute("aria-checked", "true")

    def choose_focus_area(self, focus_area_label: str) -> None:
        self.page.get_by_text(focus_area_label, exact=True).click()

    def select_state(self, state_name: str) -> None:
        self._select_radix_option(
            re.compile(rf"Select your state|{re.escape(state_name)}", re.I), state_name
        )

    def choose_insurance_option(self, option_label: str) -> None:
        option = self.page.get_by_role("radio", name=option_label, exact=True)
        option.click(force=True)
        expect(option).to_have_attribute("aria-checked", "true")

    def select_insurance_provider(self, provider_name: str) -> None:
        self._select_radix_option(
            re.compile(rf"Select your insurance provider|{re.escape(provider_name)}", re.I),
            provider_name,
        )

    def fill_personal_details(self, data: ConsultationData) -> None:
        self.first_name_input.fill(data.first_name)
        self.last_name_input.fill(data.last_name)
        self.email_input.fill(data.email)
        self.phone_input.fill(data.phone)

    def move_to_personal_info(self, data: ConsultationData) -> None:
        self.select_service_type(data.service_type_label)
        self.go_next()
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"What areas would you like to focus on\?", re.I)
            )
        ).to_be_visible()
        if data.focus_area_label is not None:
            self.choose_focus_area(data.focus_area_label)
        self.go_next()
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"What state do you live in\?", re.I)
            )
        ).to_be_visible()
        self.select_state(data.state_name)
        self.go_next()
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"Do you have insurance\?|Insurance Information", re.I)
            )
        ).to_be_visible()
        self.choose_insurance_option(data.has_insurance_option_label)
        self.go_next()
        if data.insurance_provider_label is not None:
            expect(
                self.page.get_by_role(
                    "heading", name=re.compile(r"What insurance provider do you have\?", re.I)
                )
            ).to_be_visible()
            self.select_insurance_provider(data.insurance_provider_label)
            self.go_next()
        expect(
            self.page.get_by_role("heading", name=re.compile("Tell us about yourself", re.I))
        ).to_be_visible()

    def select_first_recommended_therapist(self, expected_name: str) -> None:
        expect(self.page.get_by_text(expected_name, exact=True)).to_be_visible()
        self.page.get_by_role("button", name=re.compile(r"^Select$", re.I)).first.click()

    def choose_date(self, date_label: str) -> None:
        self.page.get_by_text(date_label, exact=True).click()

    def choose_time(self, time_label: str) -> None:
        exact_time = self.page.get_by_role(
            "button", name=re.compile(rf"^{re.escape(time_label)}$", re.I)
        ).first
        if exact_time.count() and exact_time.is_visible():
            exact_time.click()
            return
        expect(self.page.get_by_text(re.compile("Available Times", re.I))).to_be_visible()
        first_visible_time = self.page.locator("button").filter(
            has_text=re.compile(r"\b\d{1,2}:\d{2}\s*(AM|PM)\b", re.I)
        ).first
        expect(first_visible_time).to_be_visible()
        first_visible_time.click()

    def complete_happy_path(self, data: ConsultationData) -> None:
        assert data.date_label is not None and data.time_label is not None
        self.move_to_personal_info(data)
        self.fill_personal_details(data)
        self.go_next()
        self.select_first_recommended_therapist(data.therapist_name)
        self.go_next()
        self.choose_date(data.date_label)
        self.choose_time(data.time_label)
        expect(self.schedule_button).to_be_enabled()
        self.schedule_button.click()

    def expect_confirmation(self, first_name: str) -> None:
        expect(self.page.get_by_role("heading", name=re.compile("Thank You", re.I)).first).to_be_visible()
        expect(self.page.get_by_text(re.compile(r"What Happens Next\?", re.I))).to_be_visible()

    def is_next_enabled(self) -> bool:
        return self.next_button.is_enabled()

    def first_available_time_button(self) -> Locator:
        return self.page.locator("button").filter(
            has_text=re.compile(r"\b\d{1,2}:\d{2}\s*(AM|PM)\b", re.I)
        ).first

    def _select_radix_option(self, trigger_expression: re.Pattern[str], option_name: str) -> None:
        trigger = self.page.locator('button, [role="combobox"]').filter(
            has_text=trigger_expression
        ).first
        trigger.click()
        option = self.page.get_by_text(option_name, exact=True).last
        expect(option).to_be_visible()
        option.click()
