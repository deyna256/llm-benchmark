from promptum.session import Report


def test_report_summary(sample_report: Report) -> None:
    summary = sample_report.get_summary()

    assert summary.total == 3
    assert summary.passed == 2
    assert summary.failed == 1
    assert summary.pass_rate == 2 / 3
    assert summary.total_cost_usd == 0.045
    assert summary.avg_latency_ms == 123.33333333333333
    assert summary.min_latency_ms == 100.0
    assert summary.max_latency_ms == 150.0
    assert summary.execution_errors == 0
    assert summary.validation_failures == 1


def test_report_summary_empty() -> None:
    report = Report(results=[])
    summary = report.get_summary()

    assert summary.total == 0
    assert summary.passed == 0
    assert summary.failed == 0
    assert summary.pass_rate == 0
    assert summary.total_cost_usd == 0
    assert summary.avg_latency_ms == 0
    assert summary.min_latency_ms == 0
    assert summary.max_latency_ms == 0
    assert summary.execution_errors == 0
    assert summary.validation_failures == 0
