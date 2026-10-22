import re

import pytest
import requests
from playwright.sync_api import Page, expect

from automation.assertions import assert_page_healthy, assert_url_matches
from automation.config import Settings
from automation.data import FOOTER_SUPPORT_PAGES, IMPORTANT_HTTP_ROUTES
from automation.pages import ContactPage, HomePage


pytestmark = pytest.mark.ui


def test_homepage_renders_header_footer_logo_and_main_navigation_links(page: Page) -> None:
    home_page = HomePage(page)
    home_page.go_to()
    home_page.expect_loaded()
    expect(home_page.header.find_therapist_menu_button).to_be_visible()
    expect(home_page.header.find_therapist_menu_button).to_have_attribute("aria-haspopup", "menu")
    expect(home_page.header.login_link).to_be_visible()
    expect(home_page.header.join_therapist_link).to_be_visible()


def test_header_links_and_logo_navigate_correctly(page: Page) -> None:
    home_page = HomePage(page)
    contact_page = ContactPage(page)
    home_page.go_to()
    home_page.header.open_find_therapist_directory()
    assert_url_matches(page, re.compile(r"/find-a-therapist(?:$|[?#/])", re.I))
    expect(
        page.get_by_role("heading", name="Find a Therapist", exact=True, level=1)
    ).to_be_visible()
    home_page.go_to()
    home_page.header.login_link.click()
    assert_url_matches(page, re.compile(r"/dashboard/login(?:$|[?#/])", re.I))
    expect(page.get_by_text(re.compile("Sign in to your therapist community account", re.I)).first).to_be_visible()
    home_page.go_to()
    home_page.header.join_therapist_link.click()
    assert_url_matches(page, re.compile(r"/join(?:$|[?#/])", re.I))
    expect(page.get_by_text(re.compile("Join the first 500 clinicians", re.I)).first).to_be_visible()
    contact_page.go_to()
    home_page.header.logo_link.click()
    assert_url_matches(page, re.compile(r"/$"))


def test_browser_back_forward_and_refresh_preserve_route_stability(page: Page) -> None:
    home_page = HomePage(page)
    home_page.go_to()
    home_page.header.open_find_therapist_directory()
    assert_url_matches(page, re.compile(r"/find-a-therapist(?:$|[?#/])", re.I))
    page.go_back(wait_until="domcontentloaded")
    assert_url_matches(page, re.compile(r"/$"))
    page.go_forward(wait_until="domcontentloaded")
    assert_url_matches(page, re.compile(r"/find-a-therapist(?:$|[?#/])", re.I))
    page.reload(wait_until="domcontentloaded")
    assert_page_healthy(page)
    expect(
        page.get_by_role("heading", name="Find a Therapist", exact=True, level=1)
    ).to_be_visible()


@pytest.mark.parametrize("route", IMPORTANT_HTTP_ROUTES)
def test_important_public_routes_do_not_return_http_404_responses(
    settings: Settings, route: str
) -> None:
    response = requests.get(settings.absolute_url(route), timeout=30, allow_redirects=True)
    assert response.status_code != 404, f"Unexpected HTTP 404 for {route}"


@pytest.mark.parametrize(
    "route", [route for route in FOOTER_SUPPORT_PAGES if route.known_issue is None], ids=lambda route: route.label
)
def test_footer_support_links_load_real_content_pages(page: Page, route) -> None:
    page.goto(route.path, wait_until="domcontentloaded")
    assert_page_healthy(page)
    assert_url_matches(page, route.url_pattern)
    expect(page.get_by_role("heading", name=route.heading).first).to_be_visible()


def test_footer_sitemap_link_should_not_land_on_404_page(page: Page) -> None:
    sitemap_route = next(route for route in FOOTER_SUPPORT_PAGES if route.label == "Sitemap")
    page.goto(sitemap_route.path, wait_until="domcontentloaded")
    assert_page_healthy(page)
    expect(page.get_by_role("heading", name=sitemap_route.heading).first).to_be_visible()
