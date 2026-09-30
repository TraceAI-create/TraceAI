"""Custom exceptions for the TraceAI SDK."""


class TraceAIError(Exception):
    """Base exception for all TraceAI SDK errors."""
    pass


class TraceAIAPIError(TraceAIError):
    """Raised when an API request to the TraceAI backend fails."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TraceAIIntegrityError(TraceAIError):
    """Raised when the cryptographic audit chain verification fails."""
    pass
