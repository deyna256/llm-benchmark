# Session & Testing

Documentation for the `promptum.session` package.

```python
from promptum import Session, Prompt, Report, Summary, TestResult
```

---

## Session

Orchestrates test runs against an LLM provider.

```python
class Session:
    def __init__(
        self,
        provider: LLMProvider,
        name: str = "benchmark",
        max_concurrent: int = 5,
        progress_callback: Callable[[int, int, TestResult], None] | None = None,
    ): ...
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | `LLMProvider` | *required* | LLM provider instance |
| `name` | `str` | `"benchmark"` | Session name |
| `max_concurrent` | `int` | `5` | Max parallel requests |
| `progress_callback` | `Callable[[int, int, TestResult], None] \| None` | `None` | Called after each test with `(completed, total, result)` |

### Methods

**`add_test(test_case: Prompt) -> None`**

Add a single test case.

**`add_tests(test_cases: Sequence[Prompt]) -> None`**

Add multiple test cases at once.

**`async run() -> Report`**

Execute all added tests concurrently and return a `Report`. Returns an empty report if no tests were added.

---

## Prompt

Test case definition. Frozen dataclass.

```python
@dataclass(frozen=True, slots=True)
class Prompt:
    name: str
    prompt: str
    model: str
    validator: Validator
    tags: Sequence[str] = ()
    system_prompt: str | None = None
    temperature: float = 1.0
    max_tokens: int | None = None
    retry_config: RetryConfig | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *required* | Test case identifier |
| `prompt` | `str` | *required* | User prompt to send |
| `model` | `str` | *required* | Model identifier (e.g. `"openai/gpt-4"`) |
| `validator` | `Validator` | *required* | Validates the response |
| `tags` | `Sequence[str]` | `()` | Tags for filtering/grouping |
| `system_prompt` | `str \| None` | `None` | Optional system prompt |
| `temperature` | `float` | `1.0` | Sampling temperature |
| `max_tokens` | `int \| None` | `None` | Max tokens in response |
| `retry_config` | `RetryConfig \| None` | `None` | Per-test retry config (overrides provider default) |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

---

## Report

Results container with filtering and grouping. Frozen dataclass.

```python
@dataclass(frozen=True, slots=True)
class Report:
    results: Sequence[TestResult]
```

### Methods

**`get_summary() -> Summary`**

Compute aggregated metrics across all results.

**`filter(model: str | None = None, tags: Sequence[str] | None = None, passed: bool | None = None) -> Report`**

Return a new `Report` with results matching the given criteria. All parameters are optional and combined with AND logic.

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str \| None` | Filter by model name |
| `tags` | `Sequence[str] \| None` | Filter by any matching tag |
| `passed` | `bool \| None` | Filter by pass/fail status |

**`group_by(key: Callable[[TestResult], str]) -> dict[str, Report]`**

Group results into separate reports by a key function.

```python
# Group by model
for model, model_report in report.group_by(lambda r: r.test_case.model).items():
    summary = model_report.get_summary()
    print(f"{model}: {summary.pass_rate:.0%} pass rate, {summary.avg_latency_ms:.0f}ms avg")
```

---

## Summary

Aggregated metrics. Frozen dataclass. Returned by `Report.get_summary()`.

```python
@dataclass(frozen=True, slots=True)
class Summary:
    total: int
    passed: int
    failed: int
    pass_rate: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    total_cost_usd: float
    total_tokens: int
    execution_errors: int
    validation_failures: int
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total number of tests |
| `passed` | `int` | Tests that passed validation |
| `failed` | `int` | `execution_errors + validation_failures` |
| `pass_rate` | `float` | `passed / total` (0 if no tests) |
| `avg_latency_ms` | `float` | Average response latency |
| `min_latency_ms` | `float` | Minimum response latency |
| `max_latency_ms` | `float` | Maximum response latency |
| `total_cost_usd` | `float` | Total cost across all tests |
| `total_tokens` | `int` | Total tokens consumed |
| `execution_errors` | `int` | Tests that failed with provider/network errors |
| `validation_failures` | `int` | Tests that got a response but failed validation |

---

## TestResult

Single test outcome. Frozen dataclass.

```python
@dataclass(frozen=True, slots=True)
class TestResult:
    test_case: Prompt
    response: str | None
    passed: bool
    metrics: Metrics | None
    validation_details: dict[str, Any]
    execution_error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
```

| Field | Type | Description |
|-------|------|-------------|
| `test_case` | `Prompt` | The original test case |
| `response` | `str \| None` | LLM response text (`None` on error) |
| `passed` | `bool` | Whether validation passed |
| `metrics` | `Metrics \| None` | Provider metrics (`None` on error) |
| `validation_details` | `dict[str, Any]` | Validator-specific details |
| `execution_error` | `str \| None` | Error message if execution failed |
| `timestamp` | `datetime` | UTC timestamp of execution |

---

## Example: Model Comparison

```python
import asyncio
from promptum import Session, Prompt, Contains, Regex, OpenRouterClient

async def main():
    async with OpenRouterClient(api_key="your-key") as client:
        session = Session(provider=client, name="model_comparison")

        session.add_tests([
            Prompt(
                name="json_output_gpt4",
                prompt='Output JSON: {"status": "ok"}',
                model="openai/gpt-4",
                validator=Regex(r'\{"status":\s*"ok"\}'),
            ),
            Prompt(
                name="json_output_claude",
                prompt='Output JSON: {"status": "ok"}',
                model="anthropic/claude-3-5-sonnet",
                validator=Regex(r'\{"status":\s*"ok"\}'),
            ),
            Prompt(
                name="creative_writing",
                prompt="Write a haiku about Python",
                model="openai/gpt-4",
                validator=Contains("Python", case_sensitive=False),
            ),
        ])

        report = await session.run()

        # Side-by-side model comparison
        for model, model_report in report.group_by(lambda r: r.test_case.model).items():
            summary = model_report.get_summary()
            print(f"{model}: {summary.pass_rate:.0%} pass rate, {summary.avg_latency_ms:.0f}ms avg")

asyncio.run(main())
```
