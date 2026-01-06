"""Simple descriptors enforcing positive numeric constraints."""
from __future__ import annotations

from typing import Any

from exceptions import InvalidTypeError, NegativeValueError


class NonNegativeFloat:
    """Descriptor ensuring stored value is a float >= 0."""

    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> float:
        if instance is None:
            return self  # type: ignore[return-value]
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise InvalidTypeError(f"{self.name} must be numeric")
        if value < 0:
            raise NegativeValueError(f"{self.name} must be non-negative")
        instance.__dict__[self.name] = float(value)

    def __delete__(self, instance: Any) -> None:
        raise AttributeError(f"Cannot delete attribute {self.name}")


class PositiveInt:
    """Descriptor ensuring stored value is an int > 0."""

    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> int:
        if instance is None:
            return self  # type: ignore[return-value]
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, int):
            raise InvalidTypeError(f"{self.name} must be an int")
        if value <= 0:
            raise NegativeValueError(f"{self.name} must be positive")
        instance.__dict__[self.name] = value

    def __delete__(self, instance: Any) -> None:
        raise AttributeError(f"Cannot delete attribute {self.name}")


class BoundedFloat:
    """
    Descriptor enforcing a numeric value within optional bounds.
    Uses obj.__dict__ to avoid recursion.
    """

    def __init__(self, name: str, *, min_value: float | None = None, max_value: float | None = None) -> None:
        self.name = name
        self.min_value = min_value
        self.max_value = max_value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # type: ignore[return-value]
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, (int, float)):
            raise InvalidTypeError(f"{self.name} must be a number (int or float)")

        value = float(value)

        if self.min_value is not None and value < self.min_value:
            raise NegativeValueError(f"{self.name} must be >= {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise NegativeValueError(f"{self.name} must be <= {self.max_value}")

        obj.__dict__[self.name] = value

    def __delete__(self, obj) -> None:
        raise AttributeError(f"{self.name} cannot be deleted")