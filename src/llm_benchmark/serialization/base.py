"""Base serializer with shared result serialization logic."""

from typing import Any

from llm_benchmark.core.result import TestResult


class BaseSerializer:
    """
    Base class for serializers with common result serialization logic.

    Subclasses should implement:
    - serialize(report: Report) -> str
    - get_file_extension() -> str
    """

    @staticmethod
    def _serialize_result(result: TestResult) -> dict[str, Any]:
        """Convert TestResult to dictionary representation."""
        return {
            "test_case": {
                "name": result.test_case.name,
                "prompt": result.test_case.prompt,
                "model": result.test_case.model,
                "tags": list(result.test_case.tags),
                "system_prompt": result.test_case.system_prompt,
                "temperature": result.test_case.temperature,
                "max_tokens": result.test_case.max_tokens,
                "metadata": result.test_case.metadata,
                "validator": result.test_case.validator.describe(),
            },
            "response": result.response,
            "passed": result.passed,
            "metrics": {
                "latency_ms": result.metrics.latency_ms,
                "prompt_tokens": result.metrics.prompt_tokens,
                "completion_tokens": result.metrics.completion_tokens,
                "total_tokens": result.metrics.total_tokens,
                "cost_usd": result.metrics.cost_usd,
                "retry_delays": list(result.metrics.retry_delays),
                "total_attempts": result.metrics.total_attempts,
            }
            if result.metrics
            else None,
            "validation_details": result.validation_details,
            "execution_error": result.execution_error,
            "timestamp": result.timestamp.isoformat(),
        }
