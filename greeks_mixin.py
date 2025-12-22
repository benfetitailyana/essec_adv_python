"""
Greeks calculation mixin and strategies.

This module provides a mixin class for adding Greek calculations to options,
demonstrating composition over inheritance for modular functionality.

Greeks Supported:
- Delta: ∂V/∂S (sensitivity to spot price)
- Gamma: ∂²V/∂S² (convexity)
- Vega: ∂V/∂σ (volatility sensitivity)
- Theta: ∂V/∂t (time decay)
- Rho: ∂V/∂r (interest rate sensitivity)

Calculation Methods:
- Analytical formulas
- Bump-and-revalue (numerical)
- Tree-based
- FD grid-based
"""

from typing import Dict, Callable, Optional
import math
from interfaces import GreeksStrategyInterface, OptionType
from utils import logger, safe_division


class AnalyticalGreeksStrategy(GreeksStrategyInterface):
    """
    Analytical Greek formulas (e.g., Black-Scholes Greeks).

    Most efficient when closed-form solutions exist.
    """

    def name(self) -> str:
        return "Analytical"

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType,
        **kwargs,
    ) -> Dict[str, float]:
        """
        Calculate Greeks using analytical formulas.

        Stub implementation - desk quants would implement full BS Greeks.
        """
        logger.debug(f"Calculating Greeks with {self.name()} method")

        # Simplified placeholder Greeks
        # Real implementation would use proper d1, d2, N(d1), N'(d1), etc.
        sqrt_T = math.sqrt(time_to_maturity)

        delta = 0.5 if option_type == OptionType.CALL else -0.5
        gamma = 0.02 / (spot * volatility * sqrt_T) if sqrt_T > 0 else 0
        vega = spot * sqrt_T * 0.4
        theta = -spot * volatility / (2 * sqrt_T) if sqrt_T > 0 else 0
        rho = strike * time_to_maturity * 0.5

        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "rho": rho,
        }


class BumpAndRevalueGreeksStrategy(GreeksStrategyInterface):
    """
    Numerical Greeks via bump-and-revalue.

    General method that works for any pricing model.
    Calculates finite differences by bumping parameters.
    """

    def name(self) -> str:
        return "Bump-and-Revalue"

    def __init__(
        self, pricing_func: Optional[Callable] = None, bump_size: float = 0.01
    ):
        """
        Initialize with pricing function and bump size.

        Args:
            pricing_func: Function that prices the option
            bump_size: Relative bump size (1% by default)
        """
        self.pricing_func = pricing_func
        self.bump_size = bump_size

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType,
        **kwargs,
    ) -> Dict[str, float]:
        """
        Calculate Greeks by bumping parameters and repricing.

        Stub implementation showing the approach.
        """
        logger.debug(
            f"Calculating Greeks with {self.name()} method (bump={self.bump_size})"
        )

        # Placeholder - would call pricing_func with bumped parameters
        base_price = spot * 0.5  # Simplified

        # Delta: bump spot
        spot_up = spot * (1 + self.bump_size)
        price_up = spot_up * 0.5
        delta = (price_up - base_price) / (spot * self.bump_size)

        # Gamma: second derivative
        spot_down = spot * (1 - self.bump_size)
        price_down = spot_down * 0.5
        gamma = (price_up - 2 * base_price + price_down) / (
            (spot * self.bump_size) ** 2
        )

        # Vega: bump volatility
        vol_bump = 0.01  # 1% absolute
        vega = base_price * vol_bump * 10  # Simplified

        # Theta: bump time
        theta = -base_price * 0.05  # Simplified

        # Rho: bump rate
        rho = base_price * time_to_maturity * 0.5  # Simplified

        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "rho": rho,
        }


class TreeBasedGreeksStrategy(GreeksStrategyInterface):
    """Greeks from binomial/trinomial trees."""

    def name(self) -> str:
        return "Tree-Based"

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType,
        **kwargs,
    ) -> Dict[str, float]:
        """Stub implementation."""
        logger.debug(f"Calculating Greeks with {self.name()} method")
        return {"delta": 0.48, "gamma": 0.019, "vega": 18.5, "theta": -3.2, "rho": 24.1}


