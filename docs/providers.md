# Providers

Documentation for the `promptum.providers` package.

```python
from promptum import LLMProvider, OpenRouterClient, Metrics, RetryConfig, RetryStrategy
```

---

## LLMProvider Protocol

Any class with a matching `generate` method satisfies this protocol — no inheritance required.

```python
class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> tuple[str, Metrics]: ...
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | *required* | User prompt |
| `model` | `str` | *required* | Model identifier |
| `system_prompt` | `str \| None` | `None` | System prompt |
| `temperature` | `float` | `1.0` | Sampling temperature |
| `max_tokens` | `int \| None` | `None` | Max tokens in response |
| `**kwargs` | `Any` | — | Additional provider-specific parameters |

**Returns:** `tuple[str, Metrics]` — response text and metrics.

---

## OpenRouterClient

Built-in provider implementation using the [OpenRouter](https://openrouter.ai/) API. Async context manager.

```python
class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        default_retry_config: RetryConfig | None = None,
    ): ...
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | *required* | OpenRouter API key |
| `base_url` | `str` | `"https://openrouter.ai/api/v1"` | API base URL |
| `default_retry_config` | `RetryConfig \| None` | `None` | Default retry config (uses `RetryConfig()` defaults if `None`) |

### Usage

```python
async with OpenRouterClient(api_key="your-key") as client:
    response, metrics = await client.generate(
        prompt="Hello!",
        model="openai/gpt-4",
    )
```

The client must be used as an async context manager (`async with`). Calling `generate()` without entering the context raises `ProviderNotInitializedError`.

### generate()

```python
async def generate(
    self,
    prompt: str,
    model: str,
    system_prompt: str | None = None,
    temperature: float = 1.0,
    max_tokens: int | None = None,
    retry_config: RetryConfig | None = None,
    **kwargs: Any,
) -> tuple[str, Metrics]: ...
```

The `retry_config` parameter overrides the client's `default_retry_config` for this call. Additional `**kwargs` are merged into the API payload (cannot override `model`, `messages`, `temperature`, `max_tokens`).

---

## Metrics

Response metrics. Frozen dataclass.

```python
@dataclass(frozen=True, slots=True)
class Metrics:
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    retry_delays: Sequence[float] = ()
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `latency_ms` | `float` | *required* | Response latency in milliseconds |
| `prompt_tokens` | `int \| None` | `None` | Input tokens consumed |
| `completion_tokens` | `int \| None` | `None` | Output tokens generated |
| `total_tokens` | `int \| None` | `None` | Total tokens |
| `cost_usd` | `float \| None` | `None` | Cost in USD |
| `retry_delays` | `Sequence[float]` | `()` | Delay (seconds) before each retry |

### Properties

**`total_attempts -> int`** — total number of attempts (`len(retry_delays) + 1`).

---

## RetryConfig

Retry behavior configuration. Frozen dataclass.

```python
@dataclass(frozen=True, slots=True)
class RetryConfig:
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retryable_status_codes: Sequence[int] = (429, 500, 502, 503, 504)
    timeout: float = 60.0
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_attempts` | `int` | `3` | Maximum number of attempts |
| `strategy` | `RetryStrategy` | `EXPONENTIAL_BACKOFF` | Retry strategy |
| `initial_delay` | `float` | `1.0` | Initial delay in seconds |
| `max_delay` | `float` | `60.0` | Maximum delay in seconds (exponential only) |
| `exponential_base` | `float` | `2.0` | Base for exponential backoff |
| `retryable_status_codes` | `Sequence[int]` | `(429, 500, 502, 503, 504)` | HTTP status codes that trigger retries |
| `timeout` | `float` | `60.0` | Request timeout in seconds |

---

## RetryStrategy

```python
class RetryStrategy(Enum):
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
```

- **`EXPONENTIAL_BACKOFF`** — delay = `initial_delay * exponential_base ^ attempt`, capped at `max_delay`
- **`FIXED_DELAY`** — delay = `initial_delay` for every retry

---

## Exceptions

All provider exceptions inherit from `ProviderError`.

```
ProviderError
├── ProviderNotInitializedError
├── ProviderResponseParseError
├── ProviderHTTPStatusError
├── ProviderTransientError
└── ProviderRetryExhaustedError
```

### ProviderError

Base exception for all provider errors.

### ProviderNotInitializedError

Raised when `generate()` is called without entering the async context manager.

### ProviderResponseParseError

Raised when the API response has an unexpected structure.

| Attribute | Type | Description |
|-----------|------|-------------|
| `original_error` | `Exception` | The underlying parse error |

### ProviderHTTPStatusError

Raised for non-retryable HTTP errors.

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP status code |
| `response_body` | `str` | Response body |

### ProviderTransientError

Raised when all retries are exhausted due to transient errors (timeout/network).

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `int` | Total attempts made |
| `retry_delays` | `list[float]` | Delay before each retry |

### ProviderRetryExhaustedError

Raised when all retries are exhausted due to retryable HTTP status codes.

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `int` | Total attempts made |
| `last_status_code` | `int` | Last HTTP status code |
| `last_response_body` | `str` | Last response body |
| `retry_delays` | `list[float]` | Delay before each retry |

---

## Example: Custom Provider

```python
from promptum import LLMProvider, Metrics, Session, Prompt, Contains

class MyProvider:
    """No inheritance needed — just match the protocol signature."""

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs,
    ) -> tuple[str, Metrics]:
        # Your implementation here
        response = "42"
        metrics = Metrics(latency_ms=100.0)
        return response, metrics


# It just works
session = Session(provider=MyProvider())
session.add_test(Prompt(
    name="test",
    prompt="What is the answer?",
    model="my-model",
    validator=Contains("42"),
))
report = await session.run()
```
