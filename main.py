"""Simple driver script for the jump option pricing demo."""
from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import Iterable

from context_managers import PricingSession, csv_writer
from data_io import read_trades_from_csv
from decorators import log_call, time_it
from factory import OptionFactory
from interfaces import PricingResult
from logging_config import configure_logging
from strategies import StrategyRegistry
from trading import Trader, TradeBlotter


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Jump diffusion pricing demo")
	parser.add_argument("--trades", type=Path, default=Path("sample_data/trades.csv"), help="Input CSV of trades")
	parser.add_argument("--output", type=Path, default=Path("output/priced_trades.csv"), help="Where to write priced trades")
	parser.add_argument(
		"--strategies",
		nargs="+",
		default=["black_scholes", "jump_mc"],
		help="Strategies to run (black_scholes, jump_mc)",
	)
	parser.add_argument("--spot", type=float, default=100.0, help="Current spot price")
	parser.add_argument("--rate", type=float, default=0.05, help="Risk free rate")
	parser.add_argument("--vol", type=float, default=0.2, help="Volatility")
	parser.add_argument("--dividend", type=float, default=0.0, help="Dividend yield")
	return parser.parse_args()


@log_call
@time_it
def evaluate_order(strategy_key: str, config: dict) -> PricingResult:
	option = OptionFactory.create(config)
	strategy = StrategyRegistry.get(strategy_key)
	return strategy(option)


def price_orders(trades_path: Path, output_path: Path, strategies: Iterable[str], base_config: dict) -> None:
	trader = Trader(trader_id="T-001", name="Adam Jones", desk="JapanEQExotics")
	blotter = TradeBlotter(read_trades_from_csv(trades_path, trader))
	output_path.parent.mkdir(exist_ok=True)
	fieldnames = ["underlier", "strike", "maturity", "notional", "strategy", "price", "delta"]
	with PricingSession("demo-pricing"):
		with csv_writer(output_path, fieldnames=fieldnames) as writer:
			for order in blotter:
				for strategy_key in strategies:
					config = {
						"type": "equity_jump_call",
						"spot": base_config["spot"],
						"rate": base_config["rate"],
						"dividend": base_config["dividend"],
						"volatility": base_config["volatility"],
						"strike": order.strike,
						"maturity": order.maturity,
					}
					start = time.time()
					result = evaluate_order(strategy_key, config)
					elapsed = (time.time() - start) * 1000
					logging.info(
						"Trader %s priced %s with %s in %.2f ms price=%.4f",
						order.trader.name,
						order.underlier,
						strategy_key,
						elapsed,
						result.price,
					)
					writer.writerow(
						{
							"underlier": order.underlier,
							"strike": order.strike,
							"maturity": order.maturity,
							"notional": order.notional,
							"strategy": strategy_key,
							"price": f"{result.price:.4f}",
							"delta": f"{result.greeks.get('delta', 0.0):.4f}",
						}
					)


def main() -> None:
	args = parse_args()
	configure_logging()
	base_config = {"spot": args.spot, "rate": args.rate, "volatility": args.vol, "dividend": args.dividend}
	price_orders(args.trades, args.output, args.strategies, base_config)


if __name__ == "__main__":
	main()
