from typing import Any, Protocol

from promptum.providers.metrics import Metrics


class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> tuple[str, Metrics]:
        """
        Generates a response from the LLM.

        Returns:
            (response_text, metrics)
        """
        ...
