from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from promptum.providers.metrics import Metrics
from promptum.session.case import Prompt


@dataclass(frozen=True, slots=True)
class TestResult:
    test_case: Prompt
    response: str | None
    passed: bool
    metrics: Metrics | None
    validation_details: dict[str, Any]
    execution_error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
