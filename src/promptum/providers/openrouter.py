import asyncio
import time
from typing import Any

import httpx

from promptum.providers.metrics import Metrics
from promptum.providers.retry import RetryConfig, RetryStrategy


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        default_retry_config: RetryConfig | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.default_retry_config = default_retry_config or RetryConfig()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "OpenRouterClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.default_retry_config.timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Any,
    ) -> tuple[str, Metrics]:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        config = retry_config or self.default_retry_config
        retry_delays: list[float] = []

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)

        for attempt in range(config.max_attempts):
            start_time = time.perf_counter()
            try:
                response = await self._client.post(
                    "/chat/completions",
                    json=payload,
                    timeout=config.timeout,
                )

                if response.status_code == 200:
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    try:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                    except (KeyError, IndexError, TypeError) as e:
                        raise RuntimeError(f"Invalid API response structure: {e}") from e

                    usage = data.get("usage", {})
                    metrics = Metrics(
                        latency_ms=latency_ms,
                        prompt_tokens=usage.get("prompt_tokens"),
                        completion_tokens=usage.get("completion_tokens"),
                        total_tokens=usage.get("total_tokens"),
                        cost_usd=usage.get("cost") or usage.get("total_cost"),
                        retry_delays=tuple(retry_delays),
                    )

                    return content, metrics

                if response.status_code not in config.retryable_status_codes:
                    response.raise_for_status()

                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    retry_delays.append(delay)
                    await asyncio.sleep(delay)

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    retry_delays.append(delay)
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(
                        f"Request failed after {config.max_attempts} attempts: {e}"
                    ) from e
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"HTTP error {e.response.status_code}: {e.response.text}") from e

        raise RuntimeError(f"Request failed after {config.max_attempts} attempts")

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.initial_delay * (config.exponential_base**attempt)
            return min(delay, config.max_delay)
        return config.initial_delay
