from llm_benchmark.core import Metrics


def test_metrics_creation(basic_metrics: Metrics) -> None:
    assert basic_metrics.latency_ms == 150.5
    assert basic_metrics.prompt_tokens == 10
    assert basic_metrics.completion_tokens == 20
    assert basic_metrics.total_tokens == 30
    assert basic_metrics.cost_usd == 0.001
    assert basic_metrics.total_attempts == 1


def test_metrics_with_retries() -> None:
    metrics = Metrics(latency_ms=200.0, retry_delays=(1.0, 2.0))
    assert metrics.total_attempts == 3
    assert len(metrics.retry_delays) == 2


def test_metrics_without_cost() -> None:
    metrics = Metrics(latency_ms=100.0)
    assert metrics.cost_usd is None
    assert metrics.prompt_tokens is None
