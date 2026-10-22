import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


SPEC = importlib.util.spec_from_file_location(
    "jira_sync", Path(__file__).parents[2] / "scripts" / "jira_sync.py"
)
jira_sync = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(jira_sync)


class FakeJira:
    site = "https://aiqatesting.atlassian.net"

    def __init__(self, existing=()):
        self.existing = existing
        self.created = []

    def search(self, query, fields):
        return iter([{"fields": {"labels": list(self.existing)}}])

    def request(self, method, path, data):
        self.created.append(data)
        return {"key": "AQT-2"}


@pytest.fixture
def pytest_junit_report(tmp_path: Path) -> Path:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuites><testsuite name="pytest"><testcase classname="tests.test_a" name="test_passed"/>'
        '<testcase classname="tests.test_a" name="test_skipped"><skipped/></testcase>'
        '<testcase classname="tests.test_a" name="test_failed[param-a]"><failure type="AssertionError">'
        'private medical data</failure></testcase>'
        '<testcase classname="tests.test_a" name="test_error"><error type="Exception"/></testcase>'
        '</testsuite></testsuites>',
        encoding="utf-8",
    )
    return report


def test_reports_only_final_pytest_failures_and_errors(pytest_junit_report: Path) -> None:
    rows = jira_sync.failures(pytest_junit_report)
    assert [row["test"] for row in rows] == [
        "tests.test_a#test_failed[param-a]",
        "tests.test_a#test_error",
    ]
    assert "private medical" not in json.dumps(rows)
    assert rows == jira_sync.failures(pytest_junit_report.parent)


def test_missing_reports_fail_explicitly(tmp_path: Path) -> None:
    with pytest.raises(jira_sync.JiraError, match="No pytest JUnit XML"):
        jira_sync.failures(tmp_path)


def test_dry_run_does_not_call_jira(capsys) -> None:
    jira_sync.report(None, "AQT", [{"test": "A#b"}], apply=False)
    assert '"mode": "dry-run"' in capsys.readouterr().out


def test_existing_open_failure_is_not_created_again(capsys) -> None:
    jira = FakeJira(["fingerprint"])
    jira_sync.report(jira, "AQT", [{"label": "fingerprint"}], apply=True)
    assert jira.created == []
    assert "Already tracked" in capsys.readouterr().out


def test_duplicate_rows_create_only_one_bug(capsys) -> None:
    jira = FakeJira()
    row = {"label": "f1", "test": "A#b", "error_type": "AssertionError", "report": "junit.xml"}
    jira_sync.report(jira, "AQT", [row, row], apply=True)
    assert len(jira.created) == 1
    fields = jira.created[0]["fields"]
    assert fields["project"]["key"] == "AQT"
    assert fields["issuetype"]["name"] == "Bug"
    assert fields["description"]["type"] == "doc"
    capsys.readouterr()


def test_environment_file_keeps_existing_secrets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JIRA_API_TOKEN", "ci")
    env_file = tmp_path / ".env"
    env_file.write_text("JIRA_API_TOKEN=local\nJIRA_PROJECT_KEY=AQT\n", encoding="utf-8")
    jira_sync.load_env(env_file)
    assert os.environ["JIRA_API_TOKEN"] == "ci"


def test_paginates_search() -> None:
    jira = object.__new__(jira_sync.Jira)
    responses = [
        {"issues": [{"key": "AQT-1"}], "nextPageToken": "next", "isLast": False},
        {"issues": [{"key": "AQT-2"}], "isLast": True},
    ]
    calls = []

    def request(method, path, data):
        calls.append(data)
        return responses.pop(0)

    jira.request = request
    assert len(list(jira.search("project = AQT", ["summary"]))) == 2
    assert calls[1]["nextPageToken"] == "next"


def test_scoped_gateway_and_basic_auth(monkeypatch) -> None:
    monkeypatch.setenv("JIRA_SITE_URL", "https://aiqatesting.atlassian.net")
    monkeypatch.setenv("JIRA_CLOUD_ID", "12345678-1234-1234-1234-123456789abc")
    monkeypatch.setenv("JIRA_EMAIL", "qa@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "secret")
    jira = jira_sync.Jira()
    assert "api.atlassian.com/ex/jira/" in jira.base
    assert jira.auth.startswith("Basic ")
