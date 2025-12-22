"""
Factory pattern for creating option instances from configuration.

Demonstrates:
- Factory Pattern (GoF) for object creation
- Creation from dictionaries, JSON, and dataclasses
- Centralized object creation logic
- @classmethod and @staticmethod usage
"""

from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from interfaces import OptionType, AssetClass
from models import (
    MarketData,
    OptionParameters,
    JumpDiffusionParams,
    TraderInfo,
    OrderInfo,
)
from options import EquityJumpCallOption
from utils import logger, OptionPricingException


class OptionFactory:
    """
    Factory for creating option instances.

    Demonstrates Factory Pattern (GoF):
    - Encapsulates object creation logic
    - Provides multiple creation methods
    - Centralizes validation and defaults

    SOLID Principles:
    - Single Responsibility: Only handles option creation
    - Open/Closed: Easy to extend with new option types
    - Dependency Inversion: Returns interface type (could return any PricingInterface)
    """

    @staticmethod
    def create_equity_jump_call(
        spot: float,
        strike: float,
        maturity: float,
        risk_free_rate: float,
        volatility: float,
        jump_intensity: float = 0.75,
        jump_mean: float = -0.6,
        jump_std: float = 0.2,
        underlying_ticker: str = "UNKNOWN",
        dividend_yield: float = 0.0,
    ) -> EquityJumpCallOption:
        """
        Create equity jump call option from parameters.

        Static method that doesn't need class instance.

        Args:
            spot: Spot price
            strike: Strike price
            maturity: Time to maturity
            risk_free_rate: Risk-free rate
            volatility: Volatility
            jump_intensity: Jump intensity (λ)
            jump_mean: Jump mean (μ_j)
            jump_std: Jump std (δ)
            underlying_ticker: Ticker symbol
            dividend_yield: Dividend yield

        Returns:
            EquityJumpCallOption instance
        """
        logger.info(f"Creating equity jump call via factory: {underlying_ticker}")

        market_data = MarketData(
            spot=spot, risk_free_rate=risk_free_rate, dividend_yield=dividend_yield
        )

        option_params = OptionParameters(
            strike=strike,
            maturity=maturity,
            option_type=OptionType.CALL,
            volatility=volatility,
            asset_class=AssetClass.EQUITY,
            underlying_ticker=underlying_ticker,
        )

        jump_params = JumpDiffusionParams(
            jump_intensity=jump_intensity, jump_mean=jump_mean, jump_std=jump_std
        )

        return EquityJumpCallOption(
            market_data=market_data,
            option_params=option_params,
            jump_params=jump_params,
        )

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> EquityJumpCallOption:
        """
        Create option from configuration dictionary.

        Class method that provides alternative constructor.

        Args:
            config: Configuration dictionary

        Returns:
            EquityJumpCallOption instance

        Example:
            config = {
                "spot": 100.0,
                "strike": 100.0,
                "maturity": 1.0,
                ...
            }
            option = OptionFactory.from_dict(config)
        """
        logger.info("Creating option from dictionary config")

        try:
            return cls.create_equity_jump_call(
                spot=config["spot"],
                strike=config["strike"],
                maturity=config["maturity"],
                risk_free_rate=config.get("risk_free_rate", 0.05),
                volatility=config["volatility"],
                jump_intensity=config.get("jump_intensity", 0.75),
                jump_mean=config.get("jump_mean", -0.6),
                jump_std=config.get("jump_std", 0.2),
                underlying_ticker=config.get("underlying", "UNKNOWN"),
                dividend_yield=config.get("dividend_yield", 0.0),
            )
        except KeyError as e:
            raise OptionPricingException(f"Missing required configuration key: {e}")
        except Exception as e:
            raise OptionPricingException(f"Failed to create option from config: {e}")

    @classmethod
    def from_json_file(cls, file_path: str) -> EquityJumpCallOption:
        """
        Create option from JSON configuration file.

        Args:
            file_path: Path to JSON file

        Returns:
            EquityJumpCallOption instance
        """
        logger.info(f"Creating option from JSON file: {file_path}")

        try:
            with open(file_path, "r") as f:
                config = json.load(f)

            return cls.from_dict(config)

        except Exception as e:
            raise OptionPricingException(f"Failed to load option from JSON: {e}")

    @classmethod
    def from_json_string(cls, json_str: str) -> EquityJumpCallOption:
        """
        Create option from JSON string.

        Args:
            json_str: JSON string

        Returns:
            EquityJumpCallOption instance
        """
        logger.info("Creating option from JSON string")

        try:
            config = json.loads(json_str)
            return cls.from_dict(config)
        except Exception as e:
            raise OptionPricingException(f"Failed to parse JSON: {e}")

    @classmethod
    def batch_create_from_configs(
        cls, configs: List[Dict[str, Any]]
    ) -> List[EquityJumpCallOption]:
        """
        Create multiple options from list of configurations.

        Args:
            configs: List of configuration dictionaries

        Returns:
            List of EquityJumpCallOption instances
        """
        logger.info(f"Batch creating {len(configs)} options")

        options = []
        for i, config in enumerate(configs):
            try:
                option = cls.from_dict(config)
                options.append(option)
            except Exception as e:
                logger.error(f"Failed to create option {i}: {e}")
                # Continue with next option

        logger.info(f"Successfully created {len(options)} options")
        return options

    @staticmethod
    def create_default_nikkei_call() -> EquityJumpCallOption:
        """
        Create a default NIKKEI 225 call option.

        Convenience method for testing.

        Returns:
            EquityJumpCallOption with default parameters
        """
        logger.info("Creating default NIKKEI 225 call option")

        return OptionFactory.create_equity_jump_call(
            spot=28000.0,
            strike=28000.0,
            maturity=0.25,  # 3 months
            risk_free_rate=0.05,
            volatility=0.20,
            jump_intensity=0.75,
            jump_mean=-0.6,
            jump_std=0.2,
            underlying_ticker="NIKKEI225",
            dividend_yield=0.02,
        )


