class ProviderError(Exception):
    """Base exception for all provider errors."""


class ProviderNotInitializedError(ProviderError):
    """Client not initialized (missing async context manager)."""

    def __init__(self) -> None:
        super().__init__("Client not initialized. Use async context manager.")


class ProviderResponseParseError(ProviderError):
    """Invalid API response structure."""

    def __init__(self, original_error: Exception) -> None:
        self.original_error = original_error
        super().__init__(f"Invalid API response structure: {original_error}")


class ProviderHTTPStatusError(ProviderError):
    """Non-retryable HTTP status error."""

    def __init__(self, status_code: int, response_body: str) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"HTTP error {status_code}: {response_body}")


class ProviderTransientError(ProviderError):
    """Transient error (timeout/network) after all retries exhausted."""

    def __init__(self, attempts: int, retry_delays: list[float]) -> None:
        self.attempts = attempts
        self.retry_delays = retry_delays
        super().__init__(f"Request failed after {attempts} attempts due to transient error")


class ProviderRetryExhaustedError(ProviderError):
    """Retryable HTTP status after all retries exhausted."""

    def __init__(
        self,
        attempts: int,
        last_status_code: int,
        last_response_body: str,
        retry_delays: list[float],
    ) -> None:
        self.attempts = attempts
        self.last_status_code = last_status_code
        self.last_response_body = last_response_body
        self.retry_delays = retry_delays
        super().__init__(
            f"Request failed after {attempts} attempts"
            f" (last status {last_status_code})"
        )
