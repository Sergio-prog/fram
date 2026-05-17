class FramError(Exception):
    """Base error for user-facing processing failures."""


class UnsupportedFormat(FramError):
    """Raised when a file format is not supported by the requested operation."""


class InvalidOperation(FramError):
    """Raised when operation parameters are invalid for the target media."""


class ProcessingFailed(FramError):
    """Raised when an external processor or codec fails."""

