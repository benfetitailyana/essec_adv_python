"""Interfaces and base classes for pricing engines."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from descriptors import NonNegativeFloat


@dataclass
class MarketData:
    spot: float
    rate: float
    dividend: float = 0.0


@dataclass
class OptionSpecification:
    strike: float
    maturity: float


@dataclass
class PricingResult:
    price: float
    greeks: dict[str, float]


class BaseOption(abc.ABC):
    """Abstract base class for options with validation and dunder helpers."""

    spot = NonNegativeFloat("spot")
    strike = NonNegativeFloat("strike")
    maturity = NonNegativeFloat("maturity")
    rate = NonNegativeFloat("rate")
    volatility = NonNegativeFloat("volatility")

    def __init__(self, market: MarketData, spec: OptionSpecification, volatility: float) -> None:
        self.spot = market.spot
        self.rate = market.rate
        self.dividend = market.dividend
        self.strike = spec.strike
        self.maturity = spec.maturity
        self.volatility = volatility

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return (
            f"{self.__class__.__name__}(spot={self.spot}, strike={self.strike}, maturity={self.maturity}, "
            f"rate={self.rate}, vol={self.volatility})"
        )

    def __len__(self) -> int:
        return max(1, int(self.maturity * 12))

    def __call__(self) -> PricingResult:
        return self.price()

    @abc.abstractmethod
    def price(self) -> PricingResult:
        """Return pricing result including greeks."""

    @abc.abstractmethod
    def greeks(self) -> dict[str, float]:
        """Return greeks for the option."""


class GreeksMixin:
    """Mixin to expose greeks as properties."""

    @property
    def delta(self) -> float:
        return self.greeks().get("delta", 0.0)

    @property
    def gamma(self) -> float:
        return self.greeks().get("gamma", 0.0)

    @property
    def vega(self) -> float:
        return self.greeks().get("vega", 0.0)

    @property
    def theta(self) -> float:
        return self.greeks().get("theta", 0.0)

    @property
    def rho(self) -> float:
        return self.greeks().get("rho", 0.0)


@runtime_checkable
class PricingProtocol(Protocol):
    def price(self) -> PricingResult:
        ...

    def greeks(self) -> dict[str, float]:
        ...
