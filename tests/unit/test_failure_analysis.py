import importlib.util
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

import pytest


SPEC = importlib.util.spec_from_file_location(
    "failure_analysis", Path(__file__).parents[2] / "scripts" / "failure_analysis.py"
)
failure_analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = failure_analysis
SPEC.loader.exec_module(failure_analysis)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "failure_analysis"


@pytest.fixture
def selected_build(tmp_path: Path) -> tuple[Path, Path]:
    build_dir = tmp_path / "jenkins-999"
    build_dir.mkdir()
    report = build_dir / "junit.xml"
    shutil.copyfile(FIXTURES / "synthetic_junit.xml", report)
    return report, build_dir / "failure-analysis"


class FakeProvider:
    name = "mock_provider"
    model = "mock-model"

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = 0

    def analyze(self, payload):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.response


def fixture_response() -> dict:
    return json.loads((FIXTURES / "provider_response.json").read_text(encoding="utf-8"))


def test_redacts_secrets_and_personal_data() -> None:
    raw = (
        "OPENAI_API_KEY=sk-live-secret-1234567890 "
        "password=hunter2 patient@example.com +1 (555) 123-4567 "
        "Authorization: Bearer abcdefghijklmnop "
        "first_name=Taylor https://example.com/path?token=private"
    )
    redacted = failure_analysis.redact_text(raw)
    for private_value in (
        "sk-live-secret-1234567890",
        "hunter2",
        "patient@example.com",
        "555",
        "abcdefghijklmnop",
        "Taylor",
        "token=private",
    ):
        assert private_value not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_PERSONAL_DATA]" in redacted
    assert "?[REDACTED_QUERY]" in redacted


def test_deterministic_fallback_marks_unknown_and_strict_xpass(
    selected_build: tuple[Path, Path],
) -> None:
    report, output_dir = selected_build
    document = failure_analysis.analyze_report(report, output_dir, environ={})
    assert [item["category"] for item in document["analyses"]] == [
        "unknown",
        "unexpected_pass",
    ]
    assert all(item["hypothesis"].startswith("Hypothesis:") for item in document["analyses"])
    assert all(item["unknowns"] for item in document["analyses"])
    serialized = (output_dir / "failure-analysis.json").read_text(encoding="utf-8")
    for private_value in ("qa.patient@example.com", "sk-synthetic-secret", "555-123-4567"):
        assert private_value not in serialized
    assert (output_dir / "failure-analysis.md").is_file()


def test_offline_fixture_produces_validated_analysis(
    selected_build: tuple[Path, Path],
) -> None:
    report, output_dir = selected_build
    document = failure_analysis.analyze_report(
        report,
        output_dir,
        response_fixture=FIXTURES / "provider_response.json",
        environ={},
    )
    assert document["provider"]["used"] == "offline_fixture"
    assert document["provider"]["status"] == "completed"
    assert document["analyses"][0]["category"] == "suspected_product_bug"
    assert document["analyses"][1]["category"] == "unexpected_pass"


def test_malformed_provider_output_falls_back_safely(
    selected_build: tuple[Path, Path],
) -> None:
    report, output_dir = selected_build
    provider = FakeProvider(response={"analyses": []})
    document = failure_analysis.analyze_report(report, output_dir, provider=provider, environ={})
    assert provider.calls == 1
    assert document["provider"]["used"] == "deterministic_fallback"
    assert document["provider"]["status"].startswith("fallback_provider_error_")
    assert document["analyses"][0]["category"] == "unknown"


def test_provider_timeout_falls_back_safely(selected_build: tuple[Path, Path]) -> None:
    report, output_dir = selected_build
    provider = FakeProvider(error=TimeoutError())
    document = failure_analysis.analyze_report(report, output_dir, provider=provider, environ={})
    assert provider.calls == 1
    assert document["provider"]["status"] == "fallback_provider_error_TimeoutError"
    assert document["analyses"][0]["category"] == "unknown"


def test_missing_openai_credentials_never_attempts_a_request(
    selected_build: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, output_dir = selected_build

    def unexpected_provider(*args, **kwargs):
        raise AssertionError("OpenAI provider must not be created without both settings")

    monkeypatch.setattr(failure_analysis, "OpenAIProvider", unexpected_provider)
    document = failure_analysis.analyze_report(
        report,
        output_dir,
        use_openai=True,
        environ={"OPENAI_MODEL": "configured-by-test"},
    )
    assert document["provider"] == {
        "requested": "openai",
        "used": "deterministic_fallback",
        "status": "fallback_missing_credentials",
        "model": "configured-by-test",
    }


def test_cache_uses_report_model_and_prompt_without_repeating_provider_call(
    selected_build: tuple[Path, Path],
) -> None:
    report, output_dir = selected_build
    provider = FakeProvider(response=fixture_response())
    first = failure_analysis.analyze_report(report, output_dir, provider=provider, environ={})
    second = failure_analysis.analyze_report(report, output_dir, provider=provider, environ={})
    assert provider.calls == 1
    assert first["cache"]["hit"] is False
    assert second["cache"]["hit"] is True
    assert first["cache"]["key"] == second["cache"]["key"]


def test_ungrounded_evidence_is_rejected_and_replaced_by_unknown(
    selected_build: tuple[Path, Path],
) -> None:
    report, output_dir = selected_build
    response = fixture_response()
    response["analyses"][0]["evidence"] = ["A claim that is absent from the report"]
    document = failure_analysis.analyze_report(
        report,
        output_dir,
        provider=FakeProvider(response=response),
        environ={},
    )
    assert document["analyses"][0]["category"] == "unknown"
    assert document["provider"]["used"] == "deterministic_fallback"


def test_diagnostics_must_be_bounded_text_from_same_build(
    selected_build: tuple[Path, Path], tmp_path: Path
) -> None:
    report, output_dir = selected_build
    outside = tmp_path / "outside.log"
    outside.write_text("diagnostic", encoding="utf-8")
    with pytest.raises(failure_analysis.AnalysisError, match="selected build"):
        failure_analysis.analyze_report(
            report,
            output_dir,
            diagnostic_paths=[outside],
            environ={},
        )


def test_openai_provider_uses_one_bounded_structured_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured["parse"] = kwargs
            parsed = failure_analysis.StructuredAnalysisEnvelope.model_validate(fixture_response())
            return SimpleNamespace(output_parsed=parsed)

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    provider = failure_analysis.OpenAIProvider("not-a-real-key", "configured-model")
    result = provider.analyze({"failures": []})
    assert result["analyses"][0]["category"] == "suspected_product_bug"
    assert captured["client"] == {
        "api_key": "not-a-real-key",
        "timeout": failure_analysis.REQUEST_TIMEOUT_SECONDS,
        "max_retries": 0,
    }
    assert captured["parse"]["model"] == "configured-model"
    assert captured["parse"]["max_output_tokens"] == failure_analysis.MAX_OUTPUT_TOKENS
    assert captured["parse"]["store"] is False
    assert captured["parse"]["text_format"] is failure_analysis.StructuredAnalysisEnvelope
