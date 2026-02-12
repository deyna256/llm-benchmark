import asyncio
from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from promptum.providers.metrics import Metrics
from promptum.session.case import Prompt
from promptum.session.runner import Runner


async def test_run_single_passing_test(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    runner = Runner(provider=mock_provider)

    results = await runner.run([sample_prompt])

    assert len(results) == 1
    result = results[0]
    assert result.passed is True
    assert result.response == "test response"
    assert result.execution_error is None
    assert result.validation_details == {"matched": True}
    assert result.timestamp.tzinfo == UTC


async def test_run_single_failing_validation(
    mock_provider: AsyncMock,
    failing_prompt: Prompt,
):
    runner = Runner(provider=mock_provider)

    results = await runner.run([failing_prompt])

    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].response == "test response"
    assert results[0].execution_error is None


async def test_run_passes_correct_arguments_to_provider(
    mock_provider: AsyncMock,
    passing_validator: MagicMock,
):
    prompt = Prompt(
        name="detailed",
        prompt="Tell me a joke",
        model="gpt-4",
        validator=passing_validator,
        system_prompt="You are a comedian",
        temperature=0.7,
        max_tokens=100,
    )
    runner = Runner(provider=mock_provider)

    await runner.run([prompt])

    mock_provider.generate.assert_awaited_once_with(
        prompt="Tell me a joke",
        model="gpt-4",
        system_prompt="You are a comedian",
        temperature=0.7,
        max_tokens=100,
        retry_config=None,
    )


async def test_run_empty_test_cases_returns_empty_list(mock_provider: AsyncMock):
    runner = Runner(provider=mock_provider)

    results = await runner.run([])

    assert results == []


@pytest.mark.parametrize(
    "exception",
    [
        RuntimeError("API down"),
        ValueError("bad value"),
        TypeError("wrong type"),
        httpx.HTTPError("connection failed"),
    ],
    ids=["RuntimeError", "ValueError", "TypeError", "HTTPError"],
)
async def test_run_provider_exception_returns_error_result(
    sample_prompt: Prompt,
    exception: Exception,
):
    provider = AsyncMock()
    provider.generate.side_effect = exception
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert len(results) == 1
    result = results[0]
    assert result.passed is False
    assert result.response is None
    assert result.metrics is None
    assert str(exception) in result.execution_error


async def test_run_progress_callback_called_for_each_test(
    mock_provider: AsyncMock,
    passing_validator: MagicMock,
):
    callback = MagicMock()
    prompts = [
        Prompt(name=f"test-{i}", prompt=f"p{i}", model="m", validator=passing_validator)
        for i in range(3)
    ]
    runner = Runner(provider=mock_provider, progress_callback=callback)

    await runner.run(prompts)

    assert callback.call_count == 3
    for call_args in callback.call_args_list:
        completed, total, result = call_args[0]
        assert total == 3
        assert 1 <= completed <= 3


async def test_run_respects_max_concurrent_limit(
    passing_validator: MagicMock,
):
    peak = 0
    current = 0
    lock = asyncio.Lock()

    async def slow_generate(**kwargs):
        nonlocal peak, current
        async with lock:
            current += 1
            if current > peak:
                peak = current
        await asyncio.sleep(0.05)
        async with lock:
            current -= 1
        return ("response", Metrics(latency_ms=50.0))

    provider = AsyncMock()
    provider.generate.side_effect = slow_generate
    prompts = [
        Prompt(name=f"t-{i}", prompt=f"p{i}", model="m", validator=passing_validator)
        for i in range(10)
    ]
    runner = Runner(provider=provider, max_concurrent=3)

    await runner.run(prompts)

    assert peak <= 3
