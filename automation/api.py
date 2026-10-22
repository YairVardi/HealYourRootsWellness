from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable, Iterable
from uuid import uuid4

import requests

from automation.config import Settings
from automation.models import RegisterMemberRequest


REGISTER_ENDPOINT = "/api/member/register"
LOGIN_ENDPOINT = "/api/member/login"
TEAM_ACCOUNTS_ENDPOINT = "/api/member/team/accounts"
TEAM_ACCOUNT_ENDPOINT = "/api/member/team/account"
ID_KEYS = {"id", "accountid", "userid", "memberid", "_id"}
CREATED_MEMBER_PATH = Path("artifacts/member-api-created-account.json")


def assert_created(response: requests.Response) -> None:
    assert response.status_code in {200, 201}, _status_message(response, "200 or 201")


def assert_success(response: requests.Response) -> None:
    assert 200 <= response.status_code < 300, _status_message(response, "2xx")


def assert_client_error(response: requests.Response) -> None:
    assert 400 <= response.status_code < 500, _status_message(response, "4xx")


def assert_unauthorized_or_forbidden(response: requests.Response) -> None:
    assert response.status_code in {401, 403}, _status_message(response, "401 or 403")


def _status_message(response: requests.Response, expected: str) -> str:
    return f"Expected {expected}, got HTTP {response.status_code} for {response.request.method} {response.url}"


def _json_root(response: requests.Response | None) -> Any:
    if response is None or not response.content:
        return None
    try:
        return response.json()
    except (requests.JSONDecodeError, json.JSONDecodeError, ValueError):
        return None


def first_id(response: requests.Response) -> str | None:
    return _find_first_value_for_keys(_json_root(response), ID_KEYS)


def id_near_email(response: requests.Response, email: str) -> str | None:
    return _find_id_near_value(_json_root(response), email)


def contains_email(response: requests.Response, email: str) -> bool:
    return _contains_value(_json_root(response), email)


def contains_id(response: requests.Response, account_id: str) -> bool:
    return _contains_value(_json_root(response), account_id)


def _find_id_near_value(node: Any, target: str) -> str | None:
    if isinstance(node, dict):
        if any(_contains_value(value, target) for value in node.values()):
            direct = _extract_id(node)
            if direct:
                return direct
        for child in node.values():
            nested = _find_id_near_value(child, target)
            if nested:
                return nested
    elif isinstance(node, list):
        for child in node:
            nested = _find_id_near_value(child, target)
            if nested:
                return nested
    return None


def _find_first_value_for_keys(node: Any, keys: set[str]) -> str | None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key.lower() in keys:
                return _stringify(value)
        for child in node.values():
            nested = _find_first_value_for_keys(child, keys)
            if nested:
                return nested
    elif isinstance(node, list):
        for child in node:
            nested = _find_first_value_for_keys(child, keys)
            if nested:
                return nested
    return None


def _contains_value(node: Any, expected: str) -> bool:
    if not expected or node is None:
        return False
    if isinstance(node, dict):
        return any(_contains_value(value, expected) for value in node.values())
    if isinstance(node, list):
        return any(_contains_value(value, expected) for value in node)
    value = _stringify(node)
    return value is not None and value.casefold() == expected.casefold()


def _extract_id(node: dict[str, Any]) -> str | None:
    for key, value in node.items():
        if key.lower() in ID_KEYS:
            return _stringify(value)
    return None


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value).strip()
    return result or None


def unique_member_email(settings: Settings) -> str:
    timestamp = int(time.time() * 1000)
    return f"qa.automation+{timestamp}-{str(uuid4())[:8]}@{settings.member_test_email_domain}"


def valid_register_request(settings: Settings, email: str) -> RegisterMemberRequest:
    if not settings.member_test_password:
        raise ValueError("MEMBER_TEST_PASSWORD is required.")
    timestamp = int(time.time() * 1000)
    return RegisterMemberRequest(
        first_name="QA",
        last_name="Automation",
        email=email,
        password=settings.member_test_password,
        confirm_password=settings.member_test_password,
        credentials="LCSW",
        license_number=f"QA-{timestamp}",
        license_state="PA",
    )


