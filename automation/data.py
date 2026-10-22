from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import re
from typing import Any
from zoneinfo import ZoneInfo

from automation.models import ConsultationData


@dataclass(frozen=True)
class RouteExpectation:
    label: str
    path: str
    heading: re.Pattern[str]
    url_pattern: re.Pattern[str]
    known_issue: str | None = None


def route(label: str, path: str, heading: str, url_pattern: str) -> RouteExpectation:
    return RouteExpectation(label, path, re.compile(heading, re.I), re.compile(url_pattern, re.I))


LOGIN_ERROR_LEAK = "Invalid login currently exposes raw 401 JSON in the UI."
INVALID_EMAIL_VALIDATION = (
    "The current client flow only checks that the email field is non-empty before enabling Next."
)
DUPLICATE_CONSULTATION_SUBMIT = (
    "Rapid clicks on Schedule Consultation currently create duplicate consultation requests."
)
SCHEDULE_CONSULT_ENTRY_REMOVED = (
    "The current homepage no longer exposes the schedule-a-consult entry point required by the test."
)
CONTACT_BOOK_NOW_REMOVED = (
    "The current contact page replaced Book Now consultation navigation with clinician browsing."
)
CONSULTATION_WIZARD_REMOVED = (
    "The current /consultation page states that HYRW no longer performs intake, matching, or scheduling."
)

CLIENT_JOURNEY_PAGES = (
    route("Find a Therapist", "/find-a-therapist", "^Find a Therapist$", r"/find-a-therapist(?:$|[/?#])"),
    route("Services", "/services", "Find an online therapist", r"/(services|telehealth-therapy)(?:$|[/?#])"),
    route("Specialties", "/specialties", "Our Therapy Specialties|Specialties", r"/specialties(?:$|[/?#])"),
    route("Telehealth Therapy", "/telehealth-therapy", "Find an online therapist", r"/telehealth-therapy(?:$|[/?#])"),
    route("Locations", "/find-a-therapist/pennsylvania", "Pennsylvania Online Therapy", r"/find-a-therapist/pennsylvania(?:$|[/?#])"),
    route("Insurance & Pricing", "/insurance", "Insurance", r"/insurance(?:$|[/?#])"),
    route("FAQ", "/faq", "Frequently asked questions", r"/faq(?:$|[/?#])"),
    route("Contact / Book Consultation", "/contact", "Contact", r"/contact(?:$|[/?#])"),
)

THERAPIST_JOURNEY_PAGES = (
    route("Why Join", "/for-clinicians", "Community and Tools for Mental Health Providers", r"/for-clinicians(?:$|[/?#])"),
    route("Join the Network", "/join", "Join the first 500 clinicians", r"/join(?:$|[/?#])"),
    route("Group Practice Plans", "/group-practice", "One subscription for the whole practice", r"/group-practice(?:$|[/?#])"),
    route("Member Login", "/dashboard/login", "Sign in to your therapist community account", r"/dashboard/login(?:$|[/?#])"),
)

FOOTER_SUPPORT_PAGES = (
    route("Privacy Policy", "/privacy-policy", "Privacy Policy", r"/privacy-policy(?:$|[/?#])"),
    route("Terms of Service", "/terms-of-service", "Terms of Service", r"/terms-of-service(?:$|[/?#])"),
    route("Accessibility", "/accessibility", "Accessibility", r"/accessibility(?:$|[/?#])"),
    route(
        "Sitemap",
        "/sitemap",
        r"^(?:Site Map|Explore Our Wellness Sitemap)$",
        r"/sitemap(?:$|[/?#])",
    ),
)

IMPORTANT_HTTP_ROUTES = (
    "/", "/find-a-therapist", "/contact", "/consultation", "/join",
    "/for-clinicians", "/dashboard/login", "/privacy-policy",
    "/terms-of-service", "/accessibility",
)

