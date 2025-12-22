"""
Context managers for pricing sessions and data I/O.

Demonstrates:
- Class-based context manager with __enter__ and __exit__
- @contextmanager decorator for functional approach
- Resource management (database connections, files)
- Proper cleanup and error handling
"""

from typing import Optional, Any, Generator
from contextlib import contextmanager
import sqlite3
from datetime import datetime
from pathlib import Path

from utils import logger, DataIOException


class PricingSession:
    """
    Class-based context manager for pricing sessions.

    Manages a pricing session with logging, timing, and cleanup.
    Implements __enter__ and __exit__ for use with 'with' statement.

    Example:
        with PricingSession("Adam Jones", "NIKKEI225") as session:
            price = option.price()
            session.log_result(price)
    """

    def __init__(
        self, trader_name: str, instrument: str, log_file: str = "pricing_session.log"
    ):
        """
        Initialize pricing session.

        Args:
            trader_name: Name of trader
            instrument: Instrument being priced
            log_file: Log file path
        """
        self.trader_name = trader_name
        self.instrument = instrument
        self.log_file = log_file
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.results: list = []
        self.errors: list = []

        logger.info(f"PricingSession initialized for {trader_name} on {instrument}")

    def __enter__(self) -> "PricingSession":
        """
        Enter context: start timing and log session start.

        Returns:
            Self for use in 'with' statement
        """
        self.start_time = datetime.now()

        logger.info(f"=== Pricing Session Started ===")
        logger.info(f"Trader: {self.trader_name}")
        logger.info(f"Instrument: {self.instrument}")
        logger.info(f"Start time: {self.start_time}")

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """
        Exit context: log results and cleanup.

        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False to propagate exceptions, True to suppress
        """
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        logger.info(f"=== Pricing Session Ended ===")
        logger.info(f"End time: {self.end_time}")
        logger.info(f"Duration: {duration:.4f} seconds")
        logger.info(f"Results logged: {len(self.results)}")

        if exc_type is not None:
            # An exception occurred
            error_msg = f"{exc_type.__name__}: {exc_val}"
            logger.error(f"Session ended with error: {error_msg}")
            self.errors.append(error_msg)

            # Write error to log file
            self._write_to_log(f"ERROR: {error_msg}")

            # Return False to propagate the exception
            return False

        # Success
        logger.info("Session completed successfully")
        self._write_summary()

        return False  # Don't suppress exceptions

    def log_result(self, description: str, value: Any) -> None:
        """
        Log a pricing result.

        Args:
            description: Description of the result
            value: The value to log
        """
        timestamp = datetime.now()
        result = {"timestamp": timestamp, "description": description, "value": value}
        self.results.append(result)

        logger.info(f"Result logged: {description} = {value}")
        self._write_to_log(f"{timestamp} | {description}: {value}")

    def _write_to_log(self, message: str) -> None:
        """Write message to log file."""
        try:
            with open(self.log_file, "a") as f:
                f.write(f"{message}\n")
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")

    def _write_summary(self) -> None:
        """Write session summary to log file."""
        self._write_to_log("\n" + "=" * 70)
        self._write_to_log(f"Pricing Session Summary")
        self._write_to_log(f"Trader: {self.trader_name}")
        self._write_to_log(f"Instrument: {self.instrument}")
        self._write_to_log(
            f"Duration: {(self.end_time - self.start_time).total_seconds():.4f}s"
        )
        self._write_to_log(f"Results: {len(self.results)}")
        self._write_to_log("=" * 70 + "\n")


class DatabaseConnection:
    """
    Class-based context manager for database connections.

    Manages SQLite database connections with automatic commit/rollback.

    Example:
        with DatabaseConnection("trades.db") as conn:
            conn.execute("INSERT INTO trades ...")
    """

    def __init__(self, db_path: str):
        """
        Initialize database connection context.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

        logger.debug(f"DatabaseConnection initialized: {db_path}")

    def __enter__(self) -> sqlite3.Connection:
        """
        Open database connection.

        Returns:
            SQLite connection object
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Database connection opened: {self.db_path}")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to open database: {e}")
            raise DataIOException(f"Failed to open database: {e}")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """
        Close database connection with commit or rollback.

        Commits if no exception, rolls back if exception occurred.
        """
        if self.conn:
            try:
                if exc_type is None:
                    # Success - commit changes
                    self.conn.commit()
                    logger.info("Database changes committed")
                else:
                    # Error - rollback changes
                    self.conn.rollback()
                    logger.warning(
                        f"Database changes rolled back due to: {exc_type.__name__}"
                    )
            finally:
                self.conn.close()
                logger.info("Database connection closed")

        return False  # Don't suppress exceptions


