import re

import pytest
from playwright.sync_api import Page, expect

from automation.data import (
    CONSULTATION_WIZARD_REMOVED,
    DUPLICATE_CONSULTATION_SUBMIT,
    INVALID_EMAILS,
    INVALID_EMAIL_VALIDATION,
    LEADING_TRAILING_SPACES,
    LONG_INPUT,
    UNICODE_HEBREW_TEXT,
    VALID_CONSULTATION_DATA,
)
from automation.mocks import ConsultationMockOptions, mock_consultation_apis
from automation.pages import ConsultationPage


pytestmark = [
    pytest.mark.ui,
    pytest.mark.xfail(reason=CONSULTATION_WIZARD_REMOVED, strict=True),
]


def _valid_input(controller):
    return VALID_CONSULTATION_DATA.with_date_and_time(
        controller.fixtures.labels.date_label, controller.fixtures.labels.time_label
    )


def test_empty_personal_information_keeps_consultation_flow_blocked(page: Page) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(_valid_input(controller))
    assert not consultation_page.is_next_enabled()


@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
@pytest.mark.xfail(reason=INVALID_EMAIL_VALIDATION, strict=True)
def test_invalid_email_formats_should_be_blocked_before_therapist_matching(
    page: Page, invalid_email: str
) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(_valid_input(controller))
    data = VALID_CONSULTATION_DATA.with_personal_details(
        VALID_CONSULTATION_DATA.first_name,
        VALID_CONSULTATION_DATA.last_name,
        invalid_email,
        VALID_CONSULTATION_DATA.phone,
    )
    consultation_page.fill_personal_details(data)
    is_valid_email = consultation_page.email_input.evaluate("element => element.checkValidity()")
    assert not is_valid_email, f"{invalid_email} should fail HTML email validation."
    assert not consultation_page.is_next_enabled()


def test_unicode_spaces_and_special_characters_can_be_entered_without_crashing_flow(
    page: Page,
) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(_valid_input(controller))
    data = VALID_CONSULTATION_DATA.with_personal_details(
        LEADING_TRAILING_SPACES,
        UNICODE_HEBREW_TEXT,
        VALID_CONSULTATION_DATA.email,
        VALID_CONSULTATION_DATA.phone,
    )
    consultation_page.fill_personal_details(data)
    expect(consultation_page.first_name_input).to_have_value(LEADING_TRAILING_SPACES)
    expect(consultation_page.last_name_input).to_have_value(UNICODE_HEBREW_TEXT)
    consultation_page.go_next()
    expect(
        page.get_by_role("heading", name=re.compile("Choose your preferred therapist", re.I))
    ).to_be_visible()


def test_copy_paste_style_entry_and_long_input_survive_on_personal_info_step(page: Page) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(_valid_input(controller))
    consultation_page.first_name_input.click()
    consultation_page.first_name_input.fill("")
    page.keyboard.insert_text(LONG_INPUT)
    consultation_page.last_name_input.click()
    consultation_page.last_name_input.fill("")
    page.keyboard.insert_text("Copied Name")
    consultation_page.email_input.fill(VALID_CONSULTATION_DATA.email)
    consultation_page.phone_input.fill(VALID_CONSULTATION_DATA.phone)
    expect(consultation_page.first_name_input).to_have_value(LONG_INPUT)
    expect(consultation_page.last_name_input).to_have_value("Copied Name")
    assert consultation_page.is_next_enabled()


def test_multiple_rapid_submit_clicks_do_not_create_duplicate_consultation_requests(
    page: Page, browser_name: str, request: pytest.FixtureRequest
) -> None:
    if browser_name == "chromium":
        request.node.add_marker(pytest.mark.xfail(reason=DUPLICATE_CONSULTATION_SUBMIT, strict=True))
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    data = _valid_input(controller)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(data)
    consultation_page.fill_personal_details(data)
    consultation_page.go_next()
    consultation_page.select_first_recommended_therapist(data.therapist_name)
    consultation_page.go_next()
    consultation_page.choose_date(controller.fixtures.labels.date_label)
    consultation_page.choose_time(controller.fixtures.labels.time_label)
    consultation_page.schedule_button.click(click_count=3)
    consultation_page.expect_confirmation(data.first_name)
    assert len(controller.submitted_payloads) == 1


def test_consultation_flow_stays_usable_when_availability_calls_are_slow(page: Page) -> None:
    controller = mock_consultation_apis(
        page, ConsultationMockOptions(delay_availability_ms=800)
    )
    consultation_page = ConsultationPage(page)
    data = _valid_input(controller)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(data)
    consultation_page.fill_personal_details(data)
    consultation_page.go_next()
    consultation_page.select_first_recommended_therapist(data.therapist_name)
    consultation_page.go_next()
    consultation_page.choose_date(controller.fixtures.labels.date_label)
    expect(page.get_by_text(re.compile("Available Times", re.I))).to_be_visible()
    expect(consultation_page.first_available_time_button()).to_be_visible()


def test_consultation_next_requires_service_type_and_previous_preserves_selection(page: Page) -> None:
    consultation_page = ConsultationPage(page)
    service_type = VALID_CONSULTATION_DATA.service_type_label
    consultation_page.go_to()
    consultation_page.expect_loaded()
    assert not consultation_page.is_next_enabled()
    consultation_page.select_service_type(service_type)
    assert consultation_page.is_next_enabled()
    consultation_page.go_next()
    expect(
        page.get_by_role(
            "heading", name=re.compile(r"What areas would you like to focus on\?", re.I)
        )
    ).to_be_visible()
    consultation_page.go_previous()
    consultation_page.expect_loaded()
    consultation_page.expect_service_type_selected(service_type)
    assert consultation_page.is_next_enabled()
