from datetime import datetime

import pytest

from promptum.providers import Metrics
from promptum.session import Prompt, Report, TestResult
from promptum.validation import Contains


@pytest.fixture
def sample_results() -> list[TestResult]:
    return [
        TestResult(
            test_case=Prompt(
                name="test1",
                prompt="prompt",
                model="model1",
                validator=Contains("test"),
                tags=("math", "easy"),
            ),
            response="test response",
            passed=True,
            metrics=Metrics(latency_ms=100.0, cost_usd=0.01),
            validation_details={},
            timestamp=datetime.now(),
        ),
        TestResult(
            test_case=Prompt(
                name="test2",
                prompt="prompt",
                model="model1",
                validator=Contains("test"),
                tags=("geography",),
            ),
            response="fail response",
            passed=False,
            metrics=Metrics(latency_ms=150.0, cost_usd=0.02),
            validation_details={},
            timestamp=datetime.now(),
        ),
        TestResult(
            test_case=Prompt(
                name="test3",
                prompt="prompt",
                model="model2",
                validator=Contains("test"),
                tags=("math",),
            ),
            response="test response",
            passed=True,
            metrics=Metrics(latency_ms=120.0, cost_usd=0.015),
            validation_details={},
            timestamp=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_report(sample_results: list[TestResult]) -> Report:
    return Report(results=sample_results)
