"""Interfaces and base classes for pricing engines."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from descriptors import NonNegativeFloat, BoundedFloat
from exceptions import NegativeValueError

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
    _maturity = NonNegativeFloat("_maturity")
    rate = NonNegativeFloat("rate")
    _volatility =  BoundedFloat("_volatility", min_value=0.0, max_value=5.0)
    dividend = NonNegativeFloat("dividend")

    @property
    def maturity(self) -> float:
        return self._maturity

    @maturity.setter
    def maturity(self, value: float) -> None:
        if value <= 0:
            raise NegativeValueError("maturity must be > 0")
        self._maturity = value

    @maturity.deleter
    def maturity(self) -> None:
        raise AttributeError("maturity cannot be deleted")

    @property
    def volatility(self) -> float:
        return self._volatility

    @volatility.setter
    def volatility(self, value: float) -> None:
        if value <= 0:
            raise NegativeValueError("volatility must be > 0")
        self._volatility = value

    @volatility.deleter
    def volatility(self) -> None:
        raise AttributeError("volatility cannot be deleted")

    def __init__(self, market: MarketData, spec: OptionSpecification, volatility: float) -> None:
        self.spot = market.spot
        self.rate = market.rate
        self.dividend = market.dividend
        self.strike = spec.strike
        self.maturity = spec.maturity
        self.volatility = volatility

    def __repr__(self) -> str:  
        return (
            f"{self.__class__.__name__}(spot={self.spot}, strike={self.strike}, maturity={self.maturity}, "
            f"rate={self.rate}, volatility={self.volatility})"
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

class _HasGreeks(Protocol):
    def greeks(self) -> dict[str, float]: ...
    
class GreeksMixin:
    @property
    def delta(self: _HasGreeks) -> float:
        return self.greeks().get("delta", 0.0)

    @property
    def gamma(self: _HasGreeks) -> float:
        return self.greeks().get("gamma", 0.0)

    @property
    def vega(self: _HasGreeks) -> float:
        return self.greeks().get("vega", 0.0)

    @property
    def theta(self: _HasGreeks) -> float:
        return self.greeks().get("theta", 0.0)

    @property
    def rho(self: _HasGreeks) -> float:
        return self.greeks().get("rho", 0.0)


@runtime_checkable
class PricingProtocol(Protocol):
    def price(self) -> PricingResult:
        ...

    def greeks(self) -> dict[str, float]:
        ...
