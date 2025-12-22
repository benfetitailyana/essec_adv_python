"""
Pricing interfaces using both ABC and Protocol for structural typing.

This module defines the core interfaces for option pricing:
- PricingInterface: ABC-based interface (requires inheritance)
- PricingProtocol: Protocol-based interface (duck typing, no inheritance required)

These interfaces demonstrate SOLID principles:
- Interface Segregation: Separate interfaces for pricing and Greeks
- Dependency Inversion: Depend on abstractions, not concrete implementations
"""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Optional, List
from enum import Enum


class OptionType(Enum):
    """Enumeration for option types."""

    CALL = "call"
    PUT = "put"


class AssetClass(Enum):
    """Enumeration for asset classes."""

    EQUITY = "equity"
    FX = "fx"
    RATES = "rates"
    COMMODITY = "commodity"
    CRYPTO = "crypto"


class PricingInterface(ABC):
    """
    Abstract Base Class defining the interface for option pricing.

    This ABC enforces that all concrete option classes implement:
    1. price() - Calculate option price
    2. calculate_greeks() - Calculate option Greeks

    Additional concrete methods provide common functionality.

    SOLID Principles:
    - Single Responsibility: Focused only on pricing interface definition
    - Open/Closed: Open for extension (inheritance), closed for modification
    - Liskov Substitution: All subclasses can be used interchangeably
    - Interface Segregation: Minimal, focused interface
    - Dependency Inversion: High-level modules depend on this abstraction
    """

    @abstractmethod
    def price(self, method: Optional[str] = None) -> float:
        """
        Calculate the option price using specified pricing method.

        Args:
            method: Pricing method to use (e.g., 'black_scholes', 'monte_carlo')
                   If None, uses default method for the option type.

        Returns:
            Option price as a float

        Raises:
            PricingCalculationException: If pricing calculation fails
        """
        pass

    @abstractmethod
    def calculate_greeks(self, method: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate option Greeks (Delta, Gamma, Vega, Theta, Rho).

        Args:
            method: Method for Greek calculation (e.g., 'analytical', 'bump_revalue')
                   If None, uses default method.

        Returns:
            Dictionary mapping Greek name to value
            Example: {'delta': 0.6, 'gamma': 0.02, 'vega': 15.5, ...}

        Raises:
            PricingCalculationException: If Greek calculation fails
        """
        pass

    def validate_parameters(self) -> bool:
        """
        Validate option parameters.

        Concrete method with default implementation that can be overridden.

        Returns:
            True if parameters are valid

        Raises:
            OptionPricingException: If parameters are invalid
        """
        return True

    def get_option_info(self) -> Dict[str, any]:
        """
        Get basic information about the option.

        Returns:
            Dictionary with option details
        """
        return {"type": "unknown", "asset_class": "unknown", "pricing_methods": []}


class PricingProtocol(Protocol):
    """
    Protocol-based interface demonstrating duck typing without inheritance.

    Any class implementing these methods is compatible with PricingProtocol,
    even without explicit inheritance. This demonstrates structural subtyping.

    Benefits:
    - No need for inheritance
    - More flexible than ABC
    - Better for composition-based designs
    - Supports gradual typing
    """

    def price(self, method: Optional[str] = None) -> float:
        """Calculate option price."""
        ...

    def calculate_greeks(self, method: Optional[str] = None) -> Dict[str, float]:
        """Calculate option Greeks."""
        ...


class GreeksInterface(ABC):
    """
    Abstract interface specifically for Greek calculations.

    This demonstrates Interface Segregation Principle - separating
    Greek calculations into its own interface.
    """

    @abstractmethod
    def delta(self) -> float:
        """Calculate Delta: ∂V/∂S (rate of change of option value w.r.t. underlying)."""
        pass

    @abstractmethod
    def gamma(self) -> float:
        """Calculate Gamma: ∂²V/∂S² (rate of change of Delta w.r.t. underlying)."""
        pass

    @abstractmethod
    def vega(self) -> float:
        """Calculate Vega: ∂V/∂σ (sensitivity to volatility)."""
        pass

    @abstractmethod
    def theta(self) -> float:
        """Calculate Theta: ∂V/∂t (time decay)."""
        pass

    @abstractmethod
    def rho(self) -> float:
        """Calculate Rho: ∂V/∂r (sensitivity to interest rate)."""
        pass


class PricingStrategyInterface(ABC):
    """
    Strategy pattern interface for different pricing methods.

    This enables runtime selection of pricing algorithm without
    changing the option class itself.

    Pattern: Strategy (GoF)
    Purpose: Define a family of algorithms, encapsulate each one,
             and make them interchangeable.
    """

    @abstractmethod
    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs
    ) -> float:
        """
        Calculate option price using this strategy.

        Args:
            spot: Current price of underlying asset
            strike: Strike price of option
            time_to_maturity: Time to maturity in years
            risk_free_rate: Risk-free interest rate
            volatility: Volatility of underlying asset
            **kwargs: Additional parameters specific to strategy

        Returns:
            Calculated option price
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this pricing strategy."""
        pass


class GreeksStrategyInterface(ABC):
    """
    Strategy pattern interface for different Greek calculation methods.

    Allows switching between analytical, numerical, and other methods
    at runtime without changing the option implementation.
    """

    @abstractmethod
    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate all Greeks using this strategy.

        Args:
            spot: Current price of underlying asset
            strike: Strike price of option
            time_to_maturity: Time to maturity in years
            risk_free_rate: Risk-free interest rate
            volatility: Volatility of underlying asset
            option_type: Call or Put
            **kwargs: Additional parameters

        Returns:
            Dictionary with all Greek values
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this Greek calculation strategy."""
        pass


if __name__ == "__main__":
    print("=" * 70)
    print("Option Pricing Interfaces Module")
    print("=" * 70)
    print("\nThis module defines:")
    print("1. PricingInterface (ABC) - requires inheritance")
    print("2. PricingProtocol - duck typing without inheritance")
    print("3. GreeksInterface (ABC) - separate Greek calculations")
    print("4. PricingStrategyInterface (ABC) - Strategy pattern for pricing")
    print("5. GreeksStrategyInterface (ABC) - Strategy pattern for Greeks")
    print("\nDemonstrates SOLID principles and GoF Strategy pattern")
    print("=" * 70)
