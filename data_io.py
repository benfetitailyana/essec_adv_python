"""
Data I/O module for reading and writing trade data.

Supports multiple formats:
- Excel (.xlsx)
- CSV (.csv)
- JSON (.json)
- SQLite (.db)

Demonstrates:
- Multiple data format support
- Proper error handling
- Type hints
- Context managers for resource management
"""

from typing import List, Dict, Any, Optional
import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from models import OrderInfo, TraderInfo, PricingResult
from interfaces import OptionType, AssetClass
from context_managers import DatabaseConnection
from utils import logger, DataIOException


# ==============================================================================
# Excel Operations
# ==============================================================================


def read_trades_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Read trade data from Excel file.

    Args:
        file_path: Path to Excel file

    Returns:
        List of trade dictionaries

    Raises:
        DataIOException: If read fails
    """
    if not PANDAS_AVAILABLE:
        raise DataIOException(
            "pandas is required for Excel operations. Install with: pip install pandas openpyxl"
        )

    try:
        logger.info(f"Reading trades from Excel: {file_path}")
        df = pd.read_excel(file_path)

        trades = df.to_dict("records")
        logger.info(f"Successfully read {len(trades)} trades from Excel")

        return trades

    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        raise DataIOException(f"Failed to read Excel file '{file_path}': {e}")


def write_results_to_excel(results: List[Dict[str, Any]], file_path: str) -> None:
    """
    Write pricing results to Excel file.

    Args:
        results: List of result dictionaries
        file_path: Output Excel file path

    Raises:
        DataIOException: If write fails
    """
    if not PANDAS_AVAILABLE:
        raise DataIOException("pandas is required for Excel operations")

    try:
        logger.info(f"Writing {len(results)} results to Excel: {file_path}")

        df = pd.DataFrame(results)
        df.to_excel(file_path, index=False, engine="openpyxl")

        logger.info(f"Successfully wrote results to Excel")

    except Exception as e:
        logger.error(f"Failed to write Excel file: {e}")
        raise DataIOException(f"Failed to write Excel file '{file_path}': {e}")


# ==============================================================================
# CSV Operations
# ==============================================================================


def read_trades_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Read trade data from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        List of trade dictionaries
    """
    try:
        logger.info(f"Reading trades from CSV: {file_path}")

        trades = []
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append(dict(row))

        logger.info(f"Successfully read {len(trades)} trades from CSV")
        return trades

    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        raise DataIOException(f"Failed to read CSV file '{file_path}': {e}")


def write_results_to_csv(results: List[Dict[str, Any]], file_path: str) -> None:
    """
    Write pricing results to CSV file.

    Args:
        results: List of result dictionaries
        file_path: Output CSV file path
    """
    try:
        logger.info(f"Writing {len(results)} results to CSV: {file_path}")

        if not results:
            logger.warning("No results to write")
            return

        # Get all unique keys from results
        fieldnames = set()
        for result in results:
            fieldnames.update(result.keys())
        fieldnames = sorted(fieldnames)

        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        logger.info("Successfully wrote results to CSV")

    except Exception as e:
        logger.error(f"Failed to write CSV file: {e}")
        raise DataIOException(f"Failed to write CSV file '{file_path}': {e}")


# ==============================================================================
# JSON Operations
# ==============================================================================


