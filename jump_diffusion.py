"""
Jump diffusion simulation module.

Implements Merton Jump Diffusion model with:
- JumpProcess (composition) for modeling Poisson jumps
- MertonJumpModel for Euler discretization
- Generator for lazy evaluation of simulations

Demonstrates:
- Composition over inheritance (JumpProcess composed in MertonJumpModel)
- Generator pattern for memory efficiency
- Proper implementation of jump-diffusion SDE
"""

from typing import Generator, Tuple, List, Optional
import numpy as np
import math
from dataclasses import dataclass

from utils import (
    logger,
    PositiveFloat,
    NonNegativeFloat,
    PositiveInteger,
    validate_positive,
    validate_non_negative,
)
from models import JumpDiffusionParams


class JumpProcess:
    """
    Poisson jump process for modeling discontinuous price movements.

    This class is COMPOSED inside MertonJumpModel, demonstrating
    composition over inheritance. The jump logic is encapsulated
    separately from the diffusion process.

    Attributes:
        intensity: λ - expected number of jumps per unit time
        mean: μ_j - mean of log jump size
        std: δ - standard deviation of log jump size
    """

    # Using descriptors for validation
    intensity = NonNegativeFloat(default=0.0)
    mean = NonNegativeFloat(default=0.0)  # Can be negative in reality
    std = NonNegativeFloat(default=0.0)

    def __init__(self, intensity: float, mean: float, std: float):
        """
        Initialize jump process.

        Args:
            intensity: Jump intensity (λ)
            mean: Mean of log jump size (μ_j)
            std: Std dev of log jump size (δ)
        """
        self.intensity = intensity
        self.mean = mean
        self.std = std

        logger.debug(f"JumpProcess created: λ={intensity}, μ_j={mean}, δ={std}")

    @property
    def drift_correction(self) -> float:
        """
        Calculate drift correction for risk-neutral pricing.

        r_j = λ(e^(μ_j + 0.5δ²) - 1)

        This correction ensures the jump-diffusion model is risk-neutral.
        """
        return self.intensity * (math.exp(self.mean + 0.5 * self.std**2) - 1)

    def generate_jumps(
        self, dt: float, size: int, rng: Optional[np.random.Generator] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Poisson jumps and jump sizes.

        Args:
            dt: Time step
            size: Number of samples to generate
            rng: Random number generator (optional)

        Returns:
            Tuple of (jump_indicators, jump_sizes)
            - jump_indicators: Array of 0s and 1s indicating if jump occurred
            - jump_sizes: Array of jump magnitudes (only meaningful when jump occurred)
        """
        if rng is None:
            rng = np.random.default_rng()

        # Number of jumps follows Poisson distribution
        jump_indicators = rng.poisson(self.intensity * dt, size=size)

        # Jump sizes follow log-normal distribution
        jump_sizes = rng.normal(self.mean, self.std, size=size)

        return jump_indicators, jump_sizes

    def __repr__(self) -> str:
        return (
            f"JumpProcess(λ={self.intensity:.4f}, "
            f"μ_j={self.mean:.4f}, δ={self.std:.4f})"
        )


class MertonJumpModel:
    """
    Merton Jump Diffusion model for asset price simulation.

    Implements the SDE:
    dS_t = (r - r_j)S_t dt + σS_t dZ_t + J_t S_t dN_t

    where:
    - r: risk-free rate
    - r_j: jump drift correction
    - σ: volatility
    - Z_t: Brownian motion
    - J_t: jump size
    - N_t: Poisson process

    Euler discretization:
    S_t = S_{t-Δt} * {exp((r - r_j - 0.5σ²)Δt + σ√Δt Z₁) + (exp(μ_j + δZ₂) - 1) * y_t}

    Demonstrates:
    - Composition: JumpProcess is composed inside, not inherited
    - Generator: Uses yield for memory-efficient simulations
    - Proper validation and logging
    """

    def __init__(
        self,
        initial_price: float,
        risk_free_rate: float,
        volatility: float,
        jump_params: JumpDiffusionParams,
        time_horizon: float = 1.0,
        dt: float = 0.01,
        seed: Optional[int] = None,
    ):
        """
        Initialize Merton Jump Diffusion model.

        Args:
            initial_price: S₀ - initial asset price
            risk_free_rate: r - risk-free rate
            volatility: σ - volatility
            jump_params: Jump process parameters
            time_horizon: T - total time horizon
            dt: Δt - time step size
            seed: Random seed for reproducibility
        """
        # Validate inputs
        validate_positive(initial_price, "initial_price")
        validate_non_negative(risk_free_rate, "risk_free_rate")
        validate_non_negative(volatility, "volatility")
        validate_positive(time_horizon, "time_horizon")
        validate_positive(dt, "dt")

        self.initial_price = initial_price
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_horizon = time_horizon
        self.dt = dt
        self.seed = seed

        # Composition: JumpProcess is a component, not inherited
        self.jump_process = JumpProcess(
            intensity=jump_params.jump_intensity,
            mean=jump_params.jump_mean,
            std=jump_params.jump_std,
        )

        # Calculate derived parameters
        self.num_steps = int(time_horizon / dt)
        self.rng = np.random.default_rng(seed)

        logger.info(
            f"MertonJumpModel initialized: S₀={initial_price}, r={risk_free_rate}, "
            f"σ={volatility}, T={time_horizon}, Δt={dt}, steps={self.num_steps}"
        )
        logger.info(f"Jump process: {self.jump_process}")

    def simulate_path(self) -> np.ndarray:
        """
        Simulate a single price path.

        Returns:
            Array of prices from t=0 to t=T
        """
        prices = np.zeros(self.num_steps + 1)
        prices[0] = self.initial_price

        # Drift and diffusion terms
        drift = (
            self.risk_free_rate
            - self.jump_process.drift_correction
            - 0.5 * self.volatility**2
        )
        vol_sqrt_dt = self.volatility * math.sqrt(self.dt)

        for i in range(1, self.num_steps + 1):
            # Standard Brownian motion for diffusion
            z1 = self.rng.standard_normal()

            # Brownian motion for jump size
            z2 = self.rng.standard_normal()

            # Poisson jump indicator
            jump_occurs = self.rng.poisson(self.jump_process.intensity * self.dt)

            # Euler discretization
            diffusion_term = math.exp(drift * self.dt + vol_sqrt_dt * z1)

            if jump_occurs > 0:
                jump_size = (
                    math.exp(self.jump_process.mean + self.jump_process.std * z2) - 1
                )
            else:
                jump_size = 0

            prices[i] = prices[i - 1] * (diffusion_term + jump_size)

        return prices

    def simulate_terminal_prices(
        self, num_simulations: int
    ) -> Generator[float, None, None]:
        """
        Generate terminal prices lazily using a generator.

        This demonstrates:
        1. Generator pattern (yield) for memory efficiency
        2. Lazy evaluation - prices computed on demand
        3. Memory efficient - only one path stored at a time

        Args:
            num_simulations: Number of paths to simulate

        Yields:
            Terminal price (at t=T) for each simulation

        Example:
            >>> model = MertonJumpModel(...)
            >>> terminal_prices = model.simulate_terminal_prices(10000)
            >>> avg_price = sum(terminal_prices) / 10000
        """
        logger.info(f"Starting generator: {num_simulations} simulations")

        for i in range(num_simulations):
            path = self.simulate_path()
            terminal_price = path[-1]

            # Log progress periodically
            if (i + 1) % 1000 == 0:
                logger.debug(f"Generated {i + 1}/{num_simulations} paths")

            yield terminal_price

        logger.info(f"Generator completed: {num_simulations} simulations")

    def simulate_paths(self, num_simulations: int) -> np.ndarray:
        """
        Simulate multiple complete paths (for plotting).

        Args:
            num_simulations: Number of paths to simulate

        Returns:
            Array of shape (num_simulations, num_steps + 1)
        """
        logger.info(f"Simulating {num_simulations} complete paths")

        paths = np.zeros((num_simulations, self.num_steps + 1))

        for i in range(num_simulations):
            paths[i] = self.simulate_path()

        logger.info("Path simulation completed")
        return paths

    def __call__(self, num_simulations: int = 1) -> np.ndarray:
        """
        Make the model callable for convenient usage.

        Dunder method: __call__
        Allows: prices = model(1000)
        """
        if num_simulations == 1:
            return self.simulate_path()
        else:
            return self.simulate_paths(num_simulations)

    def __len__(self) -> int:
        """
        Return number of time steps.

        Dunder method: __len__
        Allows: steps = len(model)
        """
        return self.num_steps

    def __iter__(self) -> Generator[np.ndarray, None, None]:
        """
        Iterate over simulated paths indefinitely.

        Dunder method: __iter__
        Allows: for path in model: ...
        """
        while True:
            yield self.simulate_path()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MertonJumpModel(S₀={self.initial_price}, r={self.risk_free_rate}, "
            f"σ={self.volatility}, T={self.time_horizon}, Δt={self.dt}, "
            f"steps={self.num_steps}, {self.jump_process})"
        )


def calculate_call_payoff(terminal_price: float, strike: float) -> float:
    """
    Calculate European call option payoff.

    Function as first-class citizen - can be passed as argument.

    Args:
        terminal_price: Price at maturity
        strike: Strike price

    Returns:
        max(S_T - K, 0)
    """
    return max(terminal_price - strike, 0)


def calculate_put_payoff(terminal_price: float, strike: float) -> float:
    """
    Calculate European put option payoff.

    Args:
        terminal_price: Price at maturity
        strike: Strike price

    Returns:
        max(K - S_T, 0)
    """
    return max(strike - terminal_price, 0)


if __name__ == "__main__":
    print("=" * 70)
    print("Jump Diffusion Module - Merton Model")
    print("=" * 70)

    # Sample parameters from instructions
    jump_params = JumpDiffusionParams(jump_intensity=0.75, jump_mean=-0.6, jump_std=0.2)

    print(f"\nJump Parameters: {jump_params}")
    print(f"Drift correction: {jump_params.drift_correction:.6f}")

    # Create model
    model = MertonJumpModel(
        initial_price=100.0,
        risk_free_rate=0.05,
        volatility=0.2,
        jump_params=jump_params,
        time_horizon=1.0,
        dt=0.25,
        seed=42,
    )

    print(f"\nModel: {model}")
    print(f"Number of steps: {len(model)}")

    # Test generator
    print("\nTesting generator (first 5 terminal prices):")
    gen = model.simulate_terminal_prices(5)
    for i, price in enumerate(gen, 1):
        print(f"  Simulation {i}: S_T = {price:.4f}")

    # Test callable
    print("\nTesting callable interface:")
    single_path = model()
    print(f"  Single path terminal price: {single_path[-1]:.4f}")

    # Calculate option payoffs
    strike = 100.0
    print(f"\nCall option payoffs (K={strike}):")
    gen = model.simulate_terminal_prices(5)
    for i, S_T in enumerate(gen, 1):
        payoff = calculate_call_payoff(S_T, strike)
        print(f"  Path {i}: S_T={S_T:.4f}, Payoff={payoff:.4f}")

    print("\n" + "=" * 70)
