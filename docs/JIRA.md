# Jira connection for AI QA Testing

This bridge reads pytest JUnit XML. It is a deterministic API integration; it
does not add an LLM or autonomous agent.

## Local setup

1. Install Python 3.9+.
2. Copy .env.example to .env if you do not already have a local .env.
   Otherwise add the Jira keys to it without overwriting existing settings.
3. Open https://aiqatesting.atlassian.net/_edge/tenant_info in your browser.
   Copy cloudId into JIRA_CLOUD_ID.
4. Set JIRA_EMAIL to the Atlassian account that created the token, and
   JIRA_API_TOKEN to the scoped token. Keep JIRA_PROJECT_KEY=AQT.
5. Ensure AQT has a Bug work type, or set JIRA_ISSUE_TYPE to its actual name.
   Required custom fields need additional mapping in the script.

Required classic scopes: read:jira-work, write:jira-work, read:jira-user.
The account must have permission to browse AQT and create issues there.
Scoped tokens use the api.atlassian.com/ex/jira/{cloudId} gateway and
email/token Basic auth. The script loads literal .env entries, never runs
shell code, and preserves already-set CI environment variables.

Keep the token in the ignored .env file or Jenkins credentials. Do not put
it in source code, shell arguments, screenshots, or GitHub.

## Verify and read tasks

Run from the repository root:

```bash
python3 scripts/jira_sync.py check
python3 scripts/jira_sync.py issues
```

Check verifies the account and project without writes. Issues prints project
issues with descriptions/requirements as paginated JSON. This does not
implement automatic test generation.

## Preview and publish

Run pytest with a unique JUnit destination, then preview its final failures:

```bash
pytest tests --junitxml artifacts/local/junit.xml
python3 scripts/jira_sync.py report --reports artifacts/local/junit.xml
```

Preview needs no token and makes no network calls. After reviewing it:

```bash
python3 scripts/jira_sync.py report --reports artifacts/local/junit.xml --apply
```

Only final failure/error test cases are reported. Passed, skipped, and
recovered flaky attempts are excluded. A stable class/name fingerprint and
the qa-automation label identify each failure. Existing non-Done issues
prevent duplicates; a recurrence after closure creates a new issue.
Serialize reporting jobs: deduplication is best-effort, not an atomic lock,
and Jira search indexing can lag. Creates are never automatically retried.
After a timeout, inspect Jira before rerunning.

Bugs contain the test identity, exception type, report filename, and a
request to triage the failure. A test failure is not automatically classified
as a product defect. Stack traces, assertion messages, screenshots and test
data remain in local/CI JUnit, Playwright and Allure artifacts. Check that test names
do not contain private data either.

Missing reports fail explicitly. Clean stale reports before each test run
(the Jenkinsfile does this). API failures exit nonzero and do not print the
token or response body.

## Jenkins setup

1. Install Python 3.9+ on the agent.
2. Create a Username with password credential, ID: jira-aqt.
   Username = Atlassian email; password = scoped API token.
3. Use this branch's Jenkinsfile and set JIRA_CLOUD_ID in Build with Parameters.
4. Enable REPORT_TO_JIRA when you want failed tests published to Jira.

Reporting is disabled by default. The post-build step uses masked credential
environment variables and runs even after test failure. A reporting error
marks an otherwise successful build unstable; an existing failure stays
failed. JUnit/Allure publication remains enabled.

## Offline verification

```bash
pytest tests/unit/test_jira_sync.py
```

No live service, credentials or browser is used by these unit tests.

## API references

- https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
- https://support.atlassian.com/jira/kb/retrieve-my-atlassian-sites-cloud-id/
- https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
- https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
