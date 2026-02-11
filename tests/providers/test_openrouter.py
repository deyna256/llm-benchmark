import pytest

from promptum.providers.openrouter import OpenRouterClient


@pytest.mark.asyncio
async def test_generate_rejects_reserved_field_override():
    async with OpenRouterClient(api_key="test-key") as client:
        with pytest.raises(ValueError) as exc_info:
            await client.generate(
                prompt="hello",
                model="test-model",
                messages=[{"role": "user", "content": "injected"}],
            )

    assert "messages" in str(exc_info.value)
