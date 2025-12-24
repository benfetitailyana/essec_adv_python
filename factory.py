"""Factory for option instances from config dictionaries."""
from __future__ import annotations

from interfaces import MarketData, OptionSpecification
from options import EquityJumpCall


class OptionFactory:
    registry = {"equity_jump_call": EquityJumpCall}

    @classmethod
    def create(cls, config: dict) -> EquityJumpCall:
        option_type = config.get("type", "equity_jump_call")
        klass = cls.registry[option_type]
        market = MarketData(spot=float(config["spot"]), rate=float(config["rate"]), dividend=float(config.get("dividend", 0.0)))
        spec = OptionSpecification(strike=float(config["strike"]), maturity=float(config["maturity"]))
        vol = float(config["volatility"])
        return klass(market=market, spec=spec, volatility=vol)

    @classmethod
    def atm_equity(cls, spot: float, maturity: float, rate: float, volatility: float) -> EquityJumpCall:
        config = {
            "type": "equity_jump_call",
            "spot": spot,
            "strike": spot,
            "maturity": maturity,
            "rate": rate,
            "volatility": volatility,
            "dividend": 0.0,
        }
        return cls.create(config)
