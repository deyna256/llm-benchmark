from promptum.validation import Contains


def test_contains_case_sensitive(contains_validator: Contains) -> None:
    passed, details = contains_validator.validate("Hello world!")
    assert passed is True
    assert details["substring"] == "world"


def test_contains_case_sensitive_fail(contains_validator: Contains) -> None:
    passed, _ = contains_validator.validate("Hello World!")
    assert passed is False


def test_contains_case_insensitive() -> None:
    validator = Contains("world", case_sensitive=False)

    passed, _ = validator.validate("Hello WORLD!")
    assert passed is True

    passed, _ = validator.validate("Hello WoRLd!")
    assert passed is True


def test_contains_not_found() -> None:
    validator = Contains("test")
    passed, _ = validator.validate("This string has no match")
    assert passed is False


def test_contains_describe_includes_validator_name_and_substring() -> None:
    validator = Contains("example")
    description = validator.describe()
    assert "Contains" in description
    assert "example" in description
