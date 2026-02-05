from promptum.benchmark import Report


def test_report_filter_by_model(sample_report: Report) -> None:
    filtered = sample_report.filter(model="model1")

    assert len(filtered.results) == 2
    assert all(r.test_case.model == "model1" for r in filtered.results)


def test_report_filter_by_tags(sample_report: Report) -> None:
    filtered = sample_report.filter(tags=("math",))

    assert len(filtered.results) == 2
    assert all("math" in r.test_case.tags for r in filtered.results)


def test_report_filter_by_passed(sample_report: Report) -> None:
    passed = sample_report.filter(passed=True)
    assert len(passed.results) == 2
    assert all(r.passed for r in passed.results)

    failed = sample_report.filter(passed=False)
    assert len(failed.results) == 1
    assert not failed.results[0].passed


def test_report_filter_combined(sample_report: Report) -> None:
    filtered = sample_report.filter(model="model1", passed=True)

    assert len(filtered.results) == 1
    assert filtered.results[0].test_case.name == "test1"


def test_report_group_by_model(sample_report: Report) -> None:
    grouped = sample_report.group_by(lambda r: r.test_case.model)

    assert len(grouped) == 2
    assert "model1" in grouped
    assert "model2" in grouped
    assert len(grouped["model1"].results) == 2
    assert len(grouped["model2"].results) == 1


