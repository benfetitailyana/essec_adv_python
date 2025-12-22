"""
Domain model classes using @dataclass for efficient parameter storage.

This module defines dataclasses for:
- Market data and option parameters
- Jump diffusion parameters
- Model configurations

Dataclasses provide:
- Automatic __init__, __repr__, __eq__, __hash__
- Reduced memory footprint
- Type hints built-in
- Immutability options with frozen=True
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from interfaces import OptionType, AssetClass


@dataclass(frozen=True)
class MarketData:
    """
    Immutable market data for option pricing.

    Using frozen=True makes this immutable and hashable,
    which is appropriate for market snapshots.

    Attributes:
        spot: Current price of underlying asset
        risk_free_rate: Risk-free interest rate (annualized)
        dividend_yield: Continuous dividend yield (default 0)
        timestamp: When this market data was captured
    """

    spot: float
    risk_free_rate: float
    dividend_yield: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate market data after initialization."""
        if self.spot <= 0:
            raise ValueError(f"Spot price must be positive, got {self.spot}")
        if self.dividend_yield < 0:
            raise ValueError(
                f"Dividend yield cannot be negative, got {self.dividend_yield}"
            )


@dataclass(frozen=True)
class OptionParameters:
    """
    Immutable option contract parameters.

    These parameters define the option contract terms and don't change
    during the life of the option.

    Attributes:
        strike: Strike price
        maturity: Time to maturity in years
        option_type: Call or Put
        volatility: Implied or historical volatility
        asset_class: Asset class of underlying
        underlying_ticker: Ticker symbol (e.g., 'NIKKEI225', 'EURUSD')
    """

    strike: float
    maturity: float
    option_type: OptionType
    volatility: float
    asset_class: AssetClass = AssetClass.EQUITY
    underlying_ticker: str = "UNKNOWN"

    def __post_init__(self):
        """Validate option parameters."""
        if self.strike <= 0:
            raise ValueError(f"Strike must be positive, got {self.strike}")
        if self.maturity <= 0:
            raise ValueError(f"Maturity must be positive, got {self.maturity}")
        if self.volatility < 0:
            raise ValueError(f"Volatility cannot be negative, got {self.volatility}")


@dataclass(frozen=True)
class JumpDiffusionParams:
    """
    Parameters for Merton Jump Diffusion model.

    Implements the jump-diffusion SDE:
    dS_t = (r - r_j) S_t dt + σ S_t dZ_t + J_t S_t dN_t

    where r_j = λ(e^(μ_j + 0.5δ²) - 1) is the drift correction

    Attributes:
        jump_intensity: λ - expected number of jumps per year
        jump_mean: μ_j - mean of log jump size
        jump_std: δ - standard deviation of log jump size
    """

    jump_intensity: float  # λ (lambda)
    jump_mean: float  # μ_j (mu_j)
    jump_std: float  # δ (delta)

    def __post_init__(self):
        """Validate jump parameters."""
        if self.jump_intensity < 0:
            raise ValueError(
                f"Jump intensity must be non-negative, got {self.jump_intensity}"
            )
        if self.jump_std < 0:
            raise ValueError(f"Jump std must be non-negative, got {self.jump_std}")

    @property
    def drift_correction(self) -> float:
        """
        Calculate drift correction r_j = λ(e^(μ_j + 0.5δ²) - 1).

        This ensures risk-neutral pricing in the jump-diffusion framework.
        """
        import math

        return self.jump_intensity * (
            math.exp(self.jump_mean + 0.5 * self.jump_std**2) - 1
        )


@dataclass
class SimulationConfig:
    """
    Configuration for Monte Carlo simulations.

    This is mutable (not frozen) because simulation parameters
    might be adjusted during runtime.

    Attributes:
        num_simulations: Number of Monte Carlo paths
        num_time_steps: Number of time steps per path
        seed: Random seed for reproducibility
        antithetic: Whether to use antithetic variates
    """

    num_simulations: int = 10000
    num_time_steps: int = 252  # Daily steps for 1 year
    seed: Optional[int] = None
    antithetic: bool = False

    def __post_init__(self):
        """Validate simulation configuration."""
        if self.num_simulations <= 0:
            raise ValueError(
                f"Number of simulations must be positive, got {self.num_simulations}"
            )
        if self.num_time_steps <= 0:
            raise ValueError(
                f"Number of time steps must be positive, got {self.num_time_steps}"
            )


