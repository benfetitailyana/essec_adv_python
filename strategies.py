"""Strategy registry for runtime pricing method selection."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict

from interfaces import BaseOption
from merton import JumpParameters, MertonJumpModel


@dataclass
class StrategyResult:
    price: float
    greeks: dict[str, float]


PricingStrategy = Callable[[BaseOption], StrategyResult]


class StrategyRegistry:
    _strategies: Dict[str, PricingStrategy] = {}
    _default_key = "black_scholes"

    jump_mc_settings = {
        "paths": 200,
        "intensity": 0.75,
        "mean_jump": -0.6,
        "jump_vol": 0.25,
    }

    @classmethod
    def register(cls, name: str, strategy: PricingStrategy) -> None:
        cls._strategies[name] = strategy

    @classmethod
    def get(cls, name: str) -> PricingStrategy:
        return cls._strategies[name]

    @classmethod
    def default_strategy(cls) -> PricingStrategy:
        return cls._strategies[cls._default_key]

    @classmethod
    def configure_jump_mc(
        cls,
        *,
        paths: int | None = None,
        intensity: float | None = None,
        mean_jump: float | None = None,
        jump_vol: float | None = None,
    ) -> None:
        if paths is not None:
            cls.jump_mc_settings["paths"] = paths
        if intensity is not None:
            cls.jump_mc_settings["intensity"] = intensity
        if mean_jump is not None:
            cls.jump_mc_settings["mean_jump"] = mean_jump
        if jump_vol is not None:
            cls.jump_mc_settings["jump_vol"] = jump_vol


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_strategy(option: BaseOption) -> StrategyResult:
    maturity = option.maturity
    vol = option.volatility
    strike = option.strike
    spot = option.spot
    rate = option.rate
    dividend = getattr(option, "dividend", 0.0)
    if maturity <= 0 or vol <= 0:
        payoff = max(spot - strike, 0.0)
        return StrategyResult(price=payoff, greeks={"delta": 1.0 if spot > strike else 0.0})
    d1 = (math.log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * maturity) / (vol * math.sqrt(maturity))
    d2 = d1 - vol * math.sqrt(maturity)
    nd1 = _normal_cdf(d1)
    nd2 = _normal_cdf(d2)
    discounted_strike = strike * math.exp(-rate * maturity)
    forward = spot * math.exp(-dividend * maturity)
    price = forward * nd1 - discounted_strike * nd2
    delta = math.exp(-dividend * maturity) * nd1
    gamma = math.exp(-dividend * maturity) * math.exp(-0.5 * d1 * d1) / (spot * vol * math.sqrt(2 * math.pi * maturity))
    vega = forward * math.sqrt(maturity) * math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
    theta = (
        -forward * math.exp(-0.5 * d1 * d1) * vol / (2 * math.sqrt(2 * math.pi * maturity))
        - rate * discounted_strike * nd2
        + dividend * forward * nd1
    )
    rho = maturity * discounted_strike * nd2
    return StrategyResult(price=price, greeks={"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho})


def jump_diffusion_mc_strategy(option: BaseOption) -> StrategyResult:
    jump_params = JumpParameters(intensity=0.75, mean_jump=-0.6, jump_vol=0.25)
    steps = max(10, int(option.maturity * 12))
    model = MertonJumpModel(
        spot=option.spot,
        rate=option.rate,
        volatility=option.volatility,
        jump_params=jump_params,
        maturity=option.maturity,
        steps=steps,
    )
    paths = 200 
    discounted_payoff = model.price_paths(paths=paths, strike=option.strike)
    return StrategyResult(price=discounted_payoff, greeks={"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

def cox_ross_rubinstein(option: BaseOption) -> StrategyResult:
    # for the quant team
    return StrategyResult(price=0.0, greeks={"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

def jarrow_rudd_model(option: BaseOption) -> StrategyResult:
    # for the quant team
    return StrategyResult(price=0.0, greeks={"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

def stand_trinomial_tree(option: BaseOption) -> StrategyResult:
    # for the quant team
    return StrategyResult(price=0.0, greeks={"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

def adaptative_trinomial_tree(option: BaseOption) -> StrategyResult:
    # for the quant team
    return StrategyResult(price=0.0, greeks={"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

StrategyRegistry.register("black_scholes", black_scholes_strategy)
StrategyRegistry.register("jump_mc", jump_diffusion_mc_strategy)
StrategyRegistry.register("cox ross Rubinstein", cox_ross_rubinstein)
StrategyRegistry.register("jarrow Rudd", jarrow_rudd_model)
StrategyRegistry.register("trinomial tree", stand_trinomial_tree)
StrategyRegistry.register("adaptative trinomial tree", adaptative_trinomial_tree)