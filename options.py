"""Concrete option classes and simple pricing helpers."""
from __future__ import annotations

import math

from interfaces import BaseOption, GreeksMixin, PricingResult
from strategies import StrategyRegistry


class EquityJumpCall(BaseOption, GreeksMixin):
    """Equity call option using jump diffusion-friendly plumbing."""

    def price(self) -> PricingResult:
        strategy = StrategyRegistry.default_strategy()
        outcome = strategy(self)
        return PricingResult(price=outcome.price, greeks=outcome.greeks)

    def greeks(self) -> dict[str, float]:
        return self.price().greeks