class TraderFactory:
    """
    Factory for creating trader and order instances.

    Demonstrates factory pattern for domain objects.
    """

    @staticmethod
    def create_trader(
        trader_id: str, name: str, desk: str, email: Optional[str] = None
    ) -> TraderInfo:
        """
        Create trader info.

        Args:
            trader_id: Unique trader ID
            name: Trader name
            desk: Trading desk
            email: Email (optional)

        Returns:
            TraderInfo instance
        """
        logger.info(f"Creating trader: {name} ({trader_id})")

        return TraderInfo(trader_id=trader_id, name=name, desk=desk, email=email)

    @classmethod
    def create_adam_jones(cls) -> TraderInfo:
        """
        Create the Adam Jones trader from instructions.

        Convenience method for the specific trader mentioned in requirements.

        Returns:
            TraderInfo for Adam Jones
        """
        logger.info("Creating Adam Jones trader")

        return cls.create_trader(
            trader_id="AJ001",
            name="Adam Jones",
            desk="JapanEQExotics",
            email="adam.jones@bankxyz.com",
        )

    @staticmethod
    def create_order(
        order_id: str,
        trader: TraderInfo,
        quantity: int,
        underlying: str,
        strike: float,
        maturity: float,
        option_type: OptionType,
    ) -> OrderInfo:
        """
        Create order info.

        Args:
            order_id: Unique order ID
            trader: Trader placing the order
            quantity: Number of contracts
            underlying: Underlying ticker
            strike: Strike price
            maturity: Time to maturity
            option_type: Call or Put

        Returns:
            OrderInfo instance
        """
        logger.info(f"Creating order: {order_id} for {trader.name}")

        return OrderInfo(
            order_id=order_id,
            trader_info=trader,
            quantity=quantity,
            underlying=underlying,
            strike=strike,
            maturity=maturity,
            option_type=option_type,
        )

    @classmethod
    def create_adam_jones_nikkei_order(cls, quantity: int = 100) -> OrderInfo:
        """
        Create Adam Jones's NIKKEI 225 ATM call order from instructions.

        Args:
            quantity: Number of contracts (default 100)

        Returns:
            OrderInfo instance
        """
        logger.info("Creating Adam Jones NIKKEI 225 order")

        trader = cls.create_adam_jones()

        return cls.create_order(
            order_id=f"ORD_AJ_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            trader=trader,
            quantity=quantity,
            underlying="NIKKEI225",
            strike=28000.0,  # ATM
            maturity=0.25,  # 3 months
            option_type=OptionType.CALL,
        )


if __name__ == "__main__":
    from datetime import datetime

    print("=" * 70)
    print("Factory Pattern Module")
    print("=" * 70)

    # Test option factory
    print("\n1. Creating option via factory (direct parameters):")
    option = OptionFactory.create_equity_jump_call(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        underlying_ticker="TEST",
    )
    print(f"   Created: {option}")

    # Test from dictionary
    print("\n2. Creating option from dictionary:")
    config = {
        "spot": 28000.0,
        "strike": 28000.0,
        "maturity": 0.25,
        "volatility": 0.20,
        "underlying": "NIKKEI225",
    }
    option2 = OptionFactory.from_dict(config)
    print(f"   Created: {option2}")

    # Test default option
    print("\n3. Creating default NIKKEI option:")
    option3 = OptionFactory.create_default_nikkei_call()
    print(f"   Created: {option3}")

    # Test trader factory
    print("\n4. Creating Adam Jones trader:")
    trader = TraderFactory.create_adam_jones()
    print(f"   Created: {trader}")

    # Test order creation
    print("\n5. Creating Adam Jones order:")
    order = TraderFactory.create_adam_jones_nikkei_order(quantity=100)
    print(f"   Created: {order}")

    # Test batch creation
    print("\n6. Batch creating options:")
    configs = [
        {"spot": 100, "strike": 95, "maturity": 0.5, "volatility": 0.2},
        {"spot": 100, "strike": 100, "maturity": 0.5, "volatility": 0.2},
        {"spot": 100, "strike": 105, "maturity": 0.5, "volatility": 0.2},
    ]
    options = OptionFactory.batch_create_from_configs(configs)
    print(f"   Created {len(options)} options")

    print("\n" + "=" * 70)
