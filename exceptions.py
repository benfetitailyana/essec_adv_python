"""Domain-specific exceptions for the option pricing mini-project."""

class NegativeValueError(ValueError):
    """Raised when a parameter expected to be non-negative is negative."""


class InvalidTypeError(TypeError):
    """Raised when a parameter has an unexpected type."""


class PricingError(RuntimeError):
    """Raised when pricing fails due to invalid configuration or runtime issues."""
