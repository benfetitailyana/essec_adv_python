"""
Unit tests for Option Pricing Platform.

Tests cover:
- Parameter validation (descriptors/properties)
- Pricing behavior
- Generator exhaustion
- Logging side effects
- Container utilities
- Factory methods (@classmethod/@staticmethod)
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Import modules to test
from utils import (
    PositiveFloat,
    NonNegativeFloat,
    NegativeValueException,
    InvalidTypeException,
    InvalidRangeException,
)
from models import MarketData, OptionParameters, JumpDiffusionParams, TraderInfo
from interfaces import OptionType, AssetClass
from factory import OptionFactory, TraderFactory
from options import EquityJumpCallOption
from jump_diffusion import JumpProcess, MertonJumpModel
from trade_blotter import TradeBlotter, Trade
from models import OrderInfo


# ==============================================================================
# Tests for Descriptors and Validation
# ==============================================================================


class TestDescriptors:
    """Test descriptor validation."""

    def test_positive_float_accepts_positive(self):
        """Test PositiveFloat accepts positive values."""

        class TestClass:
            value = PositiveFloat(default=1.0)

        obj = TestClass()
        obj.value = 10.5
        assert obj.value == 10.5

    def test_positive_float_rejects_negative(self):
        """Test PositiveFloat rejects negative values."""

        class TestClass:
            value = PositiveFloat(default=1.0)

        obj = TestClass()
        with pytest.raises(InvalidRangeException):
            obj.value = -5.0

    def test_positive_float_rejects_zero(self):
        """Test PositiveFloat rejects zero."""

        class TestClass:
            value = PositiveFloat(default=1.0)

        obj = TestClass()
        with pytest.raises(InvalidRangeException):
            obj.value = 0.0

    def test_non_negative_float_accepts_zero(self):
        """Test NonNegativeFloat accepts zero."""

        class TestClass:
            value = NonNegativeFloat(default=0.0)

        obj = TestClass()
        obj.value = 0.0
        assert obj.value == 0.0

    def test_non_negative_float_rejects_negative(self):
        """Test NonNegativeFloat rejects negative."""

        class TestClass:
            value = NonNegativeFloat(default=0.0)

        obj = TestClass()
        with pytest.raises(NegativeValueException):
            obj.value = -1.0


# ==============================================================================
# Tests for Models
# ==============================================================================


class TestModels:
    """Test dataclass models."""

    def test_market_data_creation(self):
        """Test MarketData creation and validation."""
        market = MarketData(spot=100.0, risk_free_rate=0.05, dividend_yield=0.02)
        assert market.spot == 100.0
        assert market.risk_free_rate == 0.05

    def test_market_data_rejects_negative_spot(self):
        """Test MarketData rejects negative spot."""
        with pytest.raises(ValueError):
            MarketData(spot=-100.0, risk_free_rate=0.05)

    def test_option_parameters_creation(self):
        """Test OptionParameters creation."""
        params = OptionParameters(
            strike=100.0, maturity=1.0, option_type=OptionType.CALL, volatility=0.2
        )
        assert params.strike == 100.0
        assert params.option_type == OptionType.CALL

    def test_jump_params_drift_correction(self):
        """Test JumpDiffusionParams drift correction calculation."""
        jump_params = JumpDiffusionParams(
            jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2
        )

        drift = jump_params.drift_correction
        assert isinstance(drift, float)
        assert drift < 0  # Should be negative with negative jump mean


# ==============================================================================
# Tests for Factory Pattern
# ==============================================================================


class TestFactory:
    """Test factory methods."""

    def test_option_factory_create_equity_jump_call(self):
        """Test OptionFactory.create_equity_jump_call (staticmethod)."""
        option = OptionFactory.create_equity_jump_call(
            spot=100.0, strike=100.0, maturity=1.0, risk_free_rate=0.05, volatility=0.2
        )

        assert isinstance(option, EquityJumpCallOption)
        assert option.spot == 100.0
        assert option.strike == 100.0

    def test_option_factory_from_dict(self):
        """Test OptionFactory.from_dict (classmethod)."""
        config = {"spot": 100.0, "strike": 100.0, "maturity": 1.0, "volatility": 0.2}

        option = OptionFactory.from_dict(config)

        assert isinstance(option, EquityJumpCallOption)
        assert option.spot == 100.0

    def test_option_factory_default_nikkei(self):
        """Test OptionFactory.create_default_nikkei_call (staticmethod)."""
        option = OptionFactory.create_default_nikkei_call()

        assert option.underlying_ticker == "NIKKEI225"
        assert option.spot == 28000.0

    def test_trader_factory_create_adam_jones(self):
        """Test TraderFactory.create_adam_jones (classmethod)."""
        trader = TraderFactory.create_adam_jones()

        assert trader.name == "Adam Jones"
        assert trader.desk == "JapanEQExotics"
        assert trader.trader_id == "AJ001"


# ==============================================================================
# Tests for Jump Diffusion
# ==============================================================================


class TestJumpDiffusion:
    """Test jump diffusion model."""

    def test_jump_process_creation(self):
        """Test JumpProcess initialization."""
        jump = JumpProcess(intensity=0.75, mean=-0.6, std=0.2)

        assert jump.intensity == 0.75
        assert jump.mean == -0.6

    def test_merton_model_creation(self):
        """Test MertonJumpModel initialization."""
        jump_params = JumpDiffusionParams(
            jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2
        )

        model = MertonJumpModel(
            initial_price=100.0,
            risk_free_rate=0.05,
            volatility=0.2,
            jump_params=jump_params,
            time_horizon=1.0,
            dt=0.01,
        )

        assert model.initial_price == 100.0
        assert len(model) == 100  # __len__ test

    def test_merton_model_simulate_path(self):
        """Test path simulation."""
        jump_params = JumpDiffusionParams(
            jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2
        )

        model = MertonJumpModel(
            initial_price=100.0,
            risk_free_rate=0.05,
            volatility=0.2,
            jump_params=jump_params,
            time_horizon=1.0,
            dt=0.1,
            seed=42,
        )

        path = model.simulate_path()

        assert len(path) == 11  # 10 steps + initial
        assert path[0] == 100.0  # Initial price
        assert path[-1] > 0  # Terminal price is positive

    def test_generator_exhaustion(self):
        """Test generator produces correct number of values."""
        jump_params = JumpDiffusionParams(
            jump_intensity=0.5, jump_mean=-0.5, jump_std=0.1
        )

        model = MertonJumpModel(
            initial_price=100.0,
            risk_free_rate=0.05,
            volatility=0.2,
            jump_params=jump_params,
            time_horizon=0.5,
            dt=0.1,
            seed=42,
        )

        # Generate terminal prices using generator
        num_sims = 10
        generator = model.simulate_terminal_prices(num_sims)

        prices = list(generator)

        assert len(prices) == num_sims
        assert all(p > 0 for p in prices)


# ==============================================================================
# Tests for Options
# ==============================================================================


class TestOptions:
    """Test option classes."""

    def test_option_creation(self):
        """Test EquityJumpCallOption creation."""
        market_data = MarketData(spot=100.0, risk_free_rate=0.05)

        option_params = OptionParameters(
            strike=100.0, maturity=1.0, option_type=OptionType.CALL, volatility=0.2
        )

        option = EquityJumpCallOption(
            market_data=market_data, option_params=option_params
        )

        assert option.spot == 100.0
        assert option.is_call
        assert not option.is_put

    def test_option_callable(self):
        """Test option __call__ method."""
        option = OptionFactory.create_default_nikkei_call()

        # Should be callable
        price = option()

        assert isinstance(price, float)
        assert price > 0

    def test_option_property_setters(self):
        """Test option property setters with validation."""
        option = OptionFactory.create_default_nikkei_call()

        # Valid setter
        option.spot = 29000.0
        assert option.spot == 29000.0

        # Invalid setter should raise
        with pytest.raises((InvalidRangeException, NegativeValueException, ValueError)):
            option.spot = -100.0


# ==============================================================================
# Tests for Trade Blotter
# ==============================================================================


class TestTradeBlotter:
    """Test TradeBlotter container."""

    def test_blotter_creation(self):
        """Test TradeBlotter initialization."""
        blotter = TradeBlotter(name="Test Blotter")

        assert len(blotter) == 0
        assert blotter.name == "Test Blotter"

    def test_blotter_append(self):
        """Test appending trades to blotter."""
        blotter = TradeBlotter()

        trader = TraderInfo(trader_id="T001", name="Test Trader", desk="TestDesk")

        order = OrderInfo(
            order_id="O001",
            trader_info=trader,
            quantity=100,
            underlying="TEST",
            strike=100.0,
            maturity=1.0,
            option_type=OptionType.CALL,
        )

        trade = Trade(order=order, fill_price=10.0)
        blotter.append(trade)

        assert len(blotter) == 1
        assert blotter[0] == trade

    def test_blotter_sum_notional(self):
        """Test notional calculation."""
        blotter = TradeBlotter()

        trader = TraderInfo(trader_id="T001", name="Test Trader", desk="TestDesk")

        # Add two trades
        for i in range(2):
            order = OrderInfo(
                order_id=f"O{i:03d}",
                trader_info=trader,
                quantity=100,
                underlying="TEST",
                strike=100.0,
                maturity=1.0,
                option_type=OptionType.CALL,
            )
            trade = Trade(order=order, fill_price=10.0)
            blotter.append(trade)

        # Each trade: 100 * 10.0 = 1000.0
        # Total: 2000.0
        assert blotter.sum_notional() == 2000.0

    def test_blotter_filter_by_underlying(self):
        """Test filtering by underlying."""
        blotter = TradeBlotter()

        trader = TraderInfo(trader_id="T001", name="Test Trader", desk="TestDesk")

        # Add trades with different underlyings
        for underlying in ["NIKKEI", "TOPIX", "NIKKEI"]:
            order = OrderInfo(
                order_id=f"O_{underlying}",
                trader_info=trader,
                quantity=100,
                underlying=underlying,
                strike=100.0,
                maturity=1.0,
                option_type=OptionType.CALL,
            )
            trade = Trade(order=order, fill_price=10.0)
            blotter.append(trade)

        nikkei_trades = blotter.filter_by_underlying("NIKKEI")
        assert len(nikkei_trades) == 2


# ==============================================================================
# Tests for Logging
# ==============================================================================


class TestLogging:
    """Test logging functionality."""

    def test_pricing_generates_log(self):
        """Test that pricing operations generate log entries."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            # Create option and price it (should log)
            option = OptionFactory.create_default_nikkei_call()
            price = option.price("black_scholes")

            # Check that option_pricing.log was created
            log_path = Path("option_pricing.log")
            assert log_path.exists()

            # Check log contains some content
            log_content = log_path.read_text()
            assert len(log_content) > 0

        finally:
            # Cleanup
            if os.path.exists(log_file):
                os.unlink(log_file)


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
