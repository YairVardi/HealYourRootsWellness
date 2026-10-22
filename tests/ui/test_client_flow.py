import re

import pytest
from playwright.sync_api import Page, expect

from automation.assertions import assert_url_matches
from automation.data import (
    CLIENT_JOURNEY_PAGES,
    CONSULTATION_WIZARD_REMOVED,
    CONTACT_BOOK_NOW_REMOVED,
    SCHEDULE_CONSULT_ENTRY_REMOVED,
    VALID_CONSULTATION_DATA,
)
from automation.mocks import mock_consultation_apis
from automation.pages import ClientPage, ConsultationPage, ContactPage, FAQPage, HomePage


pytestmark = pytest.mark.ui


@pytest.mark.smoke
@pytest.mark.xfail(reason=SCHEDULE_CONSULT_ENTRY_REMOVED, strict=True)
def test_homepage_loads_and_exposes_patient_facing_entry_points(page: Page) -> None:
    home_page = HomePage(page)
    home_page.go_to()
    home_page.expect_loaded()
    expect(home_page.schedule_consult_link).to_be_visible()
    expect(home_page.header.find_therapist_menu_button).to_be_visible()


@pytest.mark.parametrize(
    "route",
    [route for route in CLIENT_JOURNEY_PAGES if route.known_issue is None],
    ids=lambda route: route.label,
)
def test_client_journey_routes_stay_inside_public_patient_facing_pages(
    page: Page, route
) -> None:
    client_page = ClientPage(page)
    client_page.go_to_route(route.path)
    client_page.expect_healthy()
    assert_url_matches(page, route.url_pattern)
    expect(page.get_by_role("heading", name=route.heading).first).to_be_visible()
    assert not any(
        forbidden in page.url for forbidden in ("/dashboard", "/join", "/for-clinicians", "/group-practice")
    )


def test_faq_route_should_render_faq_content_instead_of_global_error_boundary(page: Page) -> None:
    faq_page = FAQPage(page)
    faq_page.go_to()
    faq_page.expect_loaded()


@pytest.mark.smoke
@pytest.mark.xfail(reason=CONTACT_BOOK_NOW_REMOVED, strict=True)
def test_contact_page_book_now_cta_leads_into_consultation_flow(page: Page) -> None:
    contact_page = ContactPage(page)
    contact_page.go_to()
    contact_page.expect_loaded()
    contact_page.open_consultation()
    assert_url_matches(page, re.compile(r"/consultation(?:$|[?#/])", re.I))
    expect(
        page.get_by_role("heading", name=re.compile("Schedule Your Free Consultation", re.I))
    ).to_be_visible()


def test_client_cta_does_not_redirect_into_therapist_only_areas_under_rapid_clicks(
    page: Page,
) -> None:
    home_page = HomePage(page)
    home_page.go_to()
    home_page.primary_client_cta.evaluate("element => { element.click(); element.click(); element.click(); }")
    assert_url_matches(page, re.compile(r"/find-a-therapist(?:$|[?#/])", re.I))
    assert not any(
        forbidden in page.url for forbidden in ("/dashboard", "/join", "/for-clinicians", "/group-practice")
    )


@pytest.mark.xfail(reason=CONSULTATION_WIZARD_REMOVED, strict=True)
def test_consultation_happy_path_completes_safely_with_mocked_production_apis(
    page: Page,
) -> None:
    controller = mock_consultation_apis(page)
    data = VALID_CONSULTATION_DATA.with_date_and_time(
        controller.fixtures.labels.date_label, controller.fixtures.labels.time_label
    )
    consultation_page = ConsultationPage(page)
    consultation_page.go_to()
    consultation_page.complete_happy_path(data)
    consultation_page.expect_confirmation(data.first_name)
    assert len(controller.submitted_payloads) == 1
    payload = controller.submitted_payloads[0]
    selected_datetime = controller.fixtures.availability_by_therapist["101"]["slots"][0]["start"]
    for expected in (
        data.first_name,
        data.last_name,
        data.email,
        data.phone,
        data.state_code,
        "individual",
        "101",
        selected_datetime,
    ):
        assert expected in payload
