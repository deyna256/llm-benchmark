# Validation

Documentation for the `promptum.validation` package.

```python
from promptum import Validator, ExactMatch, Contains, Regex, JsonSchema
```

---

## Validator Protocol

Any class with matching `validate` and `describe` methods satisfies this protocol — no inheritance required.

```python
class Validator(Protocol):
    def validate(self, response: str) -> tuple[bool, dict[str, Any]]: ...
    def describe(self) -> str: ...
```

**`validate(response: str) -> tuple[bool, dict[str, Any]]`**

Returns `(passed, details)` where `details` contains validator-specific diagnostic information.

**`describe() -> str`**

Returns a human-readable description of validation criteria.

---

## ExactMatch

Checks if the response exactly equals the expected string.

```python
@dataclass(frozen=True, slots=True)
class ExactMatch:
    expected: str
    case_sensitive: bool = True
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `expected` | `str` | *required* | Expected response text |
| `case_sensitive` | `bool` | `True` | Case-sensitive comparison |

**Validation details:**

| Key | Type | Description |
|-----|------|-------------|
| `expected` | `str` | Expected value |
| `actual` | `str` | Actual response |
| `case_sensitive` | `bool` | Whether comparison was case-sensitive |

```python
validator = ExactMatch("42")
passed, details = validator.validate("42")    # True
passed, details = validator.validate("42!")   # False

validator = ExactMatch("hello", case_sensitive=False)
passed, details = validator.validate("HELLO")  # True
```

---

## Contains

Checks if the response contains a substring.

```python
@dataclass(frozen=True, slots=True)
class Contains:
    substring: str
    case_sensitive: bool = True
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `substring` | `str` | *required* | Substring to search for |
| `case_sensitive` | `bool` | `True` | Case-sensitive search |

**Validation details:**

| Key | Type | Description |
|-----|------|-------------|
| `substring` | `str` | Searched substring |
| `case_sensitive` | `bool` | Whether search was case-sensitive |

```python
validator = Contains("Python")
passed, details = validator.validate("I love Python!")  # True

validator = Contains("python", case_sensitive=False)
passed, details = validator.validate("PYTHON rocks")    # True
```

---

## Regex

Checks if the response matches a regular expression (using `re.search`).

```python
@dataclass(frozen=True, slots=True)
class Regex:
    pattern: str
    flags: int = 0
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pattern` | `str` | *required* | Regular expression pattern |
| `flags` | `int` | `0` | `re` module flags (e.g. `re.IGNORECASE`) |

**Validation details:**

| Key | Type | Description |
|-----|------|-------------|
| `pattern` | `str` | The regex pattern |
| `matched` | `str \| None` | Matched text, or `None` if no match |

```python
import re

validator = Regex(r"\d{3}-\d{4}")
passed, details = validator.validate("Call 555-1234")  # True

validator = Regex(r"hello", flags=re.IGNORECASE)
passed, details = validator.validate("HELLO world")    # True
```

---

## JsonSchema

Checks if the response is valid JSON with required keys.

```python
@dataclass(frozen=True, slots=True)
class JsonSchema:
    required_keys: tuple[str, ...] = ()
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `required_keys` | `tuple[str, ...]` | `()` | Keys that must be present in the JSON object |

**Validation details (on success):**

| Key | Type | Description |
|-----|------|-------------|
| `parsed` | `dict` | Parsed JSON data |
| `missing_keys` | `list[str]` | Keys that were missing |

**Validation details (on failure):**

| Key | Type | Description |
|-----|------|-------------|
| `error` | `str` | Error description |

```python
validator = JsonSchema()
passed, details = validator.validate('{"any": "json"}')  # True

validator = JsonSchema(required_keys=("status", "data"))
passed, details = validator.validate('{"status": "ok", "data": []}')  # True
passed, details = validator.validate('{"status": "ok"}')              # False, missing "data"
```

---

## Example: Custom Validator

```python
from typing import Any

class LengthValidator:
    """No inheritance needed — just match the protocol signature."""

    def __init__(self, min_length: int = 0, max_length: int = 1000):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        length = len(response)
        passed = self.min_length <= length <= self.max_length
        return passed, {
            "length": length,
            "min_length": self.min_length,
            "max_length": self.max_length,
        }

    def describe(self) -> str:
        return f"Length between {self.min_length} and {self.max_length}"


# Use it directly
session.add_test(Prompt(
    name="length_check",
    prompt="Write a short poem",
    model="openai/gpt-4",
    validator=LengthValidator(min_length=10, max_length=500),
))
```
