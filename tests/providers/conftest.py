from typing import Any

import pytest

from promptum.providers import Metrics, RetryConfig
from promptum.providers.retry import RetryStrategy


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


@pytest.fixture
def successful_api_response() -> dict[str, Any]:
    return {
        "choices": [{"message": {"content": "Hello, world!"}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "total_cost": 0.001,
        },
    }


@pytest.fixture
def minimal_api_response() -> dict[str, Any]:
    return {
        "choices": [{"message": {"content": "Hello, world!"}}],
    }


@pytest.fixture
def no_retry_config() -> RetryConfig:
    return RetryConfig(max_attempts=1)


@pytest.fixture
def retry_config_3_attempts() -> RetryConfig:
    return RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        initial_delay=0.01,
        max_delay=0.1,
        exponential_base=2.0,
    )
