# promptum

<div align="center">

![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)
![Async](https://img.shields.io/badge/Async-First-green?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Benchmark LLMs Like a Pro.**

Stop writing boilerplate to test LLMs. Start getting results.

</div>

---

## What's This?

A dead-simple Python library for benchmarking LLM providers. Write tests once, run them across any model, get structured results.

```python
benchmark = Benchmark(provider=client, name="my_test")
benchmark.add_test(TestCase(
    name="basic_math",
    prompt="What is 2+2?",
    model="gpt-3.5-turbo",
    validator=Contains("4")
))
report = await benchmark.run_async()
```

That's it. No setup. No config files. Just results.

---

## Why You Need This

**Before promptum:**
```python
# Custom API client for each provider
openai_client = OpenAI(api_key=...)
anthropic_client = Anthropic(api_key=...)

# Manual validation logic
if "correct answer" not in response:
    failed_tests.append(...)

# Track metrics yourself
latency = end_time - start_time
tokens = response.usage.total_tokens

# Write your own retry logic
for attempt in range(max_retries):
    try:
        response = client.chat.completions.create(...)
        break
    except Exception:
        sleep(2 ** attempt)
```

**After promptum:**
```python
report = await benchmark.run_async()
summary = report.get_summary()  # Metrics captured automatically
```

---

## Quick Start

```bash
pip install promptum  # (or: uv pip install promptum)
export OPENROUTER_API_KEY="your-key"
```

```python
import asyncio
from promptum import Benchmark, TestCase, OpenRouterClient, Contains

async def main():
    async with OpenRouterClient(api_key="your-key") as client:
        benchmark = Benchmark(provider=client, name="quick_test")

        benchmark.add_test(TestCase(
            name="basic_math",
            prompt="What is 15 * 7? Reply with just the number.",
            model="openai/gpt-3.5-turbo",
            validator=Contains("105")
        ))

        report = await benchmark.run_async()
        summary = report.get_summary()

        print(f"✓ {summary.passed}/{summary.total} tests passed")
        print(f"⚡ {summary.avg_latency_ms:.0f}ms average")
        print(f"💰 ${summary.total_cost_usd:.6f} total cost")

asyncio.run(main())
```

Run it:
```bash
python your_script.py
```

---

## What You Get

- [x] **100+ Models via OpenRouter** - One client for OpenAI, Anthropic, Google, and more
- [x] **Smart Validation** - ExactMatch, Contains, Regex, JsonSchema, or write your own
- [x] **Automatic Retries** - Exponential/linear backoff with configurable attempts
- [x] **Metrics Tracking** - Latency, tokens, cost - automatically captured
- [x] **Async by Default** - Run 100 tests in parallel without breaking a sweat
- [x] **Type Safe** - Full type hints, catches errors before runtime
- [x] **Zero Config** - No YAML files, no setup scripts, just Python

---

## Real Example

Compare GPT-4 vs Claude on your tasks:

```python
import asyncio
from promptum import Benchmark, TestCase, Contains, Regex, OpenRouterClient

async def main():
    async with OpenRouterClient(api_key="your-key") as client:
        benchmark = Benchmark(provider=client, name="model_comparison")

        benchmark.add_tests([
            TestCase(
                name="json_output_gpt4",
                prompt='Output JSON: {"status": "ok"}',
                model="openai/gpt-4",
                validator=Regex(r'\{"status":\s*"ok"\}')
            ),
            TestCase(
                name="json_output_claude",
                prompt='Output JSON: {"status": "ok"}',
                model="anthropic/claude-3-5-sonnet",
                validator=Regex(r'\{"status":\s*"ok"\}')
            ),
            TestCase(
                name="creative_writing",
                prompt="Write a haiku about Python",
                model="openai/gpt-4",
                validator=Contains("Python", case_sensitive=False)
            ),
        ])

        report = await benchmark.run_async()

        # Side-by-side model comparison
        for model, model_report in report.group_by(lambda r: r.test_case.model).items():
            summary = model_report.get_summary()
            print(f"{model}: {summary.pass_rate:.0%} pass rate, {summary.avg_latency_ms:.0f}ms avg")

asyncio.run(main())
```

---

## Use Cases

**🔬 Model Evaluation** - Compare GPT-4, Claude, Gemini on your specific tasks
**🎯 Prompt Engineering** - Test 100 prompt variations, find what works
**⚡ Latency Testing** - Measure real-world response times across providers
**💰 Cost Analysis** - Track spending per model/task before production
**🔄 Regression Testing** - Ensure model updates don't break your prompts
**📊 A/B Testing** - Data-driven model selection for your product

---

## Requirements

- Python 3.13+
- An OpenRouter API key (or implement your own provider)

That's it. No Docker, no complex setup.

---

## Why Protocol-Based?

Most libraries force inheritance:
```python
class MyProvider(BaseProvider):  # Tightly coupled
    def generate(self): ...
```

We use protocols (structural typing):
```python
class MyProvider:  # No inheritance needed
    async def generate(self) -> tuple[str, Metrics]:
        # Your implementation
        return response, metrics

# It just works
benchmark = Benchmark(provider=MyProvider())
```

Cleaner. More flexible. More Pythonic.

---

## Contributing

Found a bug? Want a feature? PRs welcome!

```bash
# Development setup
git clone https://github.com/deyna256/promptum.git
cd promptum
just sync       # Install dependencies
just test       # Run tests

# Development commands
just lint       # Check code style
just format     # Format code
just typecheck  # Type checking
```

---

## License

MIT - do whatever you want with it.

---

<div align="center">

**[⭐ Star on GitHub](https://github.com/deyna256/promptum)** | **[🐛 Report Bug](https://github.com/deyna256/promptum/issues)** | **[💡 Request Feature](https://github.com/deyna256/promptum/issues)**

Made for developers who value their time.

</div>
