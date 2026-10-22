import re

import pytest
from playwright.sync_api import Page, expect

from automation.assertions import (
    assert_elements_do_not_overlap,
    assert_no_horizontal_overflow,
    assert_url_matches,
)
from automation.data import CONSULTATION_WIZARD_REMOVED, VALID_CONSULTATION_DATA
from automation.pages import ConsultationPage, HomePage


pytestmark = pytest.mark.ui


def test_mobile_hamburger_menu_opens_and_closes_with_client_and_therapist_links(page: Page) -> None:
    home_page = HomePage(page)
    page.set_viewport_size({"width": 390, "height": 844})
    home_page.go_to()
    menu = home_page.header.navigation_menu
    expect(menu.menu_toggle).to_be_visible()
    menu.open_mobile_menu()
    expect(menu.link(re.compile("Find a Therapist", re.I))).to_be_visible()
    expect(menu.link(re.compile("Join as a Therapist", re.I))).to_be_visible()
    expect(menu.link(re.compile(r"^Login$", re.I))).to_be_visible()
    menu.close_mobile_menu()


def test_mobile_ctas_stay_tappable_and_hero_layout_avoids_overlap(page: Page) -> None:
    home_page = HomePage(page)
    page.set_viewport_size({"width": 390, "height": 844})
    home_page.go_to()
    assert_no_horizontal_overflow(page)
    expect(home_page.primary_client_cta).to_be_visible()
    expect(home_page.primary_therapist_cta).to_be_visible()
    assert_elements_do_not_overlap(home_page.primary_client_cta, home_page.primary_therapist_cta)
    home_page.primary_client_cta.click()
    assert_url_matches(page, re.compile(r"/find-a-therapist(?:$|[?#/])", re.I))


@pytest.mark.parametrize("viewport", [(768, 1024), (1024, 768)], ids=["portrait", "landscape"])
@pytest.mark.xfail(reason=CONSULTATION_WIZARD_REMOVED, strict=True)
def test_tablet_viewports_keep_consultation_entry_usable(
    page: Page, viewport: tuple[int, int]
) -> None:
    width, height = viewport
    consultation_page = ConsultationPage(page)
    page.set_viewport_size({"width": width, "height": height})
    consultation_page.go_to()
    consultation_page.expect_loaded()
    consultation_page.select_service_type(VALID_CONSULTATION_DATA.service_type_label)
    expect(consultation_page.next_button).to_be_enabled()
    assert_no_horizontal_overflow(page)
    expect(page.get_by_role("button", name=re.compile(r"^Next$", re.I))).to_be_visible()
