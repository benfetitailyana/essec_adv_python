import logging

import pytest

from descriptors import NonNegativeFloat
from exceptions import NegativeValueError
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
