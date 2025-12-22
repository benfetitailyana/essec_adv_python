# Quick Start Guide

## Installation (30 seconds)

```bash
# 1. Navigate to project directory
cd /Users/lbessard/Documents/Code/essec_adv_python

# 2. Install dependencies
pip install numpy pandas matplotlib openpyxl

# Or install all at once
pip install -r requirements.txt
```

## Run the Demo (1 minute)

```bash
# Run the complete demonstration
python main.py
```

This will:

- ✅ Load 10 sample trades from CSV
- ✅ Price options with multiple methods
- ✅ Calculate Greeks (Delta, Gamma, Vega, Theta, Rho)
- ✅ Generate jump diffusion path visualization
- ✅ Create trade blotter with Adam Jones's trades
- ✅ Write results to CSV, JSON, and SQLite

## Expected Output Files

After running `main.py`, you'll see:

- `pricing_results.csv` - Results in CSV format
- `pricing_results.json` - Results in JSON format
- `pricing_results.db` - SQLite database with results
- `jump_diffusion_paths.png` - Visualization of price paths
- `option_pricing.log` - Complete operation log

## Run Tests (optional)

```bash
# Run unit tests
python test_option_platform.py

# Or with pytest (if installed)
pytest test_option_platform.py -v
```

## Quick Examples

### Price a Single Option

```python
from factory import OptionFactory

# Create NIKKEI 225 call option
option = OptionFactory.create_default_nikkei_call()

# Get price
price = option.price("jump_diffusion_mc")
print(f"Option price: {price:.2f}")

# Get Greeks
print(f"Delta: {option.delta:.4f}")
print(f"Gamma: {option.gamma:.4f}")
```

### Compare Multiple Pricing Methods

```python
# Price with multiple methods
results = option.price_with_multiple_methods([
    "black_scholes",
    "monte_carlo",
    "jump_diffusion_mc"
])

for method, result in results.items():
    print(f"{method}: {result.price:.2f}")
```

### Create Custom Option

```python
option = OptionFactory.create_equity_jump_call(
    spot=28000.0,           # Current price
    strike=29000.0,         # Strike price
    maturity=0.25,          # 3 months
    risk_free_rate=0.05,    # 5% rate
    volatility=0.20,        # 20% vol
    jump_intensity=0.75,    # Jump frequency
    jump_mean=-0.6,         # Jump size mean
    jump_std=0.2,           # Jump size std
    underlying_ticker="NIKKEI225"
)

price = option.price()
```

## Troubleshooting

### Import Error: No module named 'numpy'

```bash
pip install numpy
```

### Import Error: No module named 'pandas'

```bash
pip install pandas openpyxl
```

### Import Error: No module named 'matplotlib'

```bash
pip install matplotlib
```

### File Not Found: sample_trades.csv

The file should be in the project directory. If missing, `main.py` will create default trades automatically.

## Key Concepts

### Pricing Methods Available

- `black_scholes` - Classic Black-Scholes
- `black_scholes_merton` - With dividends
- `binomial_crr` - Cox-Ross-Rubinstein tree
- `monte_carlo` - Standard Monte Carlo
- `jump_diffusion_mc` - With Poisson jumps (recommended)
- Plus 8 more methods!

### Greeks Calculated

- **Delta** (Δ): Sensitivity to spot price
- **Gamma** (Γ): Convexity (rate of Delta change)
- **Vega** (ν): Sensitivity to volatility
- **Theta** (Θ): Time decay
- **Rho** (ρ): Sensitivity to interest rate

### Sample Parameters

- **NIKKEI 225**: Spot=28,000, Vol=20%
- **Jump Intensity**: λ=0.75 (jumps/year)
- **Jump Mean**: μ=-0.6 (negative jumps)
- **Jump Std**: δ=0.2

## Project Structure

```
├── main.py                 ⭐ Start here!
├── utils.py                Utilities & decorators
├── interfaces.py           ABC & Protocol definitions
├── models.py               Dataclass models
├── pricing_strategies.py   13+ pricing methods
├── greeks_mixin.py        Greek calculations
├── options.py             Option classes
├── jump_diffusion.py      Merton jump model
├── trade_blotter.py       Custom container
├── context_managers.py    Resource management
├── data_io.py            Data I/O functions
├── factory.py            Factory pattern
├── sample_trades.csv     Sample data
└── test_option_platform.py  Unit tests
```

## Next Steps

1. ✅ Run `python main.py` to see everything in action
2. 📖 Read `README.md` for detailed documentation
3. 📝 Review `DESIGN_MEMO.md` for design decisions
4. 🧪 Run tests with `python test_option_platform.py`
5. 💻 Modify `sample_trades.csv` with your own trades

## Getting Help

- **README.md**: Full documentation
- **DESIGN_MEMO.md**: Design rationale and challenges
- **Code comments**: Every function documented
- **Docstrings**: Type `help(OptionFactory)` in Python

## Common Use Cases

### Load Trades from Excel

```python
from data_io import read_trades_from_excel

trades = read_trades_from_excel("my_trades.xlsx")
```

### Write Results to Database

```python
from data_io import write_results_to_sqlite

write_results_to_sqlite(results, "results.db")
```

### Plot Price Paths

```python
import matplotlib.pyplot as plt

# Simulate paths
paths = option.merton_model.simulate_paths(num_paths=50)

# Plot
for path in paths:
    plt.plot(path, alpha=0.3)
plt.show()
```

---

**Ready to go!** Run `python main.py` now! 🚀
