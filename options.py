"""Concrete option classes and simple pricing helpers."""
from __future__ import annotations

import math

from interfaces import BaseOption, GreeksMixin, MarketData, OptionSpecification, PricingResult
from strategies import StrategyRegistry, StrategyResult


class EquityJumpCall(BaseOption, GreeksMixin):
    """Equity call option using jump diffusion-friendly plumbing."""

    def price(self) -> PricingResult:
        strategy = StrategyRegistry.default_strategy()
        outcome = strategy(self)
        return PricingResult(price=outcome.price, greeks=outcome.greeks)

    def greeks(self) -> dict[str, float]:
        return StrategyRegistry.default_strategy()(self).greeks


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(spot: float, strike: float, maturity: float, rate: float, vol: float, dividend: float = 0.0) -> StrategyResult:
    if maturity <= 0 or vol <= 0:
        payoff = max(spot - strike, 0.0)
        return StrategyResult(price=payoff, greeks={"delta": 1.0 if spot > strike else 0.0})
    d1 = (math.log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * maturity) / (vol * math.sqrt(maturity))
    d2 = d1 - vol * math.sqrt(maturity)
    nd1 = normal_cdf(d1)
    nd2 = normal_cdf(d2)
    discounted_strike = strike * math.exp(-rate * maturity)
    forward = spot * math.exp(-dividend * maturity)
    price = forward * nd1 - discounted_strike * nd2
    delta = math.exp(-dividend * maturity) * nd1
    gamma = math.exp(-dividend * maturity) * math.exp(-0.5 * d1 * d1) / (spot * vol * math.sqrt(2 * math.pi * maturity))
    vega = forward * math.sqrt(maturity) * math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
    theta = -forward * math.exp(-0.5 * d1 * d1) * vol / (2 * math.sqrt(2 * math.pi * maturity)) - rate * discounted_strike * nd2 + dividend * forward * nd1
    rho = maturity * discounted_strike * nd2
    return StrategyResult(price=price, greeks={"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho})
