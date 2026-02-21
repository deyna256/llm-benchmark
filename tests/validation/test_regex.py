from promptum.validation import Regex


def test_regex_match(regex_validator: Regex) -> None:
    passed, details = regex_validator.validate("Call me at 555-1234")
    assert passed is True
    assert details["matched"] == "555-1234"


def test_regex_no_match(regex_validator: Regex) -> None:
    passed, details = regex_validator.validate("No phone here")
    assert passed is False
    assert details["matched"] is None


def test_regex_email() -> None:
    validator = Regex(r"[\w\.-]+@[\w\.-]+\.\w+")

    passed, details = validator.validate("Contact: john@example.com")
    assert passed is True
    assert details["matched"] == "john@example.com"

    passed, _ = validator.validate("No email here")
    assert passed is False


def test_regex_describe_includes_validator_name_and_pattern() -> None:
    validator = Regex(r"\d+")
    description = validator.describe()
    assert "Regex" in description
    assert r"\d+" in description
