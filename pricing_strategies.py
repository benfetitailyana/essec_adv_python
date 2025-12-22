"""
Pricing strategies implementing the Strategy Pattern (GoF).

This module provides various pricing strategies that can be selected at runtime.
Demonstrates the Strategy Pattern for algorithm selection and functions as first-class citizens.

Available Strategies:
- Black-Scholes
- Black-Scholes-Merton (with dividends)
- Binomial (CRR, Jarrow-Rudd)
- Monte Carlo (standard, quasi, jump diffusion)
- Finite Difference methods

SOLID Principles:
- Single Responsibility: Each strategy handles one pricing method
- Open/Closed: New strategies can be added without modifying existing code
- Liskov Substitution: All strategies are interchangeable
- Dependency Inversion: Clients depend on PricingStrategyInterface abstraction
"""

from typing import Callable, Dict, Optional
import math
from interfaces import PricingStrategyInterface, OptionType
from utils import logger, PricingCalculationException


# ==============================================================================
# Black-Scholes Family Strategies
# ==============================================================================


class BlackScholesStrategy(PricingStrategyInterface):
    """
    Classic Black-Scholes pricing for European options.

    Stub implementation - desk quants would fill in the details.
    """

    def name(self) -> str:
        return "Black-Scholes"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType = OptionType.CALL,
        **kwargs,
    ) -> float:
        """
        Calculate option price using Black-Scholes formula.

        Stub implementation - returns a placeholder calculation.
        Real implementation would use the full BS formula with N(d1) and N(d2).
        """
        logger.info(
            f"Pricing with {self.name()}: S={spot}, K={strike}, T={time_to_maturity}"
        )

        # Placeholder: Simple intrinsic value + time value estimate
        # Desk quants would implement full formula here
        intrinsic = (
            max(spot - strike, 0)
            if option_type == OptionType.CALL
            else max(strike - spot, 0)
        )
        time_value = (
            spot * volatility * math.sqrt(time_to_maturity) * 0.4
        )  # Rough approximation

        return intrinsic + time_value


class BlackScholesMertonStrategy(PricingStrategyInterface):
    """
    Black-Scholes-Merton with continuous dividend yield.

    Extends Black-Scholes to account for dividend payments.
    """

    def name(self) -> str:
        return "Black-Scholes-Merton"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        dividend_yield: float = 0.0,
        option_type: OptionType = OptionType.CALL,
        **kwargs,
    ) -> float:
        """Calculate price with dividend adjustment."""
        logger.info(f"Pricing with {self.name()}: dividend_yield={dividend_yield}")

        # Adjust spot for dividends
        adjusted_spot = spot * math.exp(-dividend_yield * time_to_maturity)

        # Use Black-Scholes on adjusted spot (stub)
        bs = BlackScholesStrategy()
        return bs.calculate_price(
            adjusted_spot,
            strike,
            time_to_maturity,
            risk_free_rate,
            volatility,
            option_type,
        )


class BlackModelStrategy(PricingStrategyInterface):
    """
    Black's model for options on futures/forwards.

    Used in commodities and interest rate markets.
    """

    def name(self) -> str:
        return "Black's Model"

    def calculate_price(
        self,
        spot: float,  # Forward price in this context
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation for Black's model."""
        logger.info(f"Pricing with {self.name()} (futures/forwards)")
        # Desk quants implement full Black formula here
        return spot * volatility * math.sqrt(time_to_maturity) * 0.35


# ==============================================================================
# Tree-Based Strategies
# ==============================================================================


class BinomialCRRStrategy(PricingStrategyInterface):
    """
    Cox-Ross-Rubinstein binomial tree model.

    Discrete-time lattice approach for American/European options.
    """

    def name(self) -> str:
        return "Binomial-CRR"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        num_steps: int = 100,
        **kwargs,
    ) -> float:
        """
        Stub implementation of CRR binomial tree.

        Real implementation would build tree and work backwards.
        """
        logger.info(f"Pricing with {self.name()}: {num_steps} steps")
        # Placeholder calculation
        # Desk quants implement tree construction and backward induction
        return spot * 0.5 + strike * 0.3


class JarrowRuddStrategy(PricingStrategyInterface):
    """
    Jarrow-Rudd binomial model with alternative up/down factors.

    Uses different parameterization than CRR.
    """

    def name(self) -> str:
        return "Jarrow-Rudd"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.52 + strike * 0.28


class TrinomialStrategy(PricingStrategyInterface):
    """
    Standard trinomial tree (Boyle's method).

    Three possible moves at each node: up, down, middle.
    """

    def name(self) -> str:
        return "Trinomial"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.48 + strike * 0.32


# ==============================================================================
# Finite Difference Strategies
# ==============================================================================


