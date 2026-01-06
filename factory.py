"""Factory for option instances from config dictionaries."""
from __future__ import annotations

from interfaces import BaseOption, MarketData, OptionSpecification
from options import EquityJumpCall
from exceptions import PricingError


class OptionFactory:
    registry = {"equity_jump_call": EquityJumpCall,
                # "fx_vanilla_call": FXVanillaCall,   # stub / future extension
                # "rate_caplet": RateCaplet,          # stub / future extension
        }

    @classmethod
    def create(cls, config: dict) -> BaseOption:
        option_type = config.get("type", "equity_jump_call")
        if option_type not in cls.registry:
            raise PricingError(
                f"Unknown option type '{option_type}'. Allowed types: {sorted(cls.registry.keys())}")
        klass = cls.registry[option_type]

        market = MarketData(spot=float(config["spot"]), rate=float(config["rate"]), dividend=float(config.get("dividend", 0.0)))
        spec = OptionSpecification(strike=float(config["strike"]), maturity=float(config["maturity"]))
        vol = float(config["volatility"])
        return klass(market=market, spec=spec, volatility=vol)

    @classmethod
    def atm_equity(cls, spot: float, maturity: float, rate: float, volatility: float) -> BaseOption:
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
