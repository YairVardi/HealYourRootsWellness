import re

import pytest
from playwright.sync_api import Page, expect

from automation.assertions import assert_https, assert_url_matches
from automation.data import LOGIN_ERROR_LEAK, THERAPIST_JOURNEY_PAGES
from automation.pages import DashboardPage, HomePage, LoginPage, TherapistPage


pytestmark = pytest.mark.ui


def test_therapist_cta_exists_and_redirects_to_clinician_landing_page(page: Page) -> None:
    home_page = HomePage(page)
    therapist_page = TherapistPage(page)
    home_page.go_to()
    expect(home_page.primary_therapist_cta).to_be_visible()
    expect(home_page.primary_therapist_cta).to_have_attribute("href", "/for-clinicians")
    home_page.primary_therapist_cta.focus()
    page.keyboard.press("Enter")
    therapist_page.expect_clinician_landing_loaded()
    assert_url_matches(page, re.compile(r"/for-clinicians(?:$|[?#/])", re.I))


@pytest.mark.parametrize("route", THERAPIST_JOURNEY_PAGES, ids=lambda route: route.label)
def test_therapist_routes_stay_out_of_client_booking_flow(page: Page, route) -> None:
    therapist_page = TherapistPage(page)
    page.goto(route.path, wait_until="domcontentloaded")
    therapist_page.expect_healthy()
    assert_url_matches(page, route.url_pattern)
    expect(page.get_by_text(route.heading).first).to_be_visible()
    assert not any(forbidden in page.url for forbidden in ("/find-a-therapist", "/consultation", "/schedule"))


def test_unauthenticated_users_cannot_access_member_dashboard_directly(page: Page) -> None:
    dashboard_page = DashboardPage(page)
    dashboard_page.go_to()
    dashboard_page.expect_protected_redirect()


@pytest.mark.xfail(reason=LOGIN_ERROR_LEAK, strict=True)
def test_login_errors_avoid_exposing_raw_transport_details_in_ui(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.go_to()
    login_page.expect_loaded()
    assert_https(page)
    with page.expect_response(
        lambda response: "/api/member/login" in response.url and response.request.method == "POST"
    ) as response_info:
        login_page.sign_in_with_email("invalid@example.com", "wrong-password")
    assert response_info.value is not None
    login_page.expect_login_failure_rendered()
    body_text = login_page.visible_body_text()
    assert "401:" not in body_text
    assert '{"error"' not in body_text
