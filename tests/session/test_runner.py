import asyncio
from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import httpx

from promptum.providers.metrics import Metrics
from promptum.session.case import Prompt
from promptum.session.runner import Runner


async def test_run_single_passing_test_returns_passed_result(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    runner = Runner(provider=mock_provider)

    results = await runner.run([sample_prompt])

    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].response == "test response"
    assert results[0].execution_error is None


async def test_run_single_failing_validation_returns_failed_result(
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


async def test_run_multiple_tests_returns_all_results(
    mock_provider: AsyncMock,
    passing_validator: MagicMock,
):
    prompts = [
        Prompt(name=f"test-{i}", prompt=f"prompt-{i}", model="m", validator=passing_validator)
        for i in range(3)
    ]
    runner = Runner(provider=mock_provider)

    results = await runner.run(prompts)

    assert len(results) == 3


async def test_run_empty_test_cases_returns_empty_list(mock_provider: AsyncMock):
    runner = Runner(provider=mock_provider)

    results = await runner.run([])

    assert results == []


async def test_run_provider_runtime_error_returns_error_result(
    sample_prompt: Prompt,
):
    provider = AsyncMock()
    provider.generate.side_effect = RuntimeError("API down")
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert len(results) == 1
    assert results[0].passed is False
    assert "API down" in results[0].execution_error


async def test_run_provider_value_error_returns_error_result(
    sample_prompt: Prompt,
):
    provider = AsyncMock()
    provider.generate.side_effect = ValueError("bad value")
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert results[0].passed is False
    assert "bad value" in results[0].execution_error


async def test_run_provider_type_error_returns_error_result(
    sample_prompt: Prompt,
):
    provider = AsyncMock()
    provider.generate.side_effect = TypeError("wrong type")
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert results[0].passed is False
    assert "wrong type" in results[0].execution_error


async def test_run_provider_http_error_returns_error_result(
    sample_prompt: Prompt,
):
    provider = AsyncMock()
    provider.generate.side_effect = httpx.HTTPError("connection failed")
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert results[0].passed is False
    assert "connection failed" in results[0].execution_error


async def test_run_error_result_has_none_response_and_metrics(
    sample_prompt: Prompt,
):
    provider = AsyncMock()
    provider.generate.side_effect = RuntimeError("boom")
    runner = Runner(provider=provider)

    results = await runner.run([sample_prompt])

    assert results[0].response is None
    assert results[0].metrics is None
    assert results[0].passed is False


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


async def test_run_without_progress_callback_no_error(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    runner = Runner(provider=mock_provider, progress_callback=None)

    results = await runner.run([sample_prompt])

    assert len(results) == 1


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


async def test_run_result_contains_validation_details(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    runner = Runner(provider=mock_provider)

    results = await runner.run([sample_prompt])

    assert results[0].validation_details == {"matched": True}


async def test_run_result_has_timestamp(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
):
    runner = Runner(provider=mock_provider)

    results = await runner.run([sample_prompt])

    assert results[0].timestamp is not None
    assert results[0].timestamp.tzinfo is not None
    assert results[0].timestamp.tzinfo == UTC


async def test_run_mixed_success_and_failure(
    mock_provider: AsyncMock,
    sample_prompt: Prompt,
    failing_prompt: Prompt,
):
    error_provider = AsyncMock()
    error_provider.generate.side_effect = RuntimeError("fail")
    error_prompt = Prompt(
        name="error-prompt",
        prompt="cause error",
        model="m",
        validator=MagicMock(),
    )

    # Use mock_provider for passing and failing prompts
    runner = Runner(provider=mock_provider)
    results = await runner.run([sample_prompt, failing_prompt])

    passed_count = sum(1 for r in results if r.passed)
    failed_count = sum(1 for r in results if not r.passed)
    assert passed_count == 1
    assert failed_count == 1

    # Separate run with error provider
    runner_err = Runner(provider=error_provider)
    error_results = await runner_err.run([error_prompt])
    assert error_results[0].passed is False
    assert error_results[0].execution_error is not None
