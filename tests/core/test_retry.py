from llm_benchmark.core import RetryConfig, RetryStrategy


def test_retry_config_defaults(default_retry_config: RetryConfig) -> None:
    assert default_retry_config.max_attempts == 3
    assert default_retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
    assert default_retry_config.initial_delay == 1.0
    assert default_retry_config.max_delay == 60.0
    assert default_retry_config.exponential_base == 2.0


def test_retry_config_custom() -> None:
    config = RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.FIXED_DELAY,
        initial_delay=2.0,
    )
    assert config.max_attempts == 5
    assert config.strategy == RetryStrategy.FIXED_DELAY
    assert config.initial_delay == 2.0