class ExplicitFDStrategy(PricingStrategyInterface):
    """
    Explicit Finite Difference (Forward Euler) method.

    Solves PDE using explicit time stepping.
    """

    def name(self) -> str:
        return "Explicit-FD"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation of explicit FD."""
        logger.info(f"Pricing with {self.name()}")
        # Desk quants implement grid setup and time stepping
        return spot * 0.51 + strike * 0.29


class ImplicitFDStrategy(PricingStrategyInterface):
    """
    Implicit Finite Difference (Backward Euler) method.

    More stable than explicit method, requires solving linear system.
    """

    def name(self) -> str:
        return "Implicit-FD"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.50 + strike * 0.30


class CrankNicolsonStrategy(PricingStrategyInterface):
    """
    Crank-Nicolson finite difference scheme.

    Second-order accurate in both time and space.
    """

    def name(self) -> str:
        return "Crank-Nicolson"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.495 + strike * 0.305


# ==============================================================================
# Monte Carlo Strategies
# ==============================================================================


class MonteCarloStrategy(PricingStrategyInterface):
    """
    Standard Monte Carlo simulation for European options.

    Simulates price paths and discounts expected payoff.
    """

    def name(self) -> str:
        return "Monte-Carlo"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        num_simulations: int = 10000,
        option_type: OptionType = OptionType.CALL,
        **kwargs,
    ) -> float:
        """Stub MC implementation."""
        logger.info(f"Pricing with {self.name()}: {num_simulations} simulations")
        # Desk quants implement full MC with proper variance reduction
        return spot * 0.49 + strike * 0.31


class QuasiMonteCarloStrategy(PricingStrategyInterface):
    """
    Quasi-Monte Carlo using low-discrepancy sequences.

    Better convergence than standard MC for smooth payoffs.
    """

    def name(self) -> str:
        return "Quasi-Monte-Carlo"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub QMC implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.505 + strike * 0.295


class JumpDiffusionMCStrategy(PricingStrategyInterface):
    """
    Monte Carlo for jump-diffusion models (Merton).

    Includes Poisson jumps in the simulation.
    This is the main strategy used for the project's jump call options.
    """

    def name(self) -> str:
        return "Jump-Diffusion-MC"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        jump_intensity: float = 0.75,
        jump_mean: float = -0.6,
        jump_std: float = 0.2,
        num_simulations: int = 10000,
        option_type: OptionType = OptionType.CALL,
        **kwargs,
    ) -> float:
        """
        Stub implementation of jump-diffusion MC.

        Real implementation uses the generator from jump_diffusion module.
        """
        logger.info(
            f"Pricing with {self.name()}: λ={jump_intensity}, "
            f"μ_j={jump_mean}, δ={jump_std}"
        )
        # Placeholder - actual implementation in jump_diffusion module
        jump_adjustment = jump_intensity * abs(jump_mean) * 0.5
        return max(spot - strike, 0) * (1 + jump_adjustment)


class LSMCStrategy(PricingStrategyInterface):
    """
    Least Squares Monte Carlo (Longstaff-Schwartz) for American options.

    Uses regression to estimate continuation value.
    """

    def name(self) -> str:
        return "LSMC"

    def calculate_price(
        self,
        spot: float,
        strike: float,
        time_to_maturity: float,
        risk_free_rate: float,
        volatility: float,
        **kwargs,
    ) -> float:
        """Stub LSMC implementation."""
        logger.info(f"Pricing with {self.name()}")
        return spot * 0.52 + strike * 0.28


# ==============================================================================
# Strategy Registry and Function-as-Strategy
# ==============================================================================

# Dictionary mapping strategy names to strategy instances
PRICING_STRATEGIES: Dict[str, PricingStrategyInterface] = {
    "black_scholes": BlackScholesStrategy(),
    "black_scholes_merton": BlackScholesMertonStrategy(),
    "black": BlackModelStrategy(),
    "binomial_crr": BinomialCRRStrategy(),
    "jarrow_rudd": JarrowRuddStrategy(),
    "trinomial": TrinomialStrategy(),
    "explicit_fd": ExplicitFDStrategy(),
    "implicit_fd": ImplicitFDStrategy(),
    "crank_nicolson": CrankNicolsonStrategy(),
    "monte_carlo": MonteCarloStrategy(),
    "quasi_monte_carlo": QuasiMonteCarloStrategy(),
    "jump_diffusion_mc": JumpDiffusionMCStrategy(),
    "lsmc": LSMCStrategy(),
}


def get_strategy(name: str) -> PricingStrategyInterface:
    """
    Get pricing strategy by name.

    Args:
        name: Strategy name (case-insensitive)

    Returns:
        PricingStrategyInterface instance

    Raises:
        PricingCalculationException: If strategy not found
    """
    strategy = PRICING_STRATEGIES.get(name.lower())
    if strategy is None:
        available = ", ".join(PRICING_STRATEGIES.keys())
        raise PricingCalculationException(
            f"Unknown pricing strategy '{name}'. Available: {available}"
        )
    return strategy


# Functions as first-class citizens: function-based strategies
def simple_intrinsic_pricer(
    spot: float, strike: float, option_type: OptionType = OptionType.CALL
) -> float:
    """
    Simple function-based strategy: just intrinsic value.

    Demonstrates functions as first-class citizens that can be
    passed around and used as strategies without OOP.
    """
    if option_type == OptionType.CALL:
        return max(spot - strike, 0)
    else:
        return max(strike - spot, 0)


# Type alias for function-based strategies
PricingFunction = Callable[[float, float, float, float, float], float]


if __name__ == "__main__":
    print("=" * 70)
    print("Pricing Strategies Module - Strategy Pattern (GoF)")
    print("=" * 70)

    print("\nAvailable strategies:")
    for name, strategy in PRICING_STRATEGIES.items():
        print(f"  - {name}: {strategy.name()}")

    print("\nTesting a few strategies:")
    spot, strike, T, r, vol = 100.0, 100.0, 1.0, 0.05, 0.2

    for strategy_name in ["black_scholes", "monte_carlo", "jump_diffusion_mc"]:
        strategy = get_strategy(strategy_name)
        price = strategy.calculate_price(spot, strike, T, r, vol)
        print(f"{strategy.name()}: {price:.4f}")

    print("\nFunction-as-strategy example:")
    intrinsic_price = simple_intrinsic_pricer(105, 100, OptionType.CALL)
    print(f"Simple intrinsic: {intrinsic_price:.4f}")

    print("\n" + "=" * 70)
