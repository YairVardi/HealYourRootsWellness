from __future__ import annotations

from dataclasses import dataclass
import json
import time
from urllib.parse import urlparse

from playwright.sync_api import Page, Route

from automation.data import ConsultationMockFixtures, build_mock_consultation_fixtures


@dataclass(frozen=True)
class ConsultationMockOptions:
    fixtures: ConsultationMockFixtures | None = None
    delay_match_ms: int = 0
    delay_availability_ms: int = 0


@dataclass
class ConsultationMockController:
    fixtures: ConsultationMockFixtures
    submitted_payloads: list[str]


def mock_consultation_apis(
    page: Page, options: ConsultationMockOptions | None = None
) -> ConsultationMockController:
    configured = options or ConsultationMockOptions()
    fixtures = configured.fixtures or build_mock_consultation_fixtures()
    submitted_payloads: list[str] = []

    page.route("**/api/states", lambda route: _fulfill_json(route, fixtures.states))
    page.route(
        "**/api/consultation/specialized-needs",
        lambda route: _fulfill_json(route, fixtures.specialized_needs),
    )

    def insurance_handler(route: Route) -> None:
        state_code = _last_path_segment(route.request.url)
        _fulfill_json(route, fixtures.insurance_providers_by_state.get(state_code, []))

    def match_handler(route: Route) -> None:
        _delay(configured.delay_match_ms)
        _fulfill_json(route, fixtures.therapists)

    def availability_handler(route: Route) -> None:
        _delay(configured.delay_availability_ms)
        key = _last_path_segment(route.request.url)
        availability = fixtures.availability_by_therapist.get(
            key, fixtures.availability_by_therapist.get("101", {"slots": []})
        )
        _fulfill_json(route, availability)

    def submit_handler(route: Route) -> None:
        submitted_payloads.append(route.request.post_data or "")
        _fulfill_json(route, fixtures.submit_response)

    page.route("**/api/insurance-providers/state/**", insurance_handler)
    page.route("**/api/therapists/match**", match_handler)
    page.route("**/api/calendar/availability/**", availability_handler)
    page.route("**/api/consultations/fixed", submit_handler)
    return ConsultationMockController(fixtures, submitted_payloads)


def _fulfill_json(route: Route, payload: object) -> None:
    route.fulfill(status=200, content_type="application/json", body=json.dumps(payload))


def _last_path_segment(raw_url: str) -> str:
    return urlparse(raw_url).path.rsplit("/", 1)[-1]


def _delay(milliseconds: int) -> None:
    if milliseconds > 0:
        time.sleep(milliseconds / 1000)
