from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from promptum.validation.protocol import Validator

from promptum.providers.retry import RetryConfig


@dataclass(frozen=True, slots=True)
class TestCase:
    name: str
    prompt: str
    model: str
    validator: "Validator"
    tags: Sequence[str] = ()
    system_prompt: str | None = None
    temperature: float = 1.0
    max_tokens: int | None = None
    retry_config: RetryConfig | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
