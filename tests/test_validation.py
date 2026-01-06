import logging

import pytest

from descriptors import NonNegativeFloat
from exceptions import NegativeValueError, PricingError
from factory import OptionFactory
from interfaces import MarketData, OptionSpecification
from options import EquityJumpCall


class Dummy:
    value = NonNegativeFloat("value")

    def __init__(self, value: float):
        self.value = value


def test_descriptor_rejects_negative() -> None:
    with pytest.raises(NegativeValueError):
        Dummy(-1)


def test_pricing_call_behavior() -> None:
    option = OptionFactory.atm_equity(spot=100, maturity=1, rate=0.05, volatility=0.2)
    result = option()
    assert result.price > 0


def test_logging_side_effect(tmp_path) -> None:
    log_path = tmp_path / "log.txt"
    logging.basicConfig(filename=log_path, level=logging.INFO, force=True)
    logging.info("hello")
    assert "hello" in log_path.read_text()

def test_property_validation_strict_positive_and_deleter() -> None:
    option = OptionFactory.atm_equity(spot=100, maturity=1.0, rate=0.05, volatility=0.2)

    # strict > 0
    with pytest.raises(NegativeValueError):
        option.maturity = 0.0

    with pytest.raises(NegativeValueError):
        option.volatility = 0.0

    # deleter interdit
    with pytest.raises(AttributeError):
        del option.maturity

    with pytest.raises(AttributeError):
        del option.volatility

def test_factory_unknown_type_raises_pricing_error() -> None:
    bad_config = {
        "type": "i_do_not_exist",
        "spot": 100,
        "rate": 0.05,
        "dividend": 0.0,
        "volatility": 0.2,
        "strike": 100,
        "maturity": 0.25,
    }
    with pytest.raises(PricingError):
        OptionFactory.create(bad_config)

def test_atm_equity_sets_strike_equal_spot() -> None:
    option = OptionFactory.atm_equity(spot=123.0, maturity=0.25, rate=0.05, volatility=0.2)
    assert option.strike == option.spot