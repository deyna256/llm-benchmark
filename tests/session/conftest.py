from unittest.mock import AsyncMock, MagicMock

import pytest

from promptum.providers.metrics import Metrics
from promptum.session.case import Prompt


@pytest.fixture
def mock_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.generate.return_value = ("test response", Metrics(latency_ms=100.0))
    return provider


@pytest.fixture
def passing_validator() -> MagicMock:
    validator = MagicMock()
    validator.validate.return_value = (True, {"matched": True})
    validator.describe.return_value = "always passes"
    return validator


@pytest.fixture
def failing_validator() -> MagicMock:
    validator = MagicMock()
    validator.validate.return_value = (False, {"matched": False})
    validator.describe.return_value = "always fails"
    return validator


@pytest.fixture
def sample_prompt(passing_validator: MagicMock) -> Prompt:
    return Prompt(
        name="test-prompt",
        prompt="What is 2+2?",
        model="test-model",
        validator=passing_validator,
    )


@pytest.fixture
def failing_prompt(failing_validator: MagicMock) -> Prompt:
    return Prompt(
        name="failing-prompt",
        prompt="What is 2+2?",
        model="test-model",
        validator=failing_validator,
    )
