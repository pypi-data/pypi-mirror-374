from __future__ import annotations

from typing import Optional


class ThreeXPayError(Exception):
    """Base exception for 3X PAY SDK."""


class APIError(ThreeXPayError):
    """Raised when the API returns a non-successful HTTP status code."""

    def __init__(self, status_code: int, message: Optional[str] = None, response_text: str = ""):
        self.status_code = status_code
        self.message = message or f"HTTP {status_code}"
        self.response_text = response_text
        super().__init__(f"{self.message}: {self.response_text}")


class APIResponseError(ThreeXPayError):
    """Raised when API returns success=false in a 200 OK JSON body."""

    def __init__(
        self,
        *,
        code: Optional[str] = None,
        detail: Optional[str] = None,
        traceback_id: Optional[str] = None,
        status_code: int = 200,
        response_text: str = "",
    ) -> None:
        self.code = code
        self.detail = detail
        self.traceback_id = traceback_id
        self.status_code = status_code
        self.response_text = response_text
        message_prefix = code or "API_ERROR"
        message_detail = detail or ""
        suffix = f" (traceback={traceback_id})" if traceback_id else ""
        super().__init__(f"{message_prefix}: {message_detail}{suffix}")


