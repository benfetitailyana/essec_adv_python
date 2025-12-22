"""
Option classes - base and concrete implementations.

Demonstrates:
- Abstract base class with concrete implementations
- Inheritance hierarchy (BaseOption -> EquityJumpCallOption)
- Properties for controlled access
- Dunder methods for rich behavior
- Integration with pricing strategies and Greeks mixin
"""

from typing import Optional, Dict, List
import math
from abc import abstractmethod

from interfaces import PricingInterface, OptionType, AssetClass
from models import MarketData, OptionParameters, JumpDiffusionParams, PricingResult
from greeks_mixin import GreeksMixin
from pricing_strategies import get_strategy
from jump_diffusion import MertonJumpModel, calculate_call_payoff
from utils import (
    logger,
    time_it,
    log_call,
    PositiveFloat,
    NonNegativeFloat,
    validate_positive,
    PricingCalculationException,
)


class BaseOption(PricingInterface):
    """
    Abstract base class for all options.

    Implements common functionality while leaving pricing specifics
    to concrete subclasses.

    Demonstrates:
    - Inheritance: Common option behavior in base class
    - SOLID: Single Responsibility, Open/Closed principles
    - Properties: Controlled access with validation
    - Dunder methods: Rich behavior

    Attributes controlled by properties:
        spot: Current underlying price
        strike: Strike price
        time_to_maturity: Time to maturity in years
        risk_free_rate: Risk-free rate
        volatility: Volatility
        option_type: Call or Put
    """

    # Descriptors for validation
    _spot = PositiveFloat(default=100.0)
    _strike = PositiveFloat(default=100.0)
    _time_to_maturity = PositiveFloat(default=1.0)
    _risk_free_rate = NonNegativeFloat(default=0.0)
    _volatility = NonNegativeFloat(default=0.0)

    def __init__(
        self,
        market_data: MarketData,
        option_params: OptionParameters,
        default_pricing_method: str = "black_scholes",
    ):
        """
        Initialize base option.

        Args:
            market_data: Current market data
            option_params: Option parameters
            default_pricing_method: Default pricing method to use
        """
        # Using properties to ensure validation
        self.spot = market_data.spot
        self.risk_free_rate = market_data.risk_free_rate
        self.dividend_yield = market_data.dividend_yield

        self.strike = option_params.strike
        self.time_to_maturity = option_params.maturity
        self.volatility = option_params.volatility
        self.option_type = option_params.option_type
        self.asset_class = option_params.asset_class
        self.underlying_ticker = option_params.underlying_ticker

        self.default_pricing_method = default_pricing_method

        # Cache for pricing results
        self._price_cache: Optional[float] = None
        self._last_pricing_method: Optional[str] = None

        logger.debug(f"BaseOption initialized: {self}")

    # Properties with getters, setters, and validation

    @property
    def spot(self) -> float:
        """Current spot price of underlying."""
        return self._spot

    @spot.setter
    def spot(self, value: float) -> None:
        """Set spot price with validation."""
        validate_positive(value, "spot")
        self._spot = value
        self._invalidate_cache()

    @spot.deleter
    def spot(self) -> None:
        """Delete spot price (reset to default)."""
        self._spot = 100.0
        self._invalidate_cache()

    @property
    def strike(self) -> float:
        """Strike price."""
        return self._strike

    @strike.setter
    def strike(self, value: float) -> None:
        """Set strike with validation."""
        validate_positive(value, "strike")
        self._strike = value
        self._invalidate_cache()

    @property
    def time_to_maturity(self) -> float:
        """Time to maturity in years."""
        return self._time_to_maturity

    @time_to_maturity.setter
    def time_to_maturity(self, value: float) -> None:
        """Set time to maturity with validation."""
        validate_positive(value, "time_to_maturity")
        self._time_to_maturity = value
        self._invalidate_cache()

    @property
    def risk_free_rate(self) -> float:
        """Risk-free interest rate."""
        return self._risk_free_rate

    @risk_free_rate.setter
    def risk_free_rate(self, value: float) -> None:
        """Set risk-free rate with validation."""
        self._risk_free_rate = value
        self._invalidate_cache()

    @property
    def volatility(self) -> float:
        """Volatility."""
        return self._volatility

    @volatility.setter
    def volatility(self, value: float) -> None:
        """Set volatility with validation."""
        self._volatility = value
        self._invalidate_cache()

    @property
    def moneyness(self) -> float:
        """
        Calculate moneyness: S/K.

        > 1: In the money (for calls)
        = 1: At the money
        < 1: Out of the money (for calls)
        """
        return self.spot / self.strike

    @property
    def is_call(self) -> bool:
        """True if this is a call option."""
        return self.option_type == OptionType.CALL

    @property
    def is_put(self) -> bool:
        """True if this is a put option."""
        return self.option_type == OptionType.PUT

    def _invalidate_cache(self) -> None:
        """Invalidate cached price when parameters change."""
        self._price_cache = None

    @abstractmethod
    def price(self, method: Optional[str] = None) -> float:
        """
        Calculate option price.

        Must be implemented by subclasses.
        """
        pass

    def validate_parameters(self) -> bool:
        """
        Validate all option parameters.

        Returns:
            True if all parameters are valid

        Raises:
            ValueError: If any parameter is invalid
        """
        validate_positive(self.spot, "spot")
        validate_positive(self.strike, "strike")
        validate_positive(self.time_to_maturity, "time_to_maturity")
        return True

    def get_option_info(self) -> Dict[str, any]:
        """Get option information as dictionary."""
        return {
            "type": self.option_type.value,
            "asset_class": self.asset_class.value,
            "underlying": self.underlying_ticker,
            "spot": self.spot,
            "strike": self.strike,
            "maturity": self.time_to_maturity,
            "volatility": self.volatility,
            "risk_free_rate": self.risk_free_rate,
            "moneyness": self.moneyness,
        }

    def __call__(self, method: Optional[str] = None) -> float:
        """
        Make option callable to get price.

        Dunder method: __call__
        Allows: price = option()
        """
        return self.price(method)

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"underlying={self.underlying_ticker}, "
            f"type={self.option_type.value}, "
            f"S={self.spot:.2f}, K={self.strike:.2f}, "
            f"T={self.time_to_maturity:.2f}y, "
            f"σ={self.volatility:.2%}, r={self.risk_free_rate:.2%})"
        )

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"{self.option_type.value.upper()} option on {self.underlying_ticker} "
            f"@ {self.strike:.2f} ({self.time_to_maturity:.2f}y)"
        )