@dataclass
class PricingResult:
    """
    Result of option pricing calculation.

    Mutable dataclass to store pricing results with metadata.

    Attributes:
        price: Calculated option price
        method: Pricing method used
        greeks: Dictionary of Greek values (optional)
        computation_time: Time taken for calculation in seconds
        metadata: Additional information about the calculation
    """

    price: float
    method: str
    greeks: Optional[Dict[str, float]] = None
    computation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """String representation for logging and display."""
        greeks_str = ""
        if self.greeks:
            greeks_str = ", Greeks: " + ", ".join(
                f"{k}={v:.4f}" for k, v in self.greeks.items()
            )
        return (
            f"PricingResult(price={self.price:.4f}, method={self.method}, "
            f"time={self.computation_time:.4f}s{greeks_str})"
        )


@dataclass
class TraderInfo:
    """
    Information about a trader.

    Attributes:
        trader_id: Unique trader identifier
        name: Trader name
        desk: Trading desk
        email: Contact email (optional)
    """

    trader_id: str
    name: str
    desk: str
    email: Optional[str] = None

    def __post_init__(self):
        """Validate trader information."""
        if not self.trader_id.strip():
            raise ValueError("Trader ID cannot be empty")
        if not self.name.strip():
            raise ValueError("Trader name cannot be empty")
        if not self.desk.strip():
            raise ValueError("Desk cannot be empty")

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.trader_id}, Desk: {self.desk})"


@dataclass
class OrderInfo:
    """
    Information about an option order.

    Attributes:
        order_id: Unique order identifier
        trader_info: Trader placing the order
        quantity: Number of contracts (positive for buy, negative for sell)
        underlying: Underlying asset ticker
        strike: Strike price
        maturity: Time to maturity in years
        option_type: Call or Put
        timestamp: When order was placed
        status: Order status
    """

    order_id: str
    trader_info: TraderInfo
    quantity: int
    underlying: str
    strike: float
    maturity: float
    option_type: OptionType
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"

    def __post_init__(self):
        """Validate order information."""
        if not self.order_id.strip():
            raise ValueError("Order ID cannot be empty")
        if self.quantity == 0:
            raise ValueError("Order quantity cannot be zero")
        if self.strike <= 0:
            raise ValueError(f"Strike must be positive, got {self.strike}")
        if self.maturity <= 0:
            raise ValueError(f"Maturity must be positive, got {self.maturity}")

    @property
    def side(self) -> str:
        """Return 'buy' or 'sell' based on quantity sign."""
        return "buy" if self.quantity > 0 else "sell"

    def __str__(self) -> str:
        return (
            f"Order {self.order_id}: {abs(self.quantity)} {self.option_type.value} "
            f"options @ {self.strike} on {self.underlying} "
            f"({self.side.upper()}) by {self.trader_info.name}"
        )


if __name__ == "__main__":
    print("=" * 70)
    print("Domain Models Module - @dataclass examples")
    print("=" * 70)

    # Create sample market data
    market = MarketData(spot=100.0, risk_free_rate=0.05, dividend_yield=0.02)
    print(f"\nMarket Data: {market}")

    # Create option parameters
    option_params = OptionParameters(
        strike=100.0,
        maturity=1.0,
        option_type=OptionType.CALL,
        volatility=0.2,
        underlying_ticker="NIKKEI225",
    )
    print(f"Option Parameters: {option_params}")

    # Create jump parameters
    jump_params = JumpDiffusionParams(jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2)
    print(f"Jump Parameters: {jump_params}")
    print(f"Drift correction: {jump_params.drift_correction:.6f}")

    # Create trader info
    trader = TraderInfo(
        trader_id="AJ001",
        name="Adam Jones",
        desk="JapanEQExotics",
        email="adam.jones@bankxyz.com",
    )
    print(f"\nTrader: {trader}")

    print("\n" + "=" * 70)
