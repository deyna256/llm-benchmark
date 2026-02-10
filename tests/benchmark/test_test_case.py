from promptum.session import Prompt
from promptum.validation import Contains


def test_test_case_creation() -> None:
    test_case = Prompt(
        name="test1",
        prompt="What is 2+2?",
        model="gpt-3.5-turbo",
        validator=Contains("4"),
        tags=("math",),
    )
    assert test_case.name == "test1"
    assert test_case.prompt == "What is 2+2?"
    assert test_case.model == "gpt-3.5-turbo"
    assert test_case.temperature == 1.0
    assert len(test_case.tags) == 1
    assert test_case.system_prompt is None


def test_test_case_with_system_prompt() -> None:
    test_case = Prompt(
        name="test2",
        prompt="Answer briefly",
        model="gpt-4",
        validator=Contains("yes"),
        system_prompt="You are a helpful assistant",
    )
    assert test_case.system_prompt == "You are a helpful assistant"


def test_test_case_with_custom_temperature() -> None:
    test_case = Prompt(
        name="test3",
        prompt="Be creative",
        model="gpt-4",
        validator=Contains("story"),
        temperature=1.5,
    )
    assert test_case.temperature == 1.5
