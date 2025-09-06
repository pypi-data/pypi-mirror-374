"""Enhanced error handling utilities and custom exceptions."""

from typing import Any


class AIMCPError(Exception):
    """Base exception for all AIMCP errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ResourceURIError(AIMCPError):
    """Raised when resource URI is invalid or malformed."""
