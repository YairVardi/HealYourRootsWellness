# HealYourRootsWellness Automation

Python 3.10+ automation for `https://healyourrootswellness.com` using the synchronous Playwright API, pytest, pytest-playwright, Page Objects, requests, Allure and pytest JUnit XML.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement requirements.txt
python -m playwright install chromium firefox
```

The dependency versions in `requirements.txt` are pinned. Copy `.env.example` to `.env` only if no local `.env` already exists; never overwrite the existing private file.

## Run

```bash
# Safe unit tests
pytest tests/unit

# Collection only
pytest --collect-only

# Chromium UI suite (headless by default)
pytest tests/ui --browser chromium

# Firefox UI suite
pytest tests/ui --browser firefox

# Headed execution and alternate target
pytest tests/ui --browser chromium --headed --base-url https://healyourrootswellness.com
```

Every pytest-playwright test receives a new browser context. Failure screenshots and retained traces are written to a timestamped `artifacts/<run-id>/playwright` directory unless `--output` is supplied.

## Reports

Use a unique output directory for each run so stale results cannot be published:

```bash
RUN_ID="local-$(date -u +%Y%m%dT%H%M%SZ)"
pytest tests \
  --browser chromium \
  --output "artifacts/$RUN_ID/playwright" \
  --junitxml "artifacts/$RUN_ID/junit.xml" \
  --alluredir "artifacts/$RUN_ID/allure-results" --clean-alluredir
```

The JUnit XML is suitable for Jenkins and the Jira bridge. Generate or open an Allure report with your installed Allure CLI.

## Configuration

Environment variables override `.env` values. Important settings are `BASE_URL`, `API_BASE_URL`, `BROWSER`, `HEADLESS`, `DEFAULT_TIMEOUT_MS`, `EXPECT_TIMEOUT_MS`, member API settings, and the disabled-by-default destructive investigation settings documented in `.env.example`. `OPENAI_API_KEY` and `OPENAI_MODEL` are optional and are used only when failure analysis is explicitly enabled.

Member registration tests create synthetic accounts and are skipped unless both `RUN_MUTATING_API_TESTS=true` and `MEMBER_TEST_PASSWORD` are set. Consultation submissions are intercepted by Playwright mocks. The delete/deactivate investigation has separate enablement, exact acknowledgement, candidate and account-id guards.

## Test Layout

- `automation/pages`: synchronous Playwright Page Objects and components
- `automation/mocks.py`: deterministic consultation API routes and captured submissions
- `automation/api.py`: member clients, assertions, response extraction and guarded registry
- `tests/ui`: migrated client, therapist, navigation, forms, responsive and security coverage
- `tests/api`: synthetic member registration, verification and disabled delete investigation
- `tests/unit`: configuration, API utility and Jira parser/deduplication tests
- `docs/MIGRATION.md`: Java-to-Python coverage mapping and known selector/xfail inventory

## Jira

The optional Jira bridge reads only final failures/errors from pytest JUnit XML. Dry-run reporting performs no network request:

```bash
python scripts/jira_sync.py report --reports artifacts/<run-id>/junit.xml
```

See `docs/JIRA.md` before using `--apply`. The Jira bridge remains deterministic and does not invoke the failure analyzer.

## Failure Analysis

Failure analysis is a separate, review-only command. It never changes tests or Jira issues and defaults to deterministic offline analysis:

```bash
python scripts/failure_analysis.py \
  --report artifacts/<run-id>/junit.xml \
  --output-dir artifacts/<run-id>/failure-analysis
```

To opt in to the OpenAI provider, configure both environment variables and add `--use-openai`. No default model is assumed:

```bash
export OPENAI_API_KEY='<secret>'
export OPENAI_MODEL='<model-id>'
python scripts/failure_analysis.py \
  --report artifacts/<run-id>/junit.xml \
  --output-dir artifacts/<run-id>/failure-analysis \
  --use-openai
```

For a fully offline provider demonstration, use the checked-in synthetic fixtures:

```bash
python scripts/failure_analysis.py \
  --report artifacts/<run-id>/junit.xml \
  --output-dir artifacts/<run-id>/failure-analysis \
  --response-fixture tests/fixtures/failure_analysis/provider_response.json
```

The command reads exactly one selected JUnit report. Optional `--diagnostic` inputs must be bounded UTF-8 `.txt` or `.log` files inside that report's build directory. Screenshots, traces and page dumps are not uploaded. Common secrets and personal data are redacted before provider use and artifact generation.

Validated `failure-analysis.json` and readable `failure-analysis.md` files are written below the selected build directory. Results are cached by report content, diagnostics, provider/model and prompt version. Use `--force` only for intentional re-analysis. The provider makes at most one request with no SDK retries, a 20-second timeout and a 2,500-token output limit. Without credentials, after provider errors, or after invalid output, deterministic `unknown`/`unexpected_pass` analysis is produced.

The implementation follows the official OpenAI Python SDK and Responses API structured-output guidance: https://developers.openai.com/api/docs/guides/structured-outputs

## Jenkins Inline Pipeline

Jenkins uses the local `PROJECT_DIR`, defaulting to `/Users/yairvardi/Documents/Automation/HealYourRootsWellness`. The inline pipeline contains no SCM checkout step. It creates `.venv`, installs pinned dependencies and Chromium/Firefox, runs pytest, publishes the current run's JUnit and Allure results, and archives Playwright artifacts.

`REPORT_TO_JIRA` is false by default. When enabled after failed tests, Jenkins uses Username/Password credential `jira-aqt` (username: Atlassian email, password: scoped API token). Jira reporting cannot replace the pytest exit status, and it is skipped when setup fails before a current-run JUnit file exists.

`ANALYZE_FAILURES` is also false by default. To enable hosted analysis, create a separate Jenkins **Secret text** credential containing the OpenAI API key, normally with ID `openai-api-key`; set `OPENAI_API_KEY_CREDENTIAL_ID` if a different ID is used, and set `OPENAI_MODEL` to a model available to the account. Jenkins binds the key only around the analysis command, does not read the local `.env`, archives only sanitized analysis outputs, and preserves pytest's result even when analysis fails. Existing Jira publication remains independent and unchanged.
