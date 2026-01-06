"""Merton jump diffusion Euler simulator with lazy generator."""
from __future__ import annotations

import math
import random
import numpy as np
from dataclasses import dataclass
from typing import Generator, Iterable, Iterator

from descriptors import NonNegativeFloat, PositiveInt
from exceptions import PricingError


@dataclass
class JumpParameters:
    intensity: float
    mean_jump: float
    jump_vol: float


class MertonJumpModel:
    """Euler-discretized Merton jump diffusion with Poisson jumps."""

    spot = NonNegativeFloat("spot")
    rate = NonNegativeFloat("rate")
    volatility = NonNegativeFloat("volatility")
    delta_t = NonNegativeFloat("delta_t")
    steps = PositiveInt("steps")

    def __init__(
        self,
        spot: float,
        rate: float,
        volatility: float,
        jump_params: JumpParameters,
        maturity: float,
        steps: int,
    ) -> None:
        if maturity <= 0:
            raise PricingError("Maturity must be positive")
        self.spot = spot
        self.rate = rate
        self.volatility = volatility
        self.jump_params = jump_params
        self.steps = steps
        self.delta_t = maturity / steps
        lambda_intensity = jump_params.intensity
        self.drift_correction = lambda_intensity * (math.exp(jump_params.mean_jump + 0.5 * jump_params.jump_vol**2) - 1)

    def simulate_terminal_price(self) -> float:
        price = self.spot
        for _ in range(self.steps):
            z = random.gauss(0, 1)
            jump_count = np.random.poisson(self.jump_params.intensity * self.delta_t)

            jump_term = 0.0
            if jump_count > 0:
                jump_term = np.random.normal(
                    loc=self.jump_params.mean_jump,
                    scale=self.jump_params.jump_vol,
                    size=jump_count
                ).sum()

            drift = (self.rate - self.drift_correction - 0.5 * self.volatility**2) * self.delta_t
            diffusion = self.volatility * math.sqrt(self.delta_t) * z
            price *= math.exp(drift + diffusion + jump_term)
        return price

    def terminal_price_stream(self, paths: int) -> Iterator[float]:
        for _ in range(paths):
            yield self.simulate_terminal_price()

    def payoff_stream(self, paths: int, strike: float) -> Iterator[float]:
        for terminal in self.terminal_price_stream(paths):
            yield max(terminal - strike, 0.0)

    def price_paths(self, paths: int, strike: float) -> float:
        total = 0.0
        count = 0
        for payoff in self.payoff_stream(paths, strike):
            total += payoff
            count += 1
        return math.exp(-self.rate * self.steps * self.delta_t) * total / max(count, 1)

    def plot_paths(self, paths: int) -> None:
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:  
            raise PricingError("matplotlib is required for plotting") from exc
        all_paths: list[list[float]] = []
        for _ in range(paths):
            price = self.spot
            path = [price]
            for _ in range(self.steps):
                z = random.gauss(0, 1)
                jump_count = 1 if random.random() < self.jump_params.intensity * self.delta_t else 0
                jump_amplitude = (
                    math.exp(self.jump_params.mean_jump + self.jump_params.jump_vol * random.gauss(0, 1)) - 1
                    if jump_count
                    else 0.0
                )
                drift = (self.rate - self.drift_correction - 0.5 * self.volatility**2) * self.delta_t
                diffusion = self.volatility * math.sqrt(self.delta_t) * z
                price *= math.exp(drift + diffusion) * (1 + jump_amplitude * jump_count)
                path.append(price)
            all_paths.append(path)
        for path in all_paths:
            plt.plot(path, alpha=0.6)
        plt.title("Merton Jump Diffusion Paths")
        plt.xlabel("Step")
        plt.ylabel("Price")
        plt.tight_layout()
        plt.show()
