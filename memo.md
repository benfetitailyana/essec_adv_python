# Implementation Memo (Non-Technical)

Hi, here is how the prototype was built and what could be improved.

## What the tool does

- Reads 10 sample trades from a small CSV, builds equity jump call options, and prices them with two methods: a textbook Black–Scholes model and a Monte Carlo jump-diffusion model.
- Logs who priced what, how long it took, and the resulting price/Delta into a CSV output and a log file.
- Provides a light plotting helper for jump paths (for intuition, not production).

## Key design choices

- **Modular building blocks:** A base option class plus a strategy registry means the desk can add new pricing formulas without touching the main script. The jump model is composed into strategies to keep models swappable.
- **Safety rails:** Descriptors and properties reject bad inputs (negative volatility, negative rates). Decorators capture runtime and errors, writing them to a log file for auditability.
- **Reusability:** A factory builds instruments from dictionaries, keeping the code DRY if we ingest JSON/DB rows later. A custom TradeBlotter container lets us sum notionals and filter trades cleanly.
- **Extensibility:** Both class-based and `@contextmanager` context managers are included to show how we would manage pricing sessions or file/DB handles consistently.

## Limitations and next steps

- Pricing models are intentionally simple; production would need calibrated parameters, variance reduction, and greeks aligned with the chosen model.
- Data IO targets CSV for clarity; adding SQLite/Parquet would be straightforward with the same schemas.
- Logging is minimal; structured JSON logs and correlation IDs would help in a busier desk.
- Static analysis hooks (MyPy, linting) are documented but not wired into CI here; that would be the next automation step.

## How to use it

1. Run `python main.py` to price the sample trades; results land in `output/priced_trades.csv` and `logs/app.log`.
2. Change parameters via CLI flags (`--spot`, `--vol`, `--strategies black_scholes jump_mc`).
3. Use the plotting snippet in the README to visualize jump paths.

Thanks,
Your quant dev