def read_trades_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Read trade data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        List of trade dictionaries
    """
    try:
        logger.info(f"Reading trades from JSON: {file_path}")

        with open(file_path, "r") as f:
            trades = json.load(f)

        if not isinstance(trades, list):
            trades = [trades]

        logger.info(f"Successfully read {len(trades)} trades from JSON")
        return trades

    except Exception as e:
        logger.error(f"Failed to read JSON file: {e}")
        raise DataIOException(f"Failed to read JSON file '{file_path}': {e}")


def write_results_to_json(
    results: List[Dict[str, Any]], file_path: str, indent: int = 2
) -> None:
    """
    Write pricing results to JSON file.

    Args:
        results: List of result dictionaries
        file_path: Output JSON file path
        indent: JSON indentation (None for compact)
    """
    try:
        logger.info(f"Writing {len(results)} results to JSON: {file_path}")

        with open(file_path, "w") as f:
            json.dump(results, f, indent=indent, default=str)

        logger.info("Successfully wrote results to JSON")

    except Exception as e:
        logger.error(f"Failed to write JSON file: {e}")
        raise DataIOException(f"Failed to write JSON file '{file_path}': {e}")


# ==============================================================================
# SQLite Operations
# ==============================================================================


def initialize_database(db_path: str) -> None:
    """
    Initialize SQLite database with required tables.

    Args:
        db_path: Path to database file
    """
    logger.info(f"Initializing database: {db_path}")

    with DatabaseConnection(db_path) as conn:
        cursor = conn.cursor()

        # Create trades table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                trader_id TEXT NOT NULL,
                trader_name TEXT NOT NULL,
                desk TEXT NOT NULL,
                underlying TEXT NOT NULL,
                strike REAL NOT NULL,
                maturity REAL NOT NULL,
                option_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                fill_price REAL,
                timestamp TEXT NOT NULL
            )
        """
        )

        # Create pricing_results table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pricing_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                price REAL NOT NULL,
                method TEXT NOT NULL,
                delta REAL,
                gamma REAL,
                vega REAL,
                theta REAL,
                rho REAL,
                computation_time REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (trade_id) REFERENCES trades (trade_id)
            )
        """
        )

        logger.info("Database initialized successfully")


def read_trades_from_sqlite(db_path: str) -> List[Dict[str, Any]]:
    """
    Read trade data from SQLite database.

    Args:
        db_path: Path to database file

    Returns:
        List of trade dictionaries
    """
    try:
        logger.info(f"Reading trades from SQLite: {db_path}")

        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades")

            # Get column names
            columns = [description[0] for description in cursor.description]

            # Convert rows to dictionaries
            trades = []
            for row in cursor.fetchall():
                trade = dict(zip(columns, row))
                trades.append(trade)

        logger.info(f"Successfully read {len(trades)} trades from SQLite")
        return trades

    except Exception as e:
        logger.error(f"Failed to read from SQLite: {e}")
        raise DataIOException(f"Failed to read from SQLite '{db_path}': {e}")


def write_results_to_sqlite(results: List[Dict[str, Any]], db_path: str) -> None:
    """
    Write pricing results to SQLite database.

    Args:
        results: List of result dictionaries
        db_path: Path to database file
    """
    try:
        logger.info(f"Writing {len(results)} results to SQLite: {db_path}")

        # Ensure database is initialized
        initialize_database(db_path)

        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()

            for result in results:
                cursor.execute(
                    """
                    INSERT INTO pricing_results 
                    (trade_id, price, method, delta, gamma, vega, theta, rho, 
                     computation_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.get("trade_id", "UNKNOWN"),
                        result.get("price", 0.0),
                        result.get("method", "unknown"),
                        result.get("delta"),
                        result.get("gamma"),
                        result.get("vega"),
                        result.get("theta"),
                        result.get("rho"),
                        result.get("computation_time", 0.0),
                        result.get("timestamp", datetime.now().isoformat()),
                    ),
                )

        logger.info("Successfully wrote results to SQLite")

    except Exception as e:
        logger.error(f"Failed to write to SQLite: {e}")
        raise DataIOException(f"Failed to write to SQLite '{db_path}': {e}")


# ==============================================================================
# Generic I/O Functions
# ==============================================================================


def read_trades(file_path: str) -> List[Dict[str, Any]]:
    """
    Read trades from file, auto-detecting format.

    Args:
        file_path: Path to input file

    Returns:
        List of trade dictionaries
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".xlsx" or suffix == ".xls":
        return read_trades_from_excel(file_path)
    elif suffix == ".csv":
        return read_trades_from_csv(file_path)
    elif suffix == ".json":
        return read_trades_from_json(file_path)
    elif suffix == ".db" or suffix == ".sqlite":
        return read_trades_from_sqlite(file_path)
    else:
        raise DataIOException(f"Unsupported file format: {suffix}")


def write_results(results: List[Dict[str, Any]], file_path: str) -> None:
    """
    Write results to file, auto-detecting format.

    Args:
        results: List of result dictionaries
        file_path: Output file path
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".xlsx" or suffix == ".xls":
        write_results_to_excel(results, file_path)
    elif suffix == ".csv":
        write_results_to_csv(results, file_path)
    elif suffix == ".json":
        write_results_to_json(results, file_path)
    elif suffix == ".db" or suffix == ".sqlite":
        write_results_to_sqlite(results, file_path)
    else:
        raise DataIOException(f"Unsupported file format: {suffix}")


if __name__ == "__main__":
    print("=" * 70)
    print("Data I/O Module")
    print("=" * 70)

    # Sample data
    sample_results = [
        {
            "trade_id": "TRD001",
            "price": 123.45,
            "method": "black_scholes",
            "delta": 0.65,
            "gamma": 0.02,
            "computation_time": 0.001,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "trade_id": "TRD002",
            "price": 234.56,
            "method": "monte_carlo",
            "delta": 0.55,
            "gamma": 0.03,
            "computation_time": 0.150,
            "timestamp": datetime.now().isoformat(),
        },
    ]

    # Test JSON I/O
    print("\n1. Testing JSON I/O:")
    json_file = "test_results.json"
    write_results_to_json(sample_results, json_file)
    loaded = read_trades_from_json(json_file)
    print(f"   Wrote and read {len(loaded)} records")
    Path(json_file).unlink()

    # Test CSV I/O
    print("\n2. Testing CSV I/O:")
    csv_file = "test_results.csv"
    write_results_to_csv(sample_results, csv_file)
    loaded = read_trades_from_csv(csv_file)
    print(f"   Wrote and read {len(loaded)} records")
    Path(csv_file).unlink()

    # Test SQLite I/O
    print("\n3. Testing SQLite I/O:")
    db_file = "test_results.db"
    initialize_database(db_file)
    write_results_to_sqlite(sample_results, db_file)
    print(f"   Wrote {len(sample_results)} records to SQLite")
    Path(db_file).unlink()

    print("\n" + "=" * 70)
