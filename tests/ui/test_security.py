import re

import pytest
from playwright.sync_api import Page, expect

from automation.assertions import (
    assert_https,
    assert_no_sensitive_console_leak,
    attach_console_collector,
    attach_dialog_collector,
)
from automation.data import (
    CONSULTATION_WIZARD_REMOVED,
    LOGIN_ERROR_LEAK,
    MALICIOUS_PAYLOADS,
    SPECIAL_CHARACTERS,
    UNICODE_HEBREW_TEXT,
    VALID_CONSULTATION_DATA,
)
from automation.mocks import mock_consultation_apis
from automation.pages import ConsultationPage, HomePage, LoginPage


pytestmark = pytest.mark.ui


def _valid_input(controller):
    return VALID_CONSULTATION_DATA.with_date_and_time(
        controller.fixtures.labels.date_label, controller.fixtures.labels.time_label
    )


def test_home_consultation_and_login_pages_stay_on_https(page: Page) -> None:
    for target in (HomePage(page), ConsultationPage(page), LoginPage(page)):
        target.go_to()
        assert_https(page)


@pytest.mark.xfail(reason=CONSULTATION_WIZARD_REMOVED, strict=True)
def test_script_sql_html_and_special_character_payloads_stay_inert_in_inputs(page: Page) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    dialog_messages = attach_dialog_collector(page)
    console_messages = attach_console_collector(page)
    data = _valid_input(controller)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(data)
    consultation_page.first_name_input.fill(MALICIOUS_PAYLOADS[0])
    consultation_page.last_name_input.fill(MALICIOUS_PAYLOADS[1])
    consultation_page.email_input.fill(data.email)
    consultation_page.phone_input.fill(data.phone)
    expect(consultation_page.first_name_input).to_have_value(MALICIOUS_PAYLOADS[0])
    expect(consultation_page.last_name_input).to_have_value(MALICIOUS_PAYLOADS[1])
    consultation_page.go_next()
    expect(
        page.get_by_role("heading", name=re.compile("Choose your preferred therapist", re.I))
    ).to_be_visible()
    assert dialog_messages == []
    assert_no_sensitive_console_leak(console_messages, MALICIOUS_PAYLOADS[:2])


@pytest.mark.xfail(reason=CONSULTATION_WIZARD_REMOVED, strict=True)
def test_no_sensitive_consultation_payload_is_echoed_to_console_during_entry(page: Page) -> None:
    controller = mock_consultation_apis(page)
    consultation_page = ConsultationPage(page)
    console_messages = attach_console_collector(page)
    dialog_messages = attach_dialog_collector(page)
    data = _valid_input(controller)
    consultation_page.go_to()
    consultation_page.move_to_personal_info(data)
    consultation_page.fill_personal_details(
        data.with_personal_details(UNICODE_HEBREW_TEXT, SPECIAL_CHARACTERS, data.email, data.phone)
    )
    assert dialog_messages == []
    assert_no_sensitive_console_leak(
        console_messages, (UNICODE_HEBREW_TEXT, SPECIAL_CHARACTERS, data.email, data.phone)
    )


@pytest.mark.xfail(reason=LOGIN_ERROR_LEAK, strict=True)
def test_login_failures_do_not_expose_raw_status_codes_or_json_payloads(page: Page) -> None:
    login_page = LoginPage(page)
    dialog_messages = attach_dialog_collector(page)
    login_page.go_to()
    with page.expect_response(
        lambda response: "/api/member/login" in response.url and response.request.method == "POST"
    ) as response_info:
        login_page.sign_in_with_email("invalid@example.com", "wrong-password")
    assert response_info.value is not None
    login_page.expect_login_failure_rendered()
    body_text = login_page.visible_body_text()
    assert dialog_messages == []
    assert "401:" not in body_text
    assert '{"error"' not in body_text


@pytest.mark.smoke
def test_login_page_renders_member_sign_in_options(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.go_to()
    login_page.expect_loaded()
    expect(login_page.create_account_link).to_be_visible()
