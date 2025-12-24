# Jump Option Pricing Demo

Lightweight Python project modelling a Merton jump diffusion call pricer with clear OOP patterns, strategies, logging, and data IO for a junior quant assignment. Designed to stay readable for beginners while showcasing SOLID, DRY, ABC/Protocol, descriptors, mixins, decorators, factory/strategy patterns, context managers, and generators.

## Quickstart

- Requirements: Python 3.11+, `matplotlib` only if you want path plots.
- Run demo pricing (reads 10 sample trades and writes priced CSV):
  - `python main.py --trades sample_data/trades.csv --output output/priced_trades.csv --strategies black_scholes jump_mc`
  - Adjust `--spot`, `--rate`, `--vol`, `--dividend` as needed.
- Plot a few jump paths (optional): - `python - <<'PY'
from merton import JumpParameters, MertonJumpModel
model = MertonJumpModel(spot=100, rate=0.05, volatility=0.2, jump_params=JumpParameters(intensity=0.75, mean_jump=-0.6, jump_vol=0.25), maturity=1.0, steps=20)
model.plot_paths(paths=5)
PY`
- Run tests: `pytest`.
- Suggested static check: `mypy --strict .` (sample project is fully type hinted).

## Files to Explore

- Core interfaces and mixins: [interfaces.py](interfaces.py)
- Strategies (GoF Strategy) and registry: [strategies.py](strategies.py)
- Concrete option + pricing entrypoints: [options.py](options.py), [factory.py](factory.py)
- Jump diffusion model and generator: [merton.py](merton.py)
- Decorators, context managers, logging setup: [decorators.py](decorators.py), [context_managers.py](context_managers.py), [logging_config.py](logging_config.py)
- Trader workflow and container (GoF Factory + custom MutableSequence): [trading.py](trading.py), [data_io.py](data_io.py)
- Demo runner: [main.py](main.py)
- Tests: [tests](tests)
- Sample data: [sample_data/trades.csv](sample_data/trades.csv)
- Reflection memo: [memo.md](memo.md)

## Design Highlights

- **Strategy pattern:** select `black_scholes` or `jump_mc` at runtime via `--strategies` flag using `StrategyRegistry`.
- **Factory pattern:** `OptionFactory` builds instruments from config or `atm_equity` helper; easy to extend registry.
- **ABC + Protocol:** `BaseOption` (ABC) plus `PricingProtocol` for structural typing; `GreeksMixin` exposes Greeks.
- **Descriptors + properties:** `NonNegativeFloat`/`PositiveInt` enforce sane inputs on option/model fields; greeks exposed as properties.
- **Composition vs inheritance:** `EquityJumpCall` inherits shared option behavior; `MertonJumpModel` is composed inside strategies to keep pricing model pluggable.
- **Observability:** `log_call` + `time_it` decorators, `PricingSession` context manager, logging to `logs/app.log` and stdout.
- **Generators:** `MertonJumpModel.payoff_stream` lazily yields terminal payoffs to keep memory low.
- **Data IO:** Read trades from CSV, price them, and write enriched CSV; easily switch to JSON/SQLite.
- **Testing:** pytest covers validation, pricing call behavior, generator exhaustion, blotter utilities, logging side effects.

## Using and Extending

- Add more pricing strategies by registering callables on `StrategyRegistry.register("name", func)`.
- Add new instruments by placing classes in the factory registry.
- Validators are centralized through descriptors; tweak once, benefit across models.
- Switch data sources by replacing `read_trades_from_csv` with another loader keeping the `Order` shape.

## MyPy

- Suggested command: `mypy --strict .`
- If mypy is installed, the codebase should pass; adjust paths or config as needed.
