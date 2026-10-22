#!/usr/bin/env python3
"""Jira Cloud bridge for pytest JUnit XML reports (Python 3.9+)."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
import xml.etree.ElementTree as ET


class JiraError(Exception):
    pass


def load_env(path):
    """Load literal KEY=value entries; never evaluate shell code or override CI secrets."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep and re.fullmatch(r"[A-Z][A-Z0-9_]*", key.strip()):
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Jira:
    def __init__(self):
        required = ("JIRA_SITE_URL", "JIRA_CLOUD_ID", "JIRA_EMAIL", "JIRA_API_TOKEN")
        missing = [key for key in required if not os.environ.get(key, "").strip()]
        if missing:
            raise JiraError("Missing settings: " + ", ".join(missing))
        site = urlparse(os.environ["JIRA_SITE_URL"])
        if (site.scheme != "https" or not site.hostname
                or not re.fullmatch(r"[a-z0-9-]+\.atlassian\.net", site.hostname)
                or site.username or site.password or site.port):
            raise JiraError("JIRA_SITE_URL must be your HTTPS *.atlassian.net site.")
        cloud = os.environ["JIRA_CLOUD_ID"].strip()
        if not re.fullmatch(r"[a-fA-F0-9-]{36}", cloud):
            raise JiraError("JIRA_CLOUD_ID must be the cloudId from /_edge/tenant_info.")
        self.site = "https://" + site.hostname
        self.base = "https://api.atlassian.com/ex/jira/" + cloud + "/rest/api/3"
        raw = os.environ["JIRA_EMAIL"] + ":" + os.environ["JIRA_API_TOKEN"]
        self.auth = "Basic " + base64.b64encode(raw.encode()).decode()
        self.opener = build_opener(NoRedirect())

    def request(self, method, path, data=None):
        req = Request(self.base + path,
                      data=json.dumps(data).encode() if data is not None else None,
                      headers={"Authorization": self.auth, "Accept": "application/json",
                               "Content-Type": "application/json"}, method=method)
        try:
            with self.opener.open(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            # Do not log response bodies: they may contain credentials or private data.
            raise JiraError("Jira HTTP %s. Check token scopes, cloud ID, project access "
                            "and required issue fields." % exc.code) from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise JiraError("Jira request failed; check connectivity. "
                            "A failed create may have succeeded: verify Jira before retrying.") from None

    def search(self, jql, fields):
        token = None
        seen = set()
        while True:
            body = {"jql": jql, "maxResults": 100, "fields": fields}
            if token:
                body["nextPageToken"] = token
            result = self.request("POST", "/search/jql", body)
            yield from result.get("issues", [])
            token = result.get("nextPageToken")
            if result.get("isLast", not token) or not token:
                return
            if token in seen:
                raise JiraError("Jira search returned a repeated pagination token.")
            seen.add(token)


def project_key(value):
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", value):
        raise JiraError("Invalid project key.")
    return value


def failures(directory):
    report_path = Path(directory)
    files = [report_path] if report_path.is_file() else sorted(report_path.glob("*.xml"))
    if not files:
        raise JiraError("No pytest JUnit XML reports found. Run pytest with --junitxml first.")
    found = {}
    for path in files:
        root = ET.parse(path).getroot()
        for case in root.iter("testcase"):
            failure = case.find("failure")
            if failure is None:
                failure = case.find("error")
            if failure is None:
                continue
            identity = case.get("classname", "") + "#" + case.get("name", "")
            # Stable across builds; distinct parameterized test names remain distinct.
            label = "qa-failure-" + hashlib.sha256(identity.encode()).hexdigest()[:24]
            found[label] = {
                "label": label, "test": identity,
                "error_type": failure.get("type", "Test failure"),
                "report": path.name,
            }
    return list(found.values())


def report(jira, project, items, apply=False):
    if not apply:
        print(json.dumps({"mode": "dry-run", "failure_count": len(items), "failures": items},
                         indent=2))
        return
    issue_type = os.environ.get("JIRA_ISSUE_TYPE", "Bug").strip()
    if not issue_type:
        raise JiraError("JIRA_ISSUE_TYPE cannot be empty.")
    # One search avoids eventual-consistency gaps within this run.
    existing = set()
    for issue in jira.search('project = "%s" AND labels = "qa-automation" '
                             'AND statusCategory != Done' % project, ["labels"]):
        existing.update(issue.get("fields", {}).get("labels", []))
    for item in items:
        if item["label"] in existing:
            print("Already tracked: " + item["label"])
            continue
        # Keep raw stack traces, test data and assertion messages in the local/CI
        # reports; they may contain patient, login or other private information.
        lines = [
            "Automated test failure; requires triage before classifying as a product defect.",
            "Test: " + item["test"],
            "Failure type: " + item["error_type"],
            "Pytest JUnit report: " + item["report"],
            "Review the JUnit, Playwright and Allure artifacts for expected/actual results and reproduction.",
        ]
        description = {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": line}]}
            for line in lines
        ]}
        payload = {"fields": {"project": {"key": project},
                             "issuetype": {"name": issue_type},
                             "summary": ("[Automation] " + item["test"])[:255],
                             "description": description,
                             "labels": ["qa-automation", item["label"]]}}
        result = jira.request("POST", "/issue", payload)
        existing.add(item["label"])
        print("Created: " + jira.site + "/browse/" + result["key"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Verify account and project access without writes.")
    sub.add_parser("issues", help="Read project requirements/tasks as JSON.")
    rpt = sub.add_parser("report", help="Preview or publish failures from pytest JUnit XML.")
    rpt.add_argument("--reports", default="artifacts/junit.xml")
    rpt.add_argument("--apply", action="store_true", help="Actually create Jira issues.")
    args = parser.parse_args()
    load_env(args.env_file)
    try:
        project = project_key(os.environ.get("JIRA_PROJECT_KEY", "AQT"))
        if args.command == "report":
            items = failures(args.reports)
            if not args.apply:
                report(None, project, items)
                return 0
            if not items:
                print("No test failures to report.")
                return 0
        jira = Jira()
        if args.command == "check":
            jira.request("GET", "/myself")
            jira.request("GET", "/project/" + project)
            print("Connected to Jira project " + project + ". No issues created.")
        elif args.command == "issues":
            print(json.dumps(list(jira.search('project = "%s" ORDER BY updated DESC' % project,
                                             ["summary", "description", "status", "issuetype"])),
                             ensure_ascii=False, indent=2))
        else:
            report(jira, project, items, args.apply)
        return 0
    except (JiraError, ET.ParseError, OSError) as exc:
        # Parser/OS exception messages can include report content; keep those generic.
        print(str(exc) if isinstance(exc, JiraError) else "Could not read test report files.",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