class EquityJumpCallOption(BaseOption, GreeksMixin):
    """
    Concrete implementation: Equity call option with jump diffusion.

    This is the main implementation requested in the instructions:
    - Inherits from BaseOption (inheritance)
    - Uses GreeksMixin (composition via mixin)
    - Implements jump-diffusion pricing using MertonJumpModel (composition)

    Demonstrates:
    - Inheritance: Gets base functionality from BaseOption
    - Composition: Uses JumpProcess inside MertonJumpModel
    - Mixin: Gets Greeks functionality from GreeksMixin
    - Multiple pricing methods via Strategy pattern
    """

    def __init__(
        self,
        market_data: MarketData,
        option_params: OptionParameters,
        jump_params: Optional[JumpDiffusionParams] = None,
        default_pricing_method: str = "jump_diffusion_mc",
    ):
        """
        Initialize equity jump call option.

        Args:
            market_data: Current market data
            option_params: Option contract parameters
            jump_params: Jump diffusion parameters (optional)
            default_pricing_method: Default pricing method
        """
        # Initialize both base class and mixin
        super().__init__(market_data, option_params, default_pricing_method)

        # Jump parameters (use defaults if not provided)
        if jump_params is None:
            jump_params = JumpDiffusionParams(
                jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2
            )

        self.jump_params = jump_params

        # Merton model for jump-diffusion simulations (composition)
        self._merton_model: Optional[MertonJumpModel] = None

        logger.info(f"EquityJumpCallOption created: {self}")

    @property
    def merton_model(self) -> MertonJumpModel:
        """
        Lazy initialization of Merton model.

        Creates model on first access to avoid unnecessary initialization.
        """
        if self._merton_model is None:
            self._merton_model = MertonJumpModel(
                initial_price=self.spot,
                risk_free_rate=self.risk_free_rate,
                volatility=self.volatility,
                jump_params=self.jump_params,
                time_horizon=self.time_to_maturity,
                dt=0.01,  # Daily steps
            )
        return self._merton_model

    @time_it
    @log_call
    def price(self, method: Optional[str] = None) -> float:
        """
        Calculate option price using specified method.

        Decorated with @time_it and @log_call for observability.

        Args:
            method: Pricing method name (None uses default)

        Returns:
            Option price
        """
        if method is None:
            method = self.default_pricing_method

        # Check cache
        if method == self._last_pricing_method and self._price_cache is not None:
            logger.debug(f"Using cached price: {self._price_cache}")
            return self._price_cache

        # Get strategy and calculate price
        try:
            strategy = get_strategy(method)

            # Special handling for jump diffusion MC
            if method == "jump_diffusion_mc":
                price = self._price_with_jump_diffusion()
            else:
                # Use strategy for other methods
                price = strategy.calculate_price(
                    spot=self.spot,
                    strike=self.strike,
                    time_to_maturity=self.time_to_maturity,
                    risk_free_rate=self.risk_free_rate,
                    volatility=self.volatility,
                    option_type=self.option_type,
                    jump_intensity=self.jump_params.jump_intensity,
                    jump_mean=self.jump_params.jump_mean,
                    jump_std=self.jump_params.jump_std,
                )

            # Cache the result
            self._price_cache = price
            self._last_pricing_method = method

            logger.info(f"Option priced at {price:.4f} using {strategy.name()}")

            return price

        except Exception as e:
            logger.error(f"Pricing failed with method '{method}': {str(e)}")
            raise PricingCalculationException(
                f"Failed to price option with method '{method}': {str(e)}"
            )

    def _price_with_jump_diffusion(self, num_simulations: int = 10000) -> float:
        """
        Price using Merton jump diffusion Monte Carlo.

        Uses generator for memory efficiency.

        Args:
            num_simulations: Number of Monte Carlo simulations

        Returns:
            Discounted expected payoff
        """
        logger.info(f"Pricing with jump diffusion MC: {num_simulations} simulations")

        # Generate terminal prices using generator (lazy evaluation)
        terminal_prices = self.merton_model.simulate_terminal_prices(num_simulations)

        # Calculate payoffs
        total_payoff = sum(
            calculate_call_payoff(S_T, self.strike) for S_T in terminal_prices
        )

        average_payoff = total_payoff / num_simulations

        # Discount to present value
        discount_factor = math.exp(-self.risk_free_rate * self.time_to_maturity)
        price = discount_factor * average_payoff

        logger.debug(
            f"Average payoff: {average_payoff:.4f}, "
            f"Discount factor: {discount_factor:.4f}, "
            f"Price: {price:.4f}"
        )

        return price

    def price_with_multiple_methods(
        self, methods: List[str]
    ) -> Dict[str, PricingResult]:
        """
        Price option using multiple methods for comparison.

        This satisfies the requirement: "a trader may wish to use both
        Quasi-Monte Carlo and Implicit Euler methods to price an option
        to see the difference."

        Args:
            methods: List of pricing method names

        Returns:
            Dictionary mapping method name to PricingResult
        """
        results = {}

        logger.info(f"Pricing with multiple methods: {methods}")

        for method in methods:
            try:
                import time

                start = time.time()
                price = self.price(method)
                elapsed = time.time() - start

                results[method] = PricingResult(
                    price=price, method=method, computation_time=elapsed
                )

            except Exception as e:
                logger.error(f"Method {method} failed: {str(e)}")
                results[method] = PricingResult(
                    price=0.0, method=method, metadata={"error": str(e)}
                )

        return results

    def calculate_greeks(self, method: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate Greeks (inherited from GreeksMixin).

        Overridden to add logging.
        """
        logger.info(f"Calculating Greeks with method: {method or self._greeks_method}")
        return super().calculate_greeks(method)


if __name__ == "__main__":
    print("=" * 70)
    print("Options Module - Concrete Implementation")
    print("=" * 70)

    # Create sample option
    market_data = MarketData(spot=100.0, risk_free_rate=0.05, dividend_yield=0.0)

    option_params = OptionParameters(
        strike=100.0,
        maturity=1.0,
        option_type=OptionType.CALL,
        volatility=0.2,
        asset_class=AssetClass.EQUITY,
        underlying_ticker="NIKKEI225",
    )

    jump_params = JumpDiffusionParams(jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2)

    # Create equity jump call option
    option = EquityJumpCallOption(
        market_data=market_data, option_params=option_params, jump_params=jump_params
    )

    print(f"\nOption: {option}")
    print(f"Repr: {repr(option)}")
    print(f"Moneyness: {option.moneyness:.4f}")

    # Test callable interface
    print(f"\nPricing (callable): {option():.4f}")

    # Test property setters
    print("\nTesting property setters:")
    option.spot = 105.0
    print(f"New spot: {option.spot}")
    print(f"New moneyness: {option.moneyness:.4f}")

    # Test Greeks
    print("\nGreeks:")
    greeks = option.calculate_greeks("analytical")
    for name, value in greeks.items():
        print(f"  {name.capitalize()}: {value:.4f}")

    # Test multiple pricing methods
    print("\nPricing with multiple methods:")
    results = option.price_with_multiple_methods(
        ["black_scholes", "monte_carlo", "jump_diffusion_mc"]
    )

    for method, result in results.items():
        print(f"  {method}: {result.price:.4f} ({result.computation_time:.4f}s)")

    print("\n" + "=" * 70)
