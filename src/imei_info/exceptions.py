from typing import Optional

class ImeiError(Exception):
    """Base exception for all IMEI.info SDK errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ImeiNetworkError(ImeiError):
    """Exception thrown when a network error or timeout occurs."""
    def __init__(self, message: str, original_exception: Exception):
        super().__init__(f"Network error occurred: {message}")
        self.original_exception = original_exception


class ImeiApiError(ImeiError):
    """Exception thrown when the IMEI.info API returns a non-200 status code."""
    def __init__(self, message: str, status_code: int, code: str, error_type: str, raw_response: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code                # e.g., "insufficient_credits", "invalid_luhn_checksum"
        self.error_type = error_type    # e.g., "Payment Required", "Unprocessable Entity"
        self.raw_response = raw_response

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.error_type} ({self.code}): {self.message}"


class ImeiAuthenticationError(ImeiApiError):
    """Exception for HTTP 401 Unauthorized (missing or invalid API key)."""
    pass


class ImeiInsufficientCreditsError(ImeiApiError):
    """Exception for HTTP 402 Payment Required (out of API lookup credits)."""
    pass


class ImeiValidationError(ImeiApiError):
    """Exception for HTTP 422 Unprocessable Entity (e.g., invalid Luhn checksum)."""
    pass


class ImeiRateLimitError(ImeiApiError):
    """Exception for HTTP 429 Too Many Requests (rate limit exceeded)."""
    pass


class ImeiServerError(ImeiError):
    """Exception for HTTP 500+ Internal Server Errors."""
    def __init__(self, message: str, status_code: int, raw_response: str):
        super().__init__(f"Server error ({status_code}): {message}")
        self.status_code = status_code
        self.raw_response = raw_response


def raise_for_status_code(status_code: int, text: str) -> None:
    """
    Parses the HTTP status code and response body, raising the corresponding exception.
    """
    if status_code < 400:
        return

    # Try parsing structured error response from JSON
    error_msg = text
    code = "unknown_error"
    error_type = "Error"
    
    try:
        import json
        data = json.loads(text)
        if isinstance(data, dict):
            error_msg = data.get("message", error_msg)
            code = data.get("code", code)
            error_type = data.get("error", error_type)
    except Exception:
        # Response is not valid JSON
        pass

    if status_code == 401:
        raise ImeiAuthenticationError(error_msg, status_code, code, error_type, text)
    elif status_code == 402:
        raise ImeiInsufficientCreditsError(error_msg, status_code, code, error_type, text)
    elif status_code == 422:
        raise ImeiValidationError(error_msg, status_code, code, error_type, text)
    elif status_code == 429:
        raise ImeiRateLimitError(error_msg, status_code, code, error_type, text)
    elif status_code >= 500:
        raise ImeiServerError(error_msg, status_code, text)
    else:
        raise ImeiApiError(error_msg, status_code, code, error_type, text)