class FDGridGreeksStrategy(GreeksStrategyInterface):
    """Greeks from finite difference grid."""

    def name(self) -> str:
        return "FD-Grid"

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType,
        **kwargs,
    ) -> Dict[str, float]:
        """Stub implementation."""
        logger.debug(f"Calculating Greeks with {self.name()} method")
        return {"delta": 0.51, "gamma": 0.021, "vega": 19.2, "theta": -3.5, "rho": 25.3}


# Registry of Greek calculation strategies
GREEKS_STRATEGIES: Dict[str, GreeksStrategyInterface] = {
    "analytical": AnalyticalGreeksStrategy(),
    "bump_revalue": BumpAndRevalueGreeksStrategy(),
    "tree": TreeBasedGreeksStrategy(),
    "fd_grid": FDGridGreeksStrategy(),
}


def get_greeks_strategy(name: str) -> GreeksStrategyInterface:
    """Get Greeks calculation strategy by name."""
    strategy = GREEKS_STRATEGIES.get(name.lower())
    if strategy is None:
        available = ", ".join(GREEKS_STRATEGIES.keys())
        raise ValueError(f"Unknown Greeks strategy '{name}'. Available: {available}")
    return strategy


class GreeksMixin:
    """
    Mixin class to add Greek calculations to options.

    This demonstrates composition - Greeks functionality is added
    modularly without deep inheritance hierarchies.

    Usage:
        class MyOption(BaseOption, GreeksMixin):
            pass

    The option class must have these attributes:
    - spot, strike, time_to_maturity, risk_free_rate, volatility
    - option_type

    SOLID Principle: Interface Segregation
    - Greeks are separated into their own mixin
    - Options can choose whether to include Greeks functionality
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._greeks_cache: Optional[Dict[str, float]] = None
        self._greeks_method: str = "analytical"

    def calculate_greeks(self, method: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate all Greeks using specified method.

        Args:
            method: Calculation method ('analytical', 'bump_revalue', etc.)
                   If None, uses self._greeks_method

        Returns:
            Dictionary with all Greek values
        """
        if method is None:
            method = self._greeks_method

        strategy = get_greeks_strategy(method)

        greeks = strategy.calculate_greeks(
            spot=self.spot,
            strike=self.strike,
            time_to_maturity=self.time_to_maturity,
            risk_free_rate=self.risk_free_rate,
            volatility=self.volatility,
            option_type=self.option_type,
        )

        # Cache the results
        self._greeks_cache = greeks
        return greeks

    @property
    def delta(self) -> float:
        """
        Delta: ∂V/∂S

        Rate of change of option value with respect to underlying price.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache["delta"]

    @property
    def gamma(self) -> float:
        """
        Gamma: ∂²V/∂S²

        Rate of change of Delta with respect to underlying price.
        Measures convexity.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache["gamma"]

    @property
    def vega(self) -> float:
        """
        Vega: ∂V/∂σ

        Sensitivity to volatility changes.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache["vega"]

    @property
    def theta(self) -> float:
        """
        Theta: ∂V/∂t

        Time decay - how much value the option loses per day.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache["theta"]

    @property
    def rho(self) -> float:
        """
        Rho: ∂V/∂r

        Sensitivity to interest rate changes.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache["rho"]

    @property
    def greeks(self) -> Dict[str, float]:
        """
        Get all Greeks as a dictionary.

        Convenience property for accessing all Greeks at once.
        """
        if self._greeks_cache is None:
            self.calculate_greeks()
        return self._greeks_cache

    def set_greeks_method(self, method: str) -> None:
        """
        Set the default method for Greek calculations.

        Args:
            method: Method name ('analytical', 'bump_revalue', etc.)
        """
        self._greeks_method = method
        self._greeks_cache = None  # Invalidate cache


if __name__ == "__main__":
    print("=" * 70)
    print("Greeks Mixin Module")
    print("=" * 70)

    print("\nAvailable Greeks calculation strategies:")
    for name, strategy in GREEKS_STRATEGIES.items():
        print(f"  - {name}: {strategy.name()}")

    print("\nTesting Greeks calculation:")
    strategy = get_greeks_strategy("analytical")
    greeks = strategy.calculate_greeks(
        spot=100,
        strike=100,
        time_to_maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type=OptionType.CALL,
    )

    print("\nCalculated Greeks:")
    for greek_name, value in greeks.items():
        print(f"  {greek_name.capitalize()}: {value:.4f}")

    print("\n" + "=" * 70)