# ==============================================================================
# Function-based context managers using @contextmanager
# ==============================================================================


@contextmanager
def pricing_session_context(
    trader_name: str, instrument: str
) -> Generator[dict, None, None]:
    """
    Function-based context manager for pricing sessions.

    Demonstrates @contextmanager decorator as alternative to class-based approach.
    More flexible and concise for simple cases.

    Args:
        trader_name: Name of trader
        instrument: Instrument being priced

    Yields:
        Dictionary to store session data

    Example:
        with pricing_session_context("Adam Jones", "NIKKEI225") as session:
            session['price'] = 123.45
            session['method'] = 'black_scholes'
    """
    # Setup (before yield)
    start_time = datetime.now()
    session_data = {
        "trader": trader_name,
        "instrument": instrument,
        "start_time": start_time,
        "results": [],
    }

    logger.info(
        f"Pricing session started (contextmanager): {trader_name} on {instrument}"
    )

    try:
        # Yield control to the with block
        yield session_data

        # Teardown on success (after yield, no exception)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"Pricing session completed successfully in {duration:.4f}s")
        logger.info(f"Results: {session_data.get('results', [])}")

    except Exception as e:
        # Teardown on error
        logger.error(f"Pricing session failed: {e}")
        raise

    finally:
        # Always executed (cleanup)
        logger.info("Pricing session context closed")


@contextmanager
def temporary_database(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Function-based context manager for temporary database operations.

    Alternative to DatabaseConnection class using @contextmanager decorator.

    Args:
        db_path: Path to database file

    Yields:
        SQLite connection object

    Example:
        with temporary_database("temp.db") as conn:
            conn.execute("CREATE TABLE ...")
    """
    conn = None

    try:
        # Setup
        conn = sqlite3.connect(db_path)
        logger.debug(f"Temporary database connection opened: {db_path}")

        yield conn

        # Teardown on success
        conn.commit()
        logger.debug("Temporary database changes committed")

    except Exception as e:
        # Teardown on error
        if conn:
            conn.rollback()
            logger.warning(f"Temporary database rolled back: {e}")
        raise

    finally:
        # Always cleanup
        if conn:
            conn.close()
            logger.debug("Temporary database connection closed")


@contextmanager
def file_writer(file_path: str, mode: str = "w") -> Generator[Any, None, None]:
    """
    Simple file writer context manager.

    Args:
        file_path: Path to file
        mode: File open mode

    Yields:
        File object
    """
    f = None
    try:
        f = open(file_path, mode)
        logger.debug(f"File opened: {file_path} (mode={mode})")
        yield f
    finally:
        if f:
            f.close()
            logger.debug(f"File closed: {file_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("Context Managers Module")
    print("=" * 70)

    # Test class-based context manager
    print("\n1. Testing PricingSession (class-based):")
    with PricingSession("Adam Jones", "NIKKEI225", "test_session.log") as session:
        session.log_result("Price", 123.45)
        session.log_result("Delta", 0.65)
        session.log_result("Method", "Black-Scholes")

    print("   Session completed!")

    # Test function-based context manager
    print("\n2. Testing pricing_session_context (@contextmanager):")
    with pricing_session_context("Adam Jones", "TOPIX") as session:
        session["price"] = 456.78
        session["results"].append({"greek": "delta", "value": 0.52})

    print("   Context completed!")

    # Test database context manager
    print("\n3. Testing DatabaseConnection:")
    test_db = "test_context.db"

    with DatabaseConnection(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_trades (
                id INTEGER PRIMARY KEY,
                price REAL,
                timestamp TEXT
            )
        """
        )
        cursor.execute(
            "INSERT INTO test_trades (price, timestamp) VALUES (?, ?)",
            (100.50, datetime.now().isoformat()),
        )

    print("   Database operations completed!")

    # Verify database
    with DatabaseConnection(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_trades")
        count = cursor.fetchone()[0]
        print(f"   Verified: {count} record(s) in database")

    # Cleanup
    Path(test_db).unlink(missing_ok=True)
    Path("test_session.log").unlink(missing_ok=True)

    print("\n" + "=" * 70)
