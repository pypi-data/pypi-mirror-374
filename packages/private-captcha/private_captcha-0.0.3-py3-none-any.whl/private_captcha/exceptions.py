"""Exception classes for Private Captcha client errors."""


class PrivateCaptchaError(Exception):
    """Base exception for the Private Captcha client."""


class APIKeyError(PrivateCaptchaError):
    """Raised when the API key is invalid or empty."""


class SolutionError(PrivateCaptchaError):
    """Raised for issues with the captcha solution."""


class RetriableError(PrivateCaptchaError):
    """Marker for errors that can be retried."""


class HTTPError(PrivateCaptchaError):
    """An HTTP error."""

    def __init__(self, status_code: int):
        super().__init__(f"API returned HTTP status {status_code}")
        self.status_code = status_code


class RetriableHTTPError(RetriableError):
    """An HTTP error that can be retried."""

    def __init__(self, status_code: int, retry_after: int = 0):
        super().__init__(f"API returned HTTP status {status_code}")
        self.status_code = status_code
        self.retry_after = retry_after


class VerificationFailedError(PrivateCaptchaError):
    """Raised when verification fails after all retry attempts."""

    def __init__(self, message: str, attempts: int):
        super().__init__(message)
        self.attempts = attempts
