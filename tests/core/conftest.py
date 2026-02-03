import pytest

from llm_benchmark.core import Metrics, RetryConfig


@pytest.fixture
def basic_metrics() -> Metrics:
    return Metrics(
        latency_ms=150.5,
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        cost_usd=0.001,
    )


@pytest.fixture
def default_retry_config() -> RetryConfig:
    return RetryConfig()
