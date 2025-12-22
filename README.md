# Bank XYZ Option Pricing Platform

**Advanced Python Project - Merton Jump Diffusion Option Pricing**

## Project Overview

This is a comprehensive option pricing platform developed for Bank XYZ's quantitative trading desk. The platform implements Merton Jump Diffusion models for pricing equity options with jump risk, featuring multiple pricing strategies, Greek calculations, and complete data I/O capabilities.

## Key Features

### 1. Architecture & Design Patterns

- **Abstract Base Classes (ABC)**: `PricingInterface`, `GreeksInterface` with abstract methods
- **Protocol (Structural Typing)**: `PricingProtocol` for duck-typing compatibility
- **Strategy Pattern**: Multiple pricing methods selectable at runtime
- **Factory Pattern**: Centralized option creation from configs/JSON
- **Mixin Pattern**: `GreeksMixin` for modular Greek calculations
- **SOLID Principles**: Demonstrated throughout the codebase

### 2. Core Components

#### Pricing Strategies (13+ methods)

- Black-Scholes family (standard, with dividends, Black's model)
- Binomial methods (CRR, Jarrow-Rudd)
- Trinomial trees
- Finite Difference (Explicit, Implicit, Crank-Nicolson)
- Monte Carlo (standard, Quasi-MC, Jump Diffusion, LSMC)

#### Greeks Calculation

- Delta, Gamma, Vega, Theta, Rho
- Multiple calculation methods: Analytical, Bump-and-Revalue, Tree-based, FD-Grid

#### Jump Diffusion Simulation

- Merton Jump Diffusion model with Poisson jumps
- Euler discretization implementation
- Generator pattern for memory-efficient simulations
- Path visualization with Matplotlib

### 3. Object-Oriented Features

#### Dataclasses

- `MarketData`, `OptionParameters`, `JumpDiffusionParams`
- Frozen dataclasses for immutability
- Auto-generated `__repr__`, `__eq__`, `__hash__`

#### Properties & Descriptors

- `@property` with getters, setters, deleters
- Custom descriptors: `PositiveFloat`, `NonNegativeFloat`, `BoundedFloat`
- Strict validation of all inputs

#### Dunder Methods

- `__call__`: Make options callable to get price
- `__repr__`/`__str__`: Rich string representations
- `__len__`: Number of time steps in model
- `__iter__`: Iterate over simulated paths
- `__getitem__`, `__setitem__`, `__delitem__`: Container protocol

#### Custom Container

- `TradeBlotter` inheriting from `collections.abc.MutableSequence`
- Utility methods: `sum_notional()`, `filter_by_strike()`, `unique_underliers()`

### 4. Advanced Python Features

#### Decorators

- `@time_it`: Measure execution time
- `@log_call`: Log function calls with @wraps
- Stacked decorators with metadata preservation

#### Context Managers

- Class-based: `PricingSession`, `DatabaseConnection`
- Function-based: `@contextmanager` decorators
- Proper resource management and cleanup

#### Data I/O

- Read/write: Excel (`.xlsx`), CSV (`.csv`), JSON (`.json`), SQLite (`.db`)
- Auto-format detection
- Transaction management for databases

### 5. Trader Workflow

#### Adam Jones Example

- Trader: Adam Jones (ID: AJ001)
- Desk: JapanEQExotics
- 100 ATM NIKKEI 225 call options (3M maturity)
- Complete order logging with timestamps

### 6. Observability & Logging

- Structured logging with Python `logging` module
- Timestamp tracking for all operations
- Error logging with full stack traces
- Pricing session tracking

## Project Structure

```
essec_adv_python/
├── main.py                    # Main execution file ⭐
├── utils.py                   # Utilities, decorators, descriptors
├── interfaces.py              # ABC and Protocol interfaces
├── models.py                  # Dataclass models
├── pricing_strategies.py      # Strategy pattern for pricing
├── greeks_mixin.py           # Mixin for Greek calculations
├── options.py                 # Base and concrete option classes
├── jump_diffusion.py         # Merton jump diffusion model
├── trade_blotter.py          # Custom container (MutableSequence)
├── context_managers.py       # Context managers for resources
├── data_io.py                # Data input/output functions
├── factory.py                # Factory pattern for object creation
├── sample_trades.csv         # Sample trade data (10 trades)
├── test_option_platform.py   # Unit tests
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher

### Install Dependencies

```bash
# Core dependencies (required)
pip install numpy>=1.24.0

# Optional but recommended for full functionality
pip install pandas>=2.0.0 openpyxl>=3.1.0 matplotlib>=3.7.0

# Or install all at once
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the main demonstration:

```bash
python main.py
```

This will:

1. Load 10 sample trades from CSV
2. Create option instances using Factory pattern
3. Price options with multiple methods
4. Calculate Greeks
5. Generate jump diffusion path plots
6. Demonstrate TradeBlotter operations
7. Write results to CSV, JSON, and SQLite
8. Display summary statistics

### Using the Platform

#### Creating Options

```python
from factory import OptionFactory

# Method 1: Direct creation
option = OptionFactory.create_equity_jump_call(
    spot=28000.0,
    strike=28000.0,
    maturity=0.25,
    risk_free_rate=0.05,
    volatility=0.20,
    underlying_ticker="NIKKEI225"
)

# Method 2: From dictionary
config = {
    "spot": 28000.0,
    "strike": 28000.0,
    "maturity": 0.25,
    "volatility": 0.20
}
option = OptionFactory.from_dict(config)

# Method 3: Default NIKKEI option
option = OptionFactory.create_default_nikkei_call()
```

#### Pricing Options

```python
# Single method
price = option.price("black_scholes")

# Multiple methods for comparison
results = option.price_with_multiple_methods([
    "black_scholes",
    "monte_carlo",
    "jump_diffusion_mc"
])
```

#### Calculating Greeks

```python
# All Greeks at once
greeks = option.calculate_greeks("analytical")

# Individual Greeks
delta = option.delta
gamma = option.gamma
vega = option.vega
```

#### Using Context Managers

```python
from context_managers import PricingSession

with PricingSession("Adam Jones", "NIKKEI225") as session:
    price = option.price()
    session.log_result("Price", price)
    session.log_result("Method", "jump_diffusion_mc")
```

#### Trade Blotter Operations

```python
from trade_blotter import TradeBlotter, Trade

blotter = TradeBlotter(name="My Trades")
blotter.append(trade)

# Container operations
total = blotter.sum_notional()
nikkei_trades = blotter.filter_by_underlying("NIKKEI225")
underliers = blotter.unique_underliers()
```

## Testing

Run the test suite:

```bash
# Run all tests
python test_option_platform.py

# Or with pytest
pytest test_option_platform.py -v

# With coverage
pytest test_option_platform.py --cov=. --cov-report=html
```

Tests cover:

- Parameter validation (descriptors/properties)
- Pricing calculations
- Generator exhaustion
- Logging functionality
- Container operations
- Factory methods

## Type Checking

Run MyPy for static type analysis:

```bash
mypy main.py --ignore-missing-imports
mypy options.py interfaces.py models.py --strict
```

## Design Decisions

### Inheritance vs Composition

#### Inheritance Used For:

- `BaseOption` → `EquityJumpCallOption`: Natural "is-a" relationship
- `PricingInterface` (ABC): Enforcing contract for all options
- `MutableSequence` → `TradeBlotter`: Proper container behavior

#### Composition Used For:

- `JumpProcess` inside `MertonJumpModel`: Jump logic is a component, not a type
- `GreeksMixin`: Modular functionality added via mixin, not deep inheritance
- Strategy objects inside option classes: Algorithms are pluggable components

**Rationale**: Composition provides flexibility and avoids deep inheritance hierarchies. We use inheritance only when there's a clear "is-a" relationship and behavioral contract.

### SOLID Principles Demonstrated

1. **Single Responsibility**: Each class has one reason to change

   - `JumpProcess`: Only handles jump generation
   - `OptionFactory`: Only handles option creation
   - `DataIO`: Only handles data input/output

2. **Open/Closed**: Open for extension, closed for modification

   - New pricing strategies can be added without modifying existing code
   - New option types extend `BaseOption`

3. **Liskov Substitution**: Subclasses are substitutable for base classes

   - Any `PricingInterface` implementation can be used interchangeably
   - All strategies implement same interface

4. **Interface Segregation**: Many specific interfaces over one general

   - Separate interfaces for pricing vs Greeks
   - Protocol for duck typing without inheritance

5. **Dependency Inversion**: Depend on abstractions, not concretions
   - Options depend on `PricingStrategyInterface`, not concrete strategies
   - Factory returns interface types

## Generated Output Files

After running `main.py`:

- `pricing_results.csv`: Pricing results in CSV format
- `pricing_results.json`: Pricing results in JSON format
- `pricing_results.db`: SQLite database with results
- `jump_diffusion_paths.png`: Visualization of simulated paths
- `option_pricing.log`: Complete log of all operations

## Key Parameters (Sample)

### NIKKEI 225 Options

- Spot: 28,000
- Strike: 28,000 (ATM)
- Maturity: 3 months (0.25 years)
- Volatility: 20%
- Risk-free rate: 5%

### Jump Parameters

- Jump intensity (λ): 0.75
- Jump mean (μ_j): -0.6
- Jump std (δ): 0.2

## Author

Bank XYZ Quantitative Development Team
December 2025

## License

Proprietary - Bank XYZ Internal Use Only
