pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    timeout(time: 60, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  parameters {
    string(name: 'PROJECT_DIR',
            defaultValue: '/Users/yairvardi/Documents/Automation/HealYourRootsWellness',
            description: 'Absolute local project directory. This inline pipeline never checks out SCM.')
    string(name: 'TEST_TARGET', defaultValue: 'tests',
            description: 'Pytest path or node id, for example tests/ui/test_client_flow.py.')
    choice(name: 'BROWSER_NAME', choices: ['chromium', 'firefox'],
            description: 'Playwright browser engine.')
    booleanParam(name: 'HEADLESS', defaultValue: true,
            description: 'Run Playwright without a visible browser window.')
    string(name: 'BASE_URL', defaultValue: 'https://healyourrootswellness.com',
            description: 'Target web base URL.')
    string(name: 'API_BASE_URL', defaultValue: 'https://healyourrootswellness.com',
            description: 'Target API/site base URL.')
    booleanParam(name: 'RUN_MUTATING_API_TESTS', defaultValue: false,
            description: 'Allow synthetic member registration tests. Disabled by default.')
    string(name: 'MEMBER_TEST_PASSWORD_CREDENTIAL_ID', defaultValue: '',
            description: 'Optional Jenkins Secret text credential for synthetic member tests.')
    string(name: 'MEMBER_AUTH_TOKEN_CREDENTIAL_ID', defaultValue: '',
            description: 'Optional Jenkins Secret text credential for member bearer auth.')
    string(name: 'MEMBER_AUTH_COOKIE_CREDENTIAL_ID', defaultValue: '',
            description: 'Optional Jenkins Secret text credential for member cookie auth.')
    string(name: 'MEMBER_TEST_EMAIL_DOMAIN', defaultValue: 'example.com',
            description: 'Domain for generated synthetic member addresses.')
    string(name: 'MEMBER_API_HEADERS', defaultValue: '',
            description: 'Optional non-secret headers separated by semicolons.')
    booleanParam(name: 'MEMBER_DELETE_INVESTIGATION_ENABLED', defaultValue: false,
            description: 'Enable the separately guarded delete/deactivate investigation.')
    string(name: 'MEMBER_DELETE_CANDIDATE', defaultValue: '',
            description: 'Confirmed delete/deactivate candidate name.')
    string(name: 'MEMBER_DELETE_ACCOUNT_ID', defaultValue: '',
            description: 'QA/staging account or seat id for the destructive investigation.')
    booleanParam(name: 'REPORT_TO_JIRA', defaultValue: false,
            description: 'Create AQT triage bugs for final pytest failures.')
    string(name: 'JIRA_CLOUD_ID', defaultValue: '9517b0e4-02fe-40ae-a889-12919f5fa3b4',
            description: 'cloudId from aiqatesting.atlassian.net/_edge/tenant_info.')
    booleanParam(name: 'ANALYZE_FAILURES', defaultValue: false,
            description: 'Generate review-only failure analysis after failed tests. Disabled by default.')
    string(name: 'REANALYZE_REPORT', defaultValue: 'artifacts/jenkins-31/junit.xml',
            description: 'Existing report for analysis only. Clear this field for regular test runs; requires updated failure_analysis.py.')
    booleanParam(name: 'OPENAI_CHECK_ONLY', defaultValue: true,
            description: 'Run one paid OpenAI structured-output connection check; skip pytest, Jira and failure analysis.')
    string(name: 'OPENAI_MODEL', defaultValue: 'gpt-5.6-terra',
            description: 'OpenAI model ID. Account access is verified by OPENAI_CHECK_ONLY.')
    string(name: 'OPENAI_API_KEY_CREDENTIAL_ID', defaultValue: 'openai-api-key',
            description: 'Jenkins Secret Text credential ID for the OpenAI API key.')
  }

  environment {
    CI = 'true'
    PROJECT_NAME = 'HealYourRootsWellness'
    FRAMEWORK_NAME = 'Python Playwright'
    LANGUAGE_NAME = 'Python'
    PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
  }

  stages {
    stage('Select Workspace') {
      steps {
        script {
          env.OPENAI_CHECK_MODE = (params.OPENAI_CHECK_ONLY == null || params.OPENAI_CHECK_ONLY) ? 'true' : 'false'
          // On the first run Jenkins may not have registered the new parameter yet.
          def sourceReport = params.REANALYZE_REPORT == null ? 'artifacts/jenkins-31/junit.xml' : (params.REANALYZE_REPORT.trim())
          if (sourceReport) {
            if (!(sourceReport ==~ /artifacts\/jenkins-[0-9]+\/junit\.xml/)) {
              error('REANALYZE_REPORT must look like artifacts/jenkins-31/junit.xml.')
            }
            env.OPENAI_CHECK_MODE = 'replay'
            env.SOURCE_REPORT = sourceReport
            env.REANALYSIS_OUTPUT = sourceReport.substring(0, sourceReport.lastIndexOf('/')) + "/failure-analysis-recheck-${env.BUILD_NUMBER}"
          }
          env.PROJECT_ROOT = params.PROJECT_DIR.trim()
          if (!env.PROJECT_ROOT) {
            error('PROJECT_DIR must be an absolute local project directory.')
          }
          env.RUN_ROOT = "artifacts/jenkins-${env.BUILD_NUMBER}"
          env.JUNIT_XML = "${env.RUN_ROOT}/junit.xml"
          env.ALLURE_RESULTS_DIR = "${env.RUN_ROOT}/allure-results"
          env.PLAYWRIGHT_OUTPUT_DIR = "${env.RUN_ROOT}/playwright"
          env.TEST_RUN_ID = "jenkins-${env.BUILD_NUMBER}"
        }
      }
    }

    stage('Check OpenAI Connection') {
      when { expression { return env.OPENAI_CHECK_MODE == 'true' } }
      steps {
        dir(env.PROJECT_ROOT) {
          script {
            def model = params.OPENAI_MODEL?.trim() ?: 'gpt-5.6-terra'
            def credentialId = params.OPENAI_API_KEY_CREDENTIAL_ID?.trim()
            if (!model || !credentialId) {
              error('OPENAI_MODEL and OPENAI_API_KEY_CREDENTIAL_ID are required.')
            }
            withEnv(["OPENAI_MODEL=${model}"]) {
              withCredentials([string(credentialsId: credentialId,
                      variable: 'OPENAI_API_KEY')]) {
                timeout(time: 1, unit: 'MINUTES') {
                  sh '''
set +x
set -eu
mkdir -p "${RUN_ROOT}"
.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
from typing import Literal

result_path = Path(os.environ["RUN_ROOT"]) / "openai-connection.json"
result = {"check": "structured_output_connection", "success": False}

try:
    from openai import OpenAI
    from pydantic import BaseModel

    class ConnectionResult(BaseModel):
        status: Literal["ok"]

    with OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url="https://api.openai.com/v1",
        timeout=20.0,
        max_retries=0,
    ) as client:
        response = client.responses.parse(
            model=os.environ["OPENAI_MODEL"],
            instructions='This is a connection check. Return status "ok".',
            input='Confirm the connection using the required structured format.',
            text_format=ConnectionResult,
            max_output_tokens=4096,
            store=False,
        )
    if response.output_parsed is None or response.output_parsed.status != "ok":
        raise ValueError("No valid structured response")
    result["success"] = True
except Exception as exc:
    # Never log the exception body, response, environment or credential value.
    status_code = getattr(exc, "status_code", None)
    if type(status_code) is int:
        result["http_status"] = status_code
    hints = {
        "AuthenticationError": "Check the Jenkins API key credential.",
        "PermissionDeniedError": "Check API project permissions and model access.",
        "NotFoundError": "Check the model ID and account access.",
        "RateLimitError": "Check API billing, quota and rate limits.",
        "APITimeoutError": "The request exceeded the 20-second timeout.",
        "APIConnectionError": "Check network access and Python SSL certificates.",
        "ModuleNotFoundError": "Install the project requirements in .venv.",
    }
    hint = hints.get(type(exc).__name__, "Check the SDK, request settings and structured output.")
    result["hint"] = hint
    result_path.write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
    print("OPENAI_CONNECTION_FAILED: " + hint)
    if type(status_code) is int:
        print("HTTP status: " + str(status_code))
    raise SystemExit(1)

result_path.write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
print("OPENAI_CONNECTION_OK: live structured response validated.")
print("This confirms API access, not failure-analysis quality.")
PY
                  '''
                }
              }
            }
          }
        }
      }
    }

    stage('Reanalyze Existing Report') {
      when { expression { return env.OPENAI_CHECK_MODE == 'replay' } }
      steps {
        dir(env.PROJECT_ROOT) {
          script {
            if (!fileExists(env.SOURCE_REPORT)) {
              error('The selected existing JUnit report was not found.')
            }
            def credentialId = params.OPENAI_API_KEY_CREDENTIAL_ID?.trim()
            if (!credentialId) { error('An OpenAI credential ID is required.') }
            withEnv(["OPENAI_MODEL=${params.OPENAI_MODEL?.trim() ?: 'gpt-5.6-terra'}"]) {
              withCredentials([string(credentialsId: credentialId, variable: 'OPENAI_API_KEY')]) {
                timeout(time: 1, unit: 'MINUTES') {
                  sh '''
                    set +x
                    set -eu
                    .venv/bin/python scripts/failure_analysis.py \
                      --report "${SOURCE_REPORT}" \
                      --output-dir "${REANALYSIS_OUTPUT}" \
                      --use-openai --require-openai --force \
                      --env-file /dev/null
                  '''
                }
              }
            }
          }
        }
      }
    }

    stage('Prepare Python') {
      when { expression { return env.OPENAI_CHECK_MODE == 'false' } }
      steps {
        dir(env.PROJECT_ROOT) {
          sh '''
            set -eu
            rm -rf "${RUN_ROOT}"
            mkdir -p "${RUN_ROOT}" "${ALLURE_RESULTS_DIR}" "${PLAYWRIGHT_OUTPUT_DIR}"
            python3 --version
            python3 -m venv .venv
            .venv/bin/python -m pip install --upgrade pip
            .venv/bin/python -m pip install --requirement requirements.txt
            .venv/bin/python -m playwright install chromium firefox
          '''
        }
      }
    }

    stage('Run pytest') {
      when { expression { return env.OPENAI_CHECK_MODE == 'false' } }
      steps {
        dir(env.PROJECT_ROOT) {
          script {
            def credentials = []
            if (params.MEMBER_TEST_PASSWORD_CREDENTIAL_ID?.trim()) {
              credentials << string(credentialsId: params.MEMBER_TEST_PASSWORD_CREDENTIAL_ID.trim(),
                      variable: 'MEMBER_TEST_PASSWORD')
            }
            if (params.MEMBER_AUTH_TOKEN_CREDENTIAL_ID?.trim()) {
              credentials << string(credentialsId: params.MEMBER_AUTH_TOKEN_CREDENTIAL_ID.trim(),
                      variable: 'MEMBER_AUTH_TOKEN')
            }
            if (params.MEMBER_AUTH_COOKIE_CREDENTIAL_ID?.trim()) {
              credentials << string(credentialsId: params.MEMBER_AUTH_COOKIE_CREDENTIAL_ID.trim(),
                      variable: 'MEMBER_AUTH_COOKIE')
            }

            def runPytest = {
              sh '''
                set -eu
                touch "${RUN_ROOT}/tests-started"
                HEADED_ARG=""
                if [ "${HEADLESS}" != "true" ]; then HEADED_ARG="--headed"; fi
                DELETE_CONFIRMATION=""
                if [ "${MEMBER_DELETE_INVESTIGATION_ENABLED}" = "true" ]; then
                  DELETE_CONFIRMATION="I_UNDERSTAND_THIS_MAY_DELETE_DATA"
                fi
                export BASE_URL API_BASE_URL MEMBER_TEST_EMAIL_DOMAIN MEMBER_API_HEADERS
                export RUN_MUTATING_API_TESTS MEMBER_DELETE_INVESTIGATION_ENABLED
                export MEMBER_DELETE_CANDIDATE MEMBER_DELETE_ACCOUNT_ID
                export MEMBER_DELETE_CONFIRMATION="${DELETE_CONFIRMATION}"
                .venv/bin/python -m pytest "${TEST_TARGET}" \
                  --browser="${BROWSER_NAME}" ${HEADED_ARG} \
                  --base-url="${BASE_URL}" \
                  --output="${PLAYWRIGHT_OUTPUT_DIR}" \
                  --junitxml="${JUNIT_XML}" \
                  --alluredir="${ALLURE_RESULTS_DIR}" --clean-alluredir
              '''
            }

            if (credentials) {
              withCredentials(credentials) { runPytest() }
            } else {
              runPytest()
            }
          }
        }
      }
    }
  }

  post {
    always {
      dir(env.PROJECT_ROOT ?: env.WORKSPACE) {
        script {
          def junitPath = env.JUNIT_XML?.trim()
          def allurePath = env.ALLURE_RESULTS_DIR?.trim()
          def runRoot = env.RUN_ROOT?.trim()
          def testStartedMarker = runRoot ? "${runRoot}/tests-started" : null

          if (junitPath && fileExists(junitPath)) {
            junit testResults: junitPath, allowEmptyResults: false
          } else if (env.OPENAI_CHECK_MODE == 'false') {
            echo 'No current-run JUnit report exists; setup likely failed before pytest.'
          }

          if (allurePath && fileExists(allurePath)) {
            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
              allure includeProperties: false, jdk: '', results: [[path: allurePath]]
            }
          }

          def testRunFailed = ['FAILURE', 'UNSTABLE'].contains(currentBuild.currentResult)
          if ((params.REPORT_TO_JIRA && env.OPENAI_CHECK_MODE == 'false') && testRunFailed && testStartedMarker && junitPath &&
                  fileExists(testStartedMarker) && fileExists(junitPath)) {
            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
              withCredentials([usernamePassword(credentialsId: 'jira-aqt',
                      usernameVariable: 'JIRA_EMAIL', passwordVariable: 'JIRA_API_TOKEN')]) {
                withEnv(['JIRA_SITE_URL=https://aiqatesting.atlassian.net',
                         'JIRA_PROJECT_KEY=AQT', "JIRA_CLOUD_ID=${params.JIRA_CLOUD_ID}"]) {
                  sh '.venv/bin/python scripts/jira_sync.py report --reports "${JUNIT_XML}" --apply'
                }
              }
            }
          } else if ((params.REPORT_TO_JIRA && env.OPENAI_CHECK_MODE == 'false') && !testRunFailed) {
            echo 'Skipping Jira reporting because pytest did not fail.'
          } else if ((params.REPORT_TO_JIRA && env.OPENAI_CHECK_MODE == 'false')) {
            echo 'Skipping Jira reporting because no current-run pytest JUnit report exists.'
          }

          if ((params.ANALYZE_FAILURES && env.OPENAI_CHECK_MODE == 'false') && testRunFailed && testStartedMarker && junitPath &&
                  fileExists(testStartedMarker) && fileExists(junitPath)) {
            def analysisStatus = 0
            def runFallbackAnalysis = {
              sh(returnStatus: true, script: '''
                set +x
                .venv/bin/python scripts/failure_analysis.py \
                  --report "${JUNIT_XML}" \
                  --output-dir "${RUN_ROOT}/failure-analysis" \
                  --env-file /dev/null
              ''')
            }
            def runOpenAIAnalysis = {
              sh(returnStatus: true, script: '''
                set +x
                .venv/bin/python scripts/failure_analysis.py \
                  --report "${JUNIT_XML}" \
                  --output-dir "${RUN_ROOT}/failure-analysis" \
                  --use-openai \
                  --env-file /dev/null
              ''')
            }
            withEnv(["OPENAI_MODEL=${params.OPENAI_MODEL?.trim() ?: 'gpt-5.6-terra'}"]) {
              def credentialId = params.OPENAI_API_KEY_CREDENTIAL_ID?.trim()
              if (credentialId) {
                try {
                  withCredentials([string(credentialsId: credentialId,
                          variable: 'OPENAI_API_KEY')]) {
                    analysisStatus = runOpenAIAnalysis()
                  }
                } catch (ignored) {
                  echo 'OpenAI credential unavailable; writing deterministic fallback analysis.'
                  analysisStatus = runFallbackAnalysis()
                }
              } else {
                echo 'No OpenAI credential ID configured; writing deterministic fallback analysis.'
                analysisStatus = runFallbackAnalysis()
              }
            }
            if (analysisStatus != 0) {
              echo 'Failure analysis did not complete; preserving the existing test and Jira results.'
            }
          } else if ((params.ANALYZE_FAILURES && env.OPENAI_CHECK_MODE == 'false') && !testRunFailed) {
            echo 'Skipping failure analysis because pytest did not fail.'
          } else if (params.ANALYZE_FAILURES && env.OPENAI_CHECK_MODE == 'false') {
            echo 'Skipping failure analysis because no current-run pytest JUnit report exists.'
          }

          if (env.OPENAI_CHECK_MODE == 'replay' && env.REANALYSIS_OUTPUT &&
                  fileExists(env.REANALYSIS_OUTPUT)) {
            archiveArtifacts artifacts: "${env.REANALYSIS_OUTPUT}/**",
                    allowEmptyArchive: false, fingerprint: true
          }
          if (runRoot && fileExists(runRoot)) {
            archiveArtifacts artifacts: "${runRoot}/**", allowEmptyArchive: true,
                    fingerprint: true
          } else if (env.OPENAI_CHECK_MODE != 'replay') {
            echo 'No current-run artifact directory exists.'
          }
        }
      }
    }
  }
}
