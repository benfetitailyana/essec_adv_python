# Jump Option Pricing Demo

This project implements an equity call option pricer under a Merton jump-diffusion framework.
It was developed as part of a Python assignment and focuses on clean code structure,
readability, and extensibility rather than production-level performance.

The goal of the project is to demonstrate how common quantitative finance concepts
can be implemented using modern Python design patterns.

---

## Overview

The project prices equity call options using:
- a closed-form Black–Scholes model
- a Monte Carlo jump-diffusion model based on Merton’s framework

Pricing logic is separated from financial instruments and selected at runtime.
Trades are read from a CSV file, priced, logged, and written back to an output CSV.

---


### Requirements
- Python 3.11+
- numpy
- pytest (for running tests)
- mypy (optional, for static type checking)
- matplotlib (optional, for plotting jump paths)

####  Pricing example

python main.py \
  --trades sample_data/trades.csv \
  --output output/priced_trades.csv \
  --strategies black_scholes jump_mc

Market parameters can be modified from the command line:
python main.py --spot 100 --rate 0.05 --vol 0.2 --dividend 0.0


Monte Carlo and jump parameters can also be adjusted at runtime:

python main.py \
  --strategies jump_mc \
  --paths 5000 \
  --jump_lambda 1.2 \
  --jump_mu -0.6 \
  --jump_vol 0.3

#####  Project structure
[interfaces.py](interfaces.py)
Base option abstractions, pricing results, and shared mixins.

[strategies.py](strategies.py)
Pricing strategies (Black–Scholes and jump-diffusion Monte Carlo) and a registry
used to select strategies at runtime.

[options.py](options.py)
Concrete option implementation (EquityJumpCall).

[factory.py](factory.py)
Factory used to build option instances from configuration dictionaries.

[merton.py](merton.py)
Jump-diffusion model with Poisson jumps and Euler discretization.
Exposes generators for terminal prices and payoffs.

[trading.py](trading.py)
Domain objects (Trader, Order) and a custom TradeBlotter container.

[data_io.py](data_io.py)
CSV trade loader.

[decorators.py](decorators.py) , [context_managers.py](context_managers.py), [logging_config.py](logging_config.py)
Logging, decorators, and context managers used for observability.

[main.py](main.py)
Application entry point.

[tests](tests/)
Pytest test suite.

###### Design choices
Financial instruments inherit from a common abstract base class to reuse
validated state and shared behavior.

Pricing logic is implemented using the Strategy pattern and kept outside
instrument classes. Instruments delegate pricing to strategies selected at runtime.
The jump-diffusion strategy composes a separate jump model rather than embedding
numerical logic directly inside the option.

Input validation is centralized using descriptors and properties.
Domain-specific exceptions are used to report invalid configurations clearly.

Monte Carlo simulations use generators to avoid unnecessary memory usage.

####### Testing 
The project includes a pytest test suite covering:

input validation (descriptors and properties)

pricing call behavior

generator exhaustion

logging side effects

custom container utilities

factory helper methods

python -m pytest -q

####### Typing
The codebase is fully type-annotated and checked using MyPy.
A MyPy report is included to document static type-checking results (mypy_report.txt)
python -m mypy . > mypy_report.txt