class TraceAIError(Exception):
    """Base exception for TraceAI SDK errors."""
    pass


class TraceAIAPIError(TraceAIError):
    """Raised when an API request to TraceAI backend fails."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TraceAIIntegrityError(TraceAIError):
    """Raised when client-side and server-side cryptographic audit chains do not match."""
    pass
