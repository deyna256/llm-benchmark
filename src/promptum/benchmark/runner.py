import asyncio
from collections.abc import Callable, Sequence

import httpx

from promptum.benchmark.result import TestResult
from promptum.benchmark.test_case import TestCase
from promptum.providers.protocol import LLMProvider


class Runner:
    def __init__(
        self,
        provider: LLMProvider,
        max_concurrent: int = 5,
        progress_callback: Callable[[int, int, TestResult], None] | None = None,
    ):
        self.provider = provider
        self.max_concurrent = max_concurrent
        self.progress_callback = progress_callback

    async def run(self, test_cases: Sequence[TestCase]) -> list[TestResult]:
        semaphore = asyncio.Semaphore(self.max_concurrent)
        completed = 0
        total = len(test_cases)

        async def run_with_semaphore(test_case: TestCase) -> TestResult:
            async with semaphore:
                result = await self._run_single_test(test_case)

                nonlocal completed
                completed += 1
                if self.progress_callback:
                    self.progress_callback(completed, total, result)

                return result

        results = await asyncio.gather(
            *[run_with_semaphore(tc) for tc in test_cases],
        )

        return list(results)

    async def _run_single_test(self, test_case: TestCase) -> TestResult:
        try:
            response, metrics = await self.provider.generate(
                prompt=test_case.prompt,
                model=test_case.model,
                system_prompt=test_case.system_prompt,
                temperature=test_case.temperature,
                max_tokens=test_case.max_tokens,
                retry_config=test_case.retry_config,
            )

            passed, validation_details = test_case.validator.validate(response)

            return TestResult(
                test_case=test_case,
                response=response,
                passed=passed,
                metrics=metrics,
                validation_details=validation_details,
                execution_error=None,
            )

        except (RuntimeError, ValueError, TypeError, httpx.HTTPError) as e:
            return TestResult(
                test_case=test_case,
                response=None,
                passed=False,
                metrics=None,
                validation_details={},
                execution_error=str(e),
            )
