import json
from pathlib import Path

import requests

from automation.api import contains_email, contains_id, first_id, id_near_email, load_created_account_id, save_created_member


def _response(payload) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode()
    response.headers["Content-Type"] = "application/json"
    return response


def test_extractors_find_nested_account_identity() -> None:
    response = _response({"data": [{"accountId": 42, "profile": {"email": "qa@example.com"}}]})
    assert first_id(response) == "42"
    assert id_near_email(response, "qa@example.com") == "42"
    assert contains_email(response, "QA@example.com")
    assert contains_id(response, "42")


def test_created_member_registry_preserves_id_when_later_save_has_none(tmp_path: Path) -> None:
    registry = tmp_path / "member.json"
    save_created_member("first@example.com", "account-1", "first", registry)
    save_created_member("second@example.com", None, "second", registry)
    assert load_created_account_id(registry) == "account-1"
    assert json.loads(registry.read_text(encoding="utf-8"))["email"] == "second@example.com"