class BaseApiClient:
    def __init__(
        self,
        settings: Settings,
        include_configured_auth: bool = True,
        session: requests.Session | None = None,
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self.session.headers.update(settings.member_api_headers)
        if include_configured_auth and settings.member_auth_token:
            token = settings.member_auth_token
            self.session.headers["Authorization"] = (
                token if token.lower().startswith("bearer ") else f"Bearer {token}"
            )
        if include_configured_auth and settings.member_auth_cookie:
            self.session.headers["Cookie"] = settings.member_auth_cookie

    def _url(self, path: str) -> str:
        return f"{self.settings.api_base_url}{path}"


class MemberApiClient(BaseApiClient):
    def register(self, request: RegisterMemberRequest | dict[str, Any]) -> requests.Response:
        body = request.to_dict() if isinstance(request, RegisterMemberRequest) else request
        return self.session.post(self._url(REGISTER_ENDPOINT), json=body, timeout=30)

    def login(self, email: str, password: str) -> requests.Response:
        return self.session.post(
            self._url(LOGIN_ENDPOINT), json={"email": email, "password": password}, timeout=30
        )


class AccountApiClient(BaseApiClient):
    @classmethod
    def unauthenticated(cls, settings: Settings) -> "AccountApiClient":
        return cls(settings, include_configured_auth=False)

    def get_team_accounts(self) -> requests.Response:
        return self.session.get(self._url(TEAM_ACCOUNTS_ENDPOINT), timeout=30)

    def get_team_account(self, account_id: str | None = None) -> requests.Response:
        params = {"accountId": account_id} if account_id else None
        return self.session.get(self._url(TEAM_ACCOUNT_ENDPOINT), params=params, timeout=30)

    def delete_team_account_by_account_id(self, account_id: str) -> requests.Response:
        return self.session.delete(self._url(f"/api/member/team/accounts/{account_id}"), timeout=30)

    def delete_member_by_account_id(self, account_id: str) -> requests.Response:
        return self.session.delete(self._url(f"/api/member/{account_id}"), timeout=30)

    def delete_member_account_by_account_id(self, account_id: str) -> requests.Response:
        return self.session.delete(self._url(f"/api/member/account/{account_id}"), timeout=30)

    def deactivate_team_account_with_is_active_false(self, account_id: str) -> requests.Response:
        return self._patch_team_account(account_id, {"isActive": False})

    def deactivate_team_account_with_inactive_status(self, account_id: str) -> requests.Response:
        return self._patch_team_account(account_id, {"status": "inactive"})

    def delete_discovered_team_seat_by_seat_id(
        self, seat_id: str, account_context_id: str | None = None
    ) -> requests.Response:
        params = {"accountId": account_context_id} if account_context_id else None
        return self.session.delete(
            self._url(f"/api/member/team/seats/{seat_id}"), params=params, timeout=30
        )

    def _patch_team_account(self, account_id: str, body: dict[str, Any]) -> requests.Response:
        return self.session.patch(
            self._url(f"/api/member/team/accounts/{account_id}"), json=body, timeout=30
        )


def get_team_accounts_until_created_account_appears(
    client: AccountApiClient,
    email: str,
    created_id: str | None,
    attempts: int = 5,
    interval_seconds: float = 1.0,
) -> requests.Response:
    latest: requests.Response | None = None
    for attempt in range(attempts):
        latest = client.get_team_accounts()
        if contains_email(latest, email) or (created_id is not None and contains_id(latest, created_id)):
            return latest
        if attempt < attempts - 1:
            time.sleep(interval_seconds)
    assert latest is not None
    return latest


def save_created_member(
    email: str,
    account_id: str | None,
    source: str,
    path: Path = CREATED_MEMBER_PATH,
) -> None:
    existing: dict[str, Any] = {}
    if path.is_file():
        existing = json.loads(path.read_text(encoding="utf-8"))
    existing.update(
        {
            "email": email.strip(),
            "source": source.strip(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
    )
    if account_id and account_id.strip():
        existing["accountId"] = account_id.strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def load_created_account_id(path: Path = CREATED_MEMBER_PATH) -> str | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8")).get("accountId")
    return value.strip() if isinstance(value, str) and value.strip() else None


DELETE_CANDIDATES: dict[str, Callable[[AccountApiClient, str], requests.Response]] = {
    "DELETE_MEMBER_TEAM_ACCOUNTS": lambda client, account_id: client.delete_team_account_by_account_id(account_id),
    "DELETE_MEMBER": lambda client, account_id: client.delete_member_by_account_id(account_id),
    "DELETE_MEMBER_ACCOUNT": lambda client, account_id: client.delete_member_account_by_account_id(account_id),
    "PATCH_MEMBER_TEAM_ACCOUNTS_IS_ACTIVE_FALSE": lambda client, account_id: client.deactivate_team_account_with_is_active_false(account_id),
    "PATCH_MEMBER_TEAM_ACCOUNTS_STATUS_INACTIVE": lambda client, account_id: client.deactivate_team_account_with_inactive_status(account_id),
    "DELETE_MEMBER_TEAM_SEAT_DISCOVERED_FRONTEND": lambda client, account_id: client.delete_discovered_team_seat_by_seat_id(account_id),
}
