from promptum.validation import JsonSchema


def test_json_schema_valid(json_schema_validator: JsonSchema) -> None:
    passed, details = json_schema_validator.validate('{"name": "Alice", "age": 30}')
    assert passed is True
    assert details["parsed"]["name"] == "Alice"
    assert details["parsed"]["age"] == 30
    assert details["missing_keys"] == []


def test_json_schema_missing_key(json_schema_validator: JsonSchema) -> None:
    passed, details = json_schema_validator.validate('{"name": "Bob"}')
    assert passed is False
    assert "age" in details["missing_keys"]


def test_json_schema_all_missing(json_schema_validator: JsonSchema) -> None:
    passed, details = json_schema_validator.validate('{"other": "value"}')
    assert passed is False
    assert "name" in details["missing_keys"]
    assert "age" in details["missing_keys"]


def test_json_schema_invalid_json(json_schema_validator: JsonSchema) -> None:
    passed, details = json_schema_validator.validate("not json")
    assert passed is False
    assert "error" in details


def test_json_schema_extra_keys() -> None:
    validator = JsonSchema(required_keys=("id",))
    passed, details = validator.validate('{"id": 1, "name": "Test", "extra": true}')
    assert passed is True
    assert details["parsed"]["id"] == 1


def test_json_schema_describe_includes_validator_info_and_required_keys() -> None:
    validator = JsonSchema(required_keys=("a", "b"))
    description = validator.describe()
    assert "Valid JSON" in description
    assert "a" in description
    assert "b" in description
