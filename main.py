"""
Main execution file for Option Pricing Platform.

This file demonstrates the complete workflow:
1. Load sample trades from CSV
2. Create options using Factory pattern
3. Price options with multiple methods
4. Calculate Greeks
5. Log all operations
6. Write results to output file
7. Plot price paths

Run this file to see the complete system in action.

Author: Bank XYZ Quantitative Development Team
Date: December 2025
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import math

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Core imports
from models import (
    MarketData,
    OptionParameters,
    JumpDiffusionParams,
    TraderInfo,
    OrderInfo,
    PricingResult,
)
from interfaces import OptionType, AssetClass
from factory import OptionFactory, TraderFactory
from options import EquityJumpCallOption
from trade_blotter import TradeBlotter, Trade
from context_managers import PricingSession, DatabaseConnection
from data_io import (
    read_trades_from_csv,
    write_results_to_csv,
    write_results_to_json,
    initialize_database,
    write_results_to_sqlite,
)
from utils import logger, time_it, log_call, format_timestamp

# Try importing matplotlib for plotting
try:
    import matplotlib.pyplot as plt
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Plotting will be skipped.")
    print("Install with: pip install matplotlib")


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subheader(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


@time_it
@log_call
def load_sample_trades(file_path: str = "sample_trades.csv") -> List[Dict[str, Any]]:
    """
    Load sample trades from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        List of trade dictionaries
    """
    logger.info(f"Loading sample trades from {file_path}")

    if not Path(file_path).exists():
        logger.warning(f"Sample file not found: {file_path}")
        logger.info("Creating default trades...")
        return create_default_trades()

    trades = read_trades_from_csv(file_path)
    logger.info(f"Loaded {len(trades)} trades from CSV")

    return trades


def create_default_trades() -> List[Dict[str, Any]]:
    """Create default trades if CSV not found."""
    return [
        {
            "trader_id": "AJ001",
            "trader_name": "Adam Jones",
            "desk": "JapanEQExotics",
            "order_id": f"ORD{i:03d}",
            "underlying": "NIKKEI225" if i % 2 == 0 else "TOPIX",
            "strike": 28000.0 if i % 2 == 0 else 2000.0,
            "maturity": 0.25,
            "volatility": 0.20,
            "quantity": 100,
            "option_type": "call",
            "spot": 28000.0 if i % 2 == 0 else 2000.0,
            "risk_free_rate": 0.05,
            "jump_intensity": 0.75,
            "jump_mean": -0.6,
            "jump_std": 0.2,
        }
        for i in range(1, 11)
    ]


@time_it
def create_options_from_trades(
    trades: List[Dict[str, Any]],
) -> List[EquityJumpCallOption]:
    """
    Create option instances from trade data using Factory pattern.

    Args:
        trades: List of trade dictionaries

    Returns:
        List of EquityJumpCallOption instances
    """
    logger.info(f"Creating {len(trades)} options using Factory pattern")

    options = []

    for trade in trades:
        try:
            # Convert string values to appropriate types
            option = OptionFactory.create_equity_jump_call(
                spot=float(trade["spot"]),
                strike=float(trade["strike"]),
                maturity=float(trade["maturity"]),
                risk_free_rate=float(trade.get("risk_free_rate", 0.05)),
                volatility=float(trade["volatility"]),
                jump_intensity=float(trade.get("jump_intensity", 0.75)),
                jump_mean=float(trade.get("jump_mean", -0.6)),
                jump_std=float(trade.get("jump_std", 0.2)),
                underlying_ticker=trade["underlying"],
            )

            # Attach trade metadata
            option._trade_data = trade
            options.append(option)

        except Exception as e:
            logger.error(
                f"Failed to create option for trade {trade.get('order_id')}: {e}"
            )

    logger.info(f"Successfully created {len(options)} options")
    return options


@time_it
def price_options_with_multiple_methods(
    options: List[EquityJumpCallOption], methods: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Price all options using multiple methods for comparison.

    Args:
        options: List of options to price
        methods: List of pricing methods to use

    Returns:
        List of pricing result dictionaries
    """
    if methods is None:
        methods = ["black_scholes", "monte_carlo", "jump_diffusion_mc"]

    logger.info(f"Pricing {len(options)} options with methods: {methods}")

    all_results = []

    for i, option in enumerate(options, 1):
        print(
            f"\nPricing option {i}/{len(options)}: {option.underlying_ticker} "
            f"@ {option.strike:.0f} ({option.time_to_maturity:.2f}y)"
        )

        for method in methods:
            try:
                start_time = time.time()
                price = option.price(method)
                elapsed_time = time.time() - start_time

                # Calculate Greeks
                greeks = option.calculate_greeks("analytical")

                # Compile result
                result = {
                    "order_id": option._trade_data.get("order_id", "UNKNOWN"),
                    "trader_id": option._trade_data.get("trader_id", "UNKNOWN"),
                    "trader_name": option._trade_data.get("trader_name", "UNKNOWN"),
                    "underlying": option.underlying_ticker,
                    "strike": option.strike,
                    "maturity": option.time_to_maturity,
                    "spot": option.spot,
                    "volatility": option.volatility,
                    "method": method,
                    "price": price,
                    "delta": greeks.get("delta"),
                    "gamma": greeks.get("gamma"),
                    "vega": greeks.get("vega"),
                    "theta": greeks.get("theta"),
                    "rho": greeks.get("rho"),
                    "computation_time": elapsed_time,
                    "timestamp": datetime.now().isoformat(),
                }

                all_results.append(result)

                print(
                    f"  {method:20s}: Price = {price:10.4f}  "
                    f"Delta = {greeks['delta']:6.4f}  "
                    f"Time = {elapsed_time:.4f}s"
                )

            except Exception as e:
                logger.error(f"Pricing failed for method {method}: {e}")

    logger.info(f"Completed pricing: {len(all_results)} results generated")
    return all_results


