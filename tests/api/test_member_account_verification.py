from __future__ import annotations

import requests
import pytest

from automation.api import (
    AccountApiClient,
    MemberApiClient,
    assert_created,
    assert_success,
    assert_unauthorized_or_forbidden,
    contains_email,
    contains_id,
    first_id,
    get_team_accounts_until_created_account_appears,
    id_near_email,
    save_created_member,
    unique_member_email,
    valid_register_request,
)
from automation.config import Settings


pytestmark = pytest.mark.api


def test_created_member_account_appears_in_team_accounts(settings: Settings) -> None:
    if not settings.run_mutating_api_tests:
        pytest.skip("Set RUN_MUTATING_API_TESTS=true to enable synthetic member registration tests.")
    if not settings.member_test_password:
        pytest.skip("Set MEMBER_TEST_PASSWORD before running member API tests.")
    shared_session = requests.Session()
    member_client = MemberApiClient(settings, include_configured_auth=False, session=shared_session)
    account_client = AccountApiClient(settings, session=shared_session)
    request = valid_register_request(settings, unique_member_email(settings))
    register_response = member_client.register(request)
    assert_created(register_response)
    created_id = first_id(register_response)
    accounts_response = get_team_accounts_until_created_account_appears(
        account_client, request.email, created_id
    )
    assert_success(accounts_response)
    assert accounts_response.text.strip(), "team accounts response body should not be blank"
    found_by_email = contains_email(accounts_response, request.email)
    found_by_id = created_id is not None and contains_id(accounts_response, created_id)
    assert found_by_email or found_by_id, (
        "created member should appear in GET /api/member/team/accounts by email or returned id"
    )
    account_id = id_near_email(accounts_response, request.email) or created_id or first_id(accounts_response)
    save_created_member(request.email, account_id, "member-team-accounts-response")


def test_team_accounts_rejects_unauthenticated_requests(settings: Settings) -> None:
    response = AccountApiClient.unauthenticated(settings).get_team_accounts()
    assert_unauthorized_or_forbidden(response)
