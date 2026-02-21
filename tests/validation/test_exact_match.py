from promptum.validation import ExactMatch


def test_exact_match_case_sensitive(exact_match_validator: ExactMatch) -> None:
    passed, details = exact_match_validator.validate("Hello")
    assert passed is True
    assert details["expected"] == "Hello"
    assert details["actual"] == "Hello"


def test_exact_match_case_sensitive_fail(exact_match_validator: ExactMatch) -> None:
    passed, details = exact_match_validator.validate("hello")
    assert passed is False
    assert details["expected"] == "Hello"
    assert details["actual"] == "hello"


def test_exact_match_case_insensitive() -> None:
    validator = ExactMatch("Hello", case_sensitive=False)

    passed, _ = validator.validate("hello")
    assert passed is True

    passed, _ = validator.validate("HELLO")
    assert passed is True

    passed, _ = validator.validate("HeLLo")
    assert passed is True


def test_exact_match_describe_includes_validator_name_and_expected_value() -> None:
    validator = ExactMatch("test")
    description = validator.describe()
    assert "Exact match" in description
    assert "test" in description