def plot_jump_diffusion_paths(
    option: EquityJumpCallOption,
    num_paths: int = 50,
    output_file: str = "jump_diffusion_paths.png",
) -> None:
    """
    Plot sample paths from Merton jump diffusion model.

    Args:
        option: Option with jump diffusion model
        num_paths: Number of paths to plot
        output_file: Output file name
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib not available, skipping plot")
        return

    logger.info(f"Plotting {num_paths} jump diffusion paths")

    print_subheader(f"Generating {num_paths} Price Paths")

    # Generate paths
    paths = option.merton_model.simulate_paths(num_paths)
    time_steps = np.linspace(0, option.time_to_maturity, paths.shape[1])

    # Create plot
    plt.figure(figsize=(12, 7))

    # Plot paths with transparency
    for i in range(num_paths):
        plt.plot(time_steps, paths[i], alpha=0.3, linewidth=0.8)

    # Highlight first path
    plt.plot(time_steps, paths[0], "b-", linewidth=2, alpha=0.8, label="Sample Path")

    # Plot strike as horizontal line
    plt.axhline(
        y=option.strike,
        color="r",
        linestyle="--",
        linewidth=2,
        label=f"Strike = {option.strike:.0f}",
    )

    # Plot initial price
    plt.axhline(
        y=option.spot,
        color="g",
        linestyle=":",
        linewidth=1,
        alpha=0.5,
        label=f"Initial = {option.spot:.0f}",
    )

    plt.xlabel("Time (years)", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.title(
        f"Merton Jump Diffusion Paths - {option.underlying_ticker}\n"
        f"λ={option.jump_params.jump_intensity}, μ_j={option.jump_params.jump_mean}, "
        f"σ={option.volatility:.2%}",
        fontsize=14,
    )
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    logger.info(f"Plot saved to {output_file}")

    print(f"\nPlot saved to: {output_file}")

    # Show statistics
    terminal_prices = paths[:, -1]
    print(f"\nTerminal Price Statistics:")
    print(f"  Mean:   {np.mean(terminal_prices):10.2f}")
    print(f"  Median: {np.median(terminal_prices):10.2f}")
    print(f"  Std:    {np.std(terminal_prices):10.2f}")
    print(f"  Min:    {np.min(terminal_prices):10.2f}")
    print(f"  Max:    {np.max(terminal_prices):10.2f}")


def demonstrate_trade_blotter(
    trades_data: List[Dict[str, Any]], results: List[Dict[str, Any]]
) -> TradeBlotter:
    """
    Demonstrate TradeBlotter container functionality.

    Args:
        trades_data: Trade data dictionaries
        results: Pricing results

    Returns:
        Populated TradeBlotter
    """
    print_subheader("Trade Blotter Operations")

    # Create Adam Jones trader
    adam_jones = TraderFactory.create_adam_jones()

    # Create blotter
    blotter = TradeBlotter(name="Adam Jones - JapanEQExotics")

    # Create trades and add to blotter
    for trade_data in trades_data:
        # Find pricing result
        matching_result = next(
            (r for r in results if r["order_id"] == trade_data["order_id"]), None
        )

        if matching_result:
            order = OrderInfo(
                order_id=trade_data["order_id"],
                trader_info=adam_jones,
                quantity=int(trade_data["quantity"]),
                underlying=trade_data["underlying"],
                strike=float(trade_data["strike"]),
                maturity=float(trade_data["maturity"]),
                option_type=OptionType.CALL,
            )

            trade = Trade(order=order, fill_price=matching_result["price"])

            blotter.append(trade)

    # Demonstrate container operations
    print(f"\nBlotter: {blotter}")
    print(f"Total trades: {len(blotter)}")
    print(f"Total notional: ${blotter.sum_notional():,.2f}")
    print(f"Unique underliers: {blotter.unique_underliers()}")

    # Filter operations
    nikkei_trades = blotter.filter_by_underlying("NIKKEI225")
    print(f"NIKKEI225 trades: {len(nikkei_trades)}")

    # Summary
    summary = blotter.get_summary()
    print(f"\nBlotter Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    return blotter


def main():
    """
    Main execution function.

    Demonstrates complete workflow from data loading to result output.
    """
    print_header("Bank XYZ Option Pricing Platform")
    print(f"Execution Time: {format_timestamp()}")
    print(f"Trader: Adam Jones (ID: AJ001)")
    print(f"Desk: JapanEQExotics")

    # =========================================================================
    # Step 1: Load Sample Trades
    # =========================================================================
    print_header("Step 1: Load Sample Trades")

    trades_data = load_sample_trades("sample_trades.csv")
    print(f"\nLoaded {len(trades_data)} trades")
    print(
        f"Sample trade: {trades_data[0]['order_id']} - "
        f"{trades_data[0]['underlying']} @ {trades_data[0]['strike']}"
    )

    # =========================================================================
    # Step 2: Create Options Using Factory Pattern
    # =========================================================================
    print_header("Step 2: Create Options (Factory Pattern)")

    options = create_options_from_trades(trades_data)
    print(f"\nCreated {len(options)} option instances")
    print(f"Sample option: {options[0]}")

    # =========================================================================
    # Step 3: Price Options with Multiple Methods
    # =========================================================================
    print_header("Step 3: Price Options (Multiple Methods)")

    # Use PricingSession context manager
    with PricingSession("Adam Jones", "NIKKEI225 & TOPIX Options") as session:
        pricing_methods = ["black_scholes", "jump_diffusion_mc"]
        results = price_options_with_multiple_methods(options, pricing_methods)

        session.log_result("Total options priced", len(options))
        session.log_result("Total results", len(results))
        session.log_result("Methods used", ", ".join(pricing_methods))

    # =========================================================================
    # Step 4: Demonstrate Jump Diffusion Plotting
    # =========================================================================
    print_header("Step 4: Plot Jump Diffusion Paths")

    # Use first NIKKEI option for plotting
    nikkei_option = next(
        (opt for opt in options if opt.underlying_ticker == "NIKKEI225"), options[0]
    )

    plot_jump_diffusion_paths(nikkei_option, num_paths=100)

    # =========================================================================
    # Step 5: Trade Blotter Operations
    # =========================================================================
    print_header("Step 5: Trade Blotter (Custom Container)")

    blotter = demonstrate_trade_blotter(trades_data, results)

    # =========================================================================
    # Step 6: Write Results to Multiple Formats
    # =========================================================================
    print_header("Step 6: Write Results to Output Files")

    output_files = {
        "CSV": "pricing_results.csv",
        "JSON": "pricing_results.json",
        "SQLite": "pricing_results.db",
    }

    # Write to CSV
    print(f"\nWriting to CSV: {output_files['CSV']}")
    write_results_to_csv(results, output_files["CSV"])

    # Write to JSON
    print(f"Writing to JSON: {output_files['JSON']}")
    write_results_to_json(results, output_files["JSON"])

    # Write to SQLite
    print(f"Writing to SQLite: {output_files['SQLite']}")
    initialize_database(output_files["SQLite"])
    write_results_to_sqlite(results, output_files["SQLite"])

    print("\nAll results written successfully!")

    # =========================================================================
    # Step 7: Summary Statistics
    # =========================================================================
    print_header("Step 7: Summary Statistics")

    # Group results by method
    methods_summary = {}
    for result in results:
        method = result["method"]
        if method not in methods_summary:
            methods_summary[method] = {"prices": [], "computation_times": []}
        methods_summary[method]["prices"].append(result["price"])
        methods_summary[method]["computation_times"].append(result["computation_time"])

    print("\nPricing Method Comparison:")
    for method, data in methods_summary.items():
        avg_price = sum(data["prices"]) / len(data["prices"])
        avg_time = sum(data["computation_times"]) / len(data["computation_times"])
        print(f"\n  {method}:")
        print(f"    Avg Price:          ${avg_price:,.4f}")
        print(f"    Avg Computation:    {avg_time:.4f}s")
        print(f"    Total Calculations: {len(data['prices'])}")

    # =========================================================================
    # Completion
    # =========================================================================
    print_header("Execution Complete")

    print("\nGenerated Files:")
    for format_name, file_path in output_files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"  ✓ {format_name:10s}: {file_path} ({size:,} bytes)")

    if MATPLOTLIB_AVAILABLE and Path("jump_diffusion_paths.png").exists():
        print(f"  ✓ Plot:        jump_diffusion_paths.png")

    print(f"\nLog File: option_pricing.log")
    print(f"\nAll operations logged successfully!")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        logger.warning("Execution interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        logger.exception("Fatal error in main execution")
        raise
