from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from promptum.benchmark.test_case import TestCase
from promptum.providers.metrics import Metrics


@dataclass(frozen=True, slots=True)
class TestResult:
    test_case: TestCase
    response: str | None
    passed: bool
    metrics: Metrics | None
    validation_details: dict[str, Any]
    execution_error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
