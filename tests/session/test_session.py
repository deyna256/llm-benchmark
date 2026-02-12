from unittest.mock import AsyncMock, MagicMock, patch

from promptum.session.case import Prompt
from promptum.session.report import Report
from promptum.session.session import Session


async def test_add_test_appends_to_internal_list(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    session = Session(provider=mock_provider)

    session.add_test(sample_prompt)

    assert len(session._test_cases) == 1
    assert session._test_cases[0] is sample_prompt


async def test_add_tests_extends_internal_list(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
    failing_prompt: Prompt,
):
    session = Session(provider=mock_provider)

    session.add_tests([sample_prompt, failing_prompt])

    assert len(session._test_cases) == 2


async def test_run_empty_returns_empty_report(mock_provider: AsyncMock):
    session = Session(provider=mock_provider)

    report = await session.run()

    assert isinstance(report, Report)
    assert len(report.results) == 0


async def test_run_returns_report_with_results(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    session = Session(provider=mock_provider)
    session.add_test(sample_prompt)

    report = await session.run()

    assert isinstance(report, Report)
    assert len(report.results) == 1
    assert report.results[0].passed is True


async def test_run_passes_max_concurrent(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    session = Session(provider=mock_provider, max_concurrent=10)
    session.add_test(sample_prompt)

    with patch("promptum.session.session.Runner") as mock_runner_cls:
        mock_runner = AsyncMock()
        mock_runner.run.return_value = []
        mock_runner_cls.return_value = mock_runner

        await session.run()

        mock_runner_cls.assert_called_once_with(
            provider=mock_provider,
            max_concurrent=10,
            progress_callback=None,
        )


async def test_run_passes_progress_callback(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    callback = MagicMock()
    session = Session(provider=mock_provider, progress_callback=callback)
    session.add_test(sample_prompt)

    with patch("promptum.session.session.Runner") as mock_runner_cls:
        mock_runner = AsyncMock()
        mock_runner.run.return_value = []
        mock_runner_cls.return_value = mock_runner

        await session.run()

        mock_runner_cls.assert_called_once_with(
            provider=mock_provider,
            max_concurrent=5,
            progress_callback=callback,
        )