INVALID_EMAILS = ("abc", "abc@", "abc@.com", "abc@gmail")
MALICIOUS_PAYLOADS = (
    "<script>alert(1)</script>",
    "' OR 1=1 --",
    "<b>bold</b>",
    "<img src=x onerror=alert(1)>",
)
SPECIAL_CHARACTERS = "QA !@#$%^&*()_+-=[]{};:'\\\",.<>/?`~"
UNICODE_HEBREW_TEXT = "שלום בדיקת אוטומציה"
LEADING_TRAILING_SPACES = "  Yael  "
LONG_INPUT = "long-input-" * 25

VALID_CONSULTATION_DATA = ConsultationData(
    service_type_label="Individual Therapy",
    focus_area_label="Anxiety",
    state_name="Pennsylvania",
    state_code="PA",
    has_insurance_option_label="Yes, I have insurance",
    insurance_provider_label="Aetna",
    first_name="QA",
    last_name="Automation",
    email="qa.automation+hyr@example.com",
    phone="5551234567",
    therapist_name="Dr. Avery Cole",
)


@dataclass(frozen=True)
class ConsultationLabels:
    date_label: str
    time_label: str


@dataclass(frozen=True)
class ConsultationMockFixtures:
    states: list[dict[str, Any]]
    specialized_needs: list[dict[str, Any]]
    insurance_providers_by_state: dict[str, list[dict[str, Any]]]
    therapists: list[dict[str, Any]]
    availability_by_therapist: dict[str, dict[str, Any]]
    submit_response: dict[str, Any]
    labels: ConsultationLabels


def build_mock_consultation_fixtures(today: date | None = None) -> ConsultationMockFixtures:
    current_day = today or date.today()
    appointment_day = current_day + timedelta(days=1)
    while appointment_day.weekday() >= 5:
        appointment_day += timedelta(days=1)
    primary_slot = datetime.combine(appointment_day, time(14, 0), timezone.utc)
    backup_slot = datetime.combine(appointment_day, time(14, 30), timezone.utc)
    primary_iso = primary_slot.isoformat().replace("+00:00", "Z")
    backup_iso = backup_slot.isoformat().replace("+00:00", "Z")
    if appointment_day == current_day:
        date_label = "Today"
    elif appointment_day == current_day + timedelta(days=1):
        date_label = "Tomorrow"
    else:
        date_label = appointment_day.strftime("%a, %b %-d")
    time_label = primary_slot.astimezone(ZoneInfo("America/New_York")).strftime("%-I:%M %p")
    return ConsultationMockFixtures(
        states=[
            {"id": 1, "name": "Pennsylvania", "abbreviation": "PA", "isActive": True},
            {"id": 2, "name": "Florida", "abbreviation": "FL", "isActive": True},
            {"id": 3, "name": "New York", "abbreviation": "NY", "isActive": False},
        ],
        specialized_needs=[
            {"id": 1, "optionValue": "anxiety", "optionLabel": "Anxiety", "description": "Support for worry, panic, and day-to-day stress.", "isActive": True},
            {"id": 2, "optionValue": "trauma", "optionLabel": "Trauma", "description": "Trauma-informed care for processing difficult experiences.", "isActive": True},
            {"id": 3, "optionValue": "relationship-issues", "optionLabel": "Relationship Issues", "description": "Communication, conflict, and attachment support.", "isActive": True},
        ],
        insurance_providers_by_state={
            "PA": [
                {"id": 11, "name": "Aetna", "type": "commercial", "isActive": True},
                {"id": 12, "name": "Legacy Health Plan", "type": "commercial", "isActive": False},
            ],
            "FL": [{"id": 21, "name": "Self Pay Only", "type": "self_pay", "isActive": False}],
        },
        therapists=[
            {"id": 101, "name": "Dr. Avery Cole", "specialties": ["Anxiety", "Trauma"]},
            {"id": 102, "name": "Jordan Patel, LPC", "specialties": ["Relationship Issues"]},
        ],
        availability_by_therapist={
            "101": {"slots": [{"start": primary_iso, "available": True}, {"start": backup_iso, "available": True}]},
            "102": {"slots": [{"start": backup_iso, "available": True}]},
        },
        submit_response={"id": 9001, "status": "scheduled"},
        labels=ConsultationLabels(date_label, time_label),
    )
