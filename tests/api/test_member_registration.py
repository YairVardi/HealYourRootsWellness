from __future__ import annotations

import pytest

from automation.api import (
    MemberApiClient,
    assert_client_error,
    assert_created,
    first_id,
    save_created_member,
    unique_member_email,
    valid_register_request,
)
from automation.config import Settings


pytestmark = pytest.mark.api


@pytest.fixture
def member_api_client(settings: Settings) -> MemberApiClient:
    if not settings.run_mutating_api_tests:
        pytest.skip("Set RUN_MUTATING_API_TESTS=true to enable synthetic member registration tests.")
    if not settings.member_test_password:
        pytest.skip("Set MEMBER_TEST_PASSWORD before running member registration tests.")
    return MemberApiClient(settings, include_configured_auth=False)


def _new_valid_request(settings: Settings):
    return valid_register_request(settings, unique_member_email(settings))


def test_create_member_account_returns_success_and_created_identity_when_available(
    member_api_client: MemberApiClient, settings: Settings
) -> None:
    request = _new_valid_request(settings)
    response = member_api_client.register(request)
    assert_created(response)
    assert response.text.strip(), "registration response body should not be blank"
    created_id = first_id(response)
    if created_id is not None:
        assert created_id.strip()
    save_created_member(request.email, created_id, "member-register-response")


def test_create_member_account_rejects_missing_required_fields(
    member_api_client: MemberApiClient, settings: Settings
) -> None:
    body = _new_valid_request(settings).to_dict()
    for key in ("email", "password", "confirmPassword"):
        body.pop(key)
    assert_client_error(member_api_client.register(body))


def test_create_member_account_rejects_invalid_email(
    member_api_client: MemberApiClient, settings: Settings
) -> None:
    body = _new_valid_request(settings).to_dict()
    body["email"] = "not-an-email"
    assert_client_error(member_api_client.register(body))


def test_create_member_account_rejects_duplicate_email(
    member_api_client: MemberApiClient, settings: Settings
) -> None:
    request = _new_valid_request(settings)
    assert_created(member_api_client.register(request))
    assert_client_error(member_api_client.register(request))


def test_create_member_account_rejects_empty_body(member_api_client: MemberApiClient) -> None:
    assert_client_error(member_api_client.register({}))
