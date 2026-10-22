import pytest

from automation.api import (
    AccountApiClient,
    DELETE_CANDIDATES,
    assert_success,
    load_created_account_id,
)
from automation.config import Settings


pytestmark = [pytest.mark.api, pytest.mark.destructive]


def test_confirmed_delete_or_deactivate_candidate_succeeds(settings: Settings) -> None:
    if not settings.delete_investigation_enabled:
        pytest.skip("Delete account investigation is disabled by default.")
    if not settings.delete_confirmation_accepted:
        pytest.skip("Set the explicit MEMBER_DELETE_CONFIRMATION acknowledgement to run.")
    account_id = settings.delete_account_id or load_created_account_id()
    if not account_id:
        pytest.skip("Set MEMBER_DELETE_ACCOUNT_ID or run the verification test first.")
    if settings.delete_candidate not in DELETE_CANDIDATES:
        pytest.skip(f"Unsupported or missing MEMBER_DELETE_CANDIDATE: {settings.delete_candidate}")
    response = DELETE_CANDIDATES[settings.delete_candidate](AccountApiClient(settings), account_id)
    assert_success(response)
