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
