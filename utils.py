"""
Utility module for Option Pricing Platform.

This module provides decorators, descriptors, custom exceptions, and validation
utilities used throughout the option pricing platform.

Key Components:
- Decorators: @time_it, @log_call for observability
- Descriptors: Type and value validation (NonNegativeFloat, PositiveFloat, etc.)
- Custom Exceptions: Domain-specific error handling
- Validation functions: Input validation helpers
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, Optional, Union
from datetime import datetime
import sys

# ==============================================================================
# Custom Exceptions
# ==============================================================================


class OptionPricingException(Exception):
    """Base exception for all option pricing errors."""

    pass


class NegativeValueException(OptionPricingException):
    """Raised when a value that must be non-negative is negative."""

    def __init__(self, param_name: str, value: float):
        self.param_name = param_name
        self.value = value
        super().__init__(f"Parameter '{param_name}' must be non-negative, got {value}")


class InvalidTypeException(OptionPricingException):
    """Raised when a parameter has an invalid type."""

    def __init__(self, param_name: str, expected_type: type, actual_type: type):
        self.param_name = param_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"Parameter '{param_name}' expected {expected_type.__name__}, "
            f"got {actual_type.__name__}"
        )


class InvalidRangeException(OptionPricingException):
    """Raised when a parameter is outside its valid range."""

    def __init__(
        self,
        param_name: str,
        value: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ):
        self.param_name = param_name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val

        if min_val is not None and max_val is not None:
            msg = f"Parameter '{param_name}' must be in range [{min_val}, {max_val}], got {value}"
        elif min_val is not None:
            msg = f"Parameter '{param_name}' must be >= {min_val}, got {value}"
        else:
            msg = f"Parameter '{param_name}' must be <= {max_val}, got {value}"

        super().__init__(msg)


class PricingCalculationException(OptionPricingException):
    """Raised when pricing calculation fails."""

    pass


class DataIOException(OptionPricingException):
    """Raised when data input/output operations fail."""

    pass


# ==============================================================================
# Logging Configuration
# ==============================================================================


def setup_logger(
    name: str = "OptionPricing",
    log_file: str = "option_pricing.log",
    level: int = logging.INFO,
    console_output: bool = True,
) -> logging.Logger:
    """
    Set up and configure a logger for the application.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        console_output: Whether to also output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_output:
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Default logger instance
logger = setup_logger()


# ==============================================================================
# Decorators
# ==============================================================================

F = TypeVar("F", bound=Callable[..., Any])


def time_it(func: F) -> F:
    """
    Decorator to measure and log the execution time of a function.

    This decorator measures wall clock time and logs the duration.
    Useful for performance monitoring of pricing calculations.

    Args:
        func: Function to be timed

    Returns:
        Wrapped function that logs execution time

    Example:
        @time_it
        def price_option(self):
            # pricing logic
            pass
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        logger.info(f"Starting execution of {func.__name__}")

        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {elapsed_time:.4f} seconds")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"Error in {func.__name__} after {elapsed_time:.4f} seconds: {str(e)}"
            )
            raise

    return wrapper  # type: ignore


def log_call(func: F) -> F:
    """
    Decorator to log function calls with arguments and return values.

    Uses @wraps to preserve function metadata when stacking decorators.
    Logs entry, arguments, return value, and any exceptions.

    Args:
        func: Function to be logged

    Returns:
        Wrapped function that logs calls

    Example:
        @log_call
        @time_it
        def calculate_delta(self):
            # calculation logic
            pass
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Build argument string for logging
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.debug(f"Calling {func.__name__}({signature})")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result!r}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise

    return wrapper  # type: ignore


def validate_inputs(func: F) -> F:
    """
    Decorator to validate function inputs before execution.

    Can be used in conjunction with type hints and custom validation logic.

    Args:
        func: Function whose inputs should be validated

    Returns:
        Wrapped function with input validation
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Custom validation logic can be added here
        logger.debug(f"Validating inputs for {func.__name__}")
        return func(*args, **kwargs)

    return wrapper  # type: ignore


# ==============================================================================
# Descriptors for Validation
# ==============================================================================


class TypedDescriptor:
    """
    Base descriptor that enforces type checking.

    This descriptor validates that the assigned value matches the expected type.
    Follows the descriptor protocol with __get__, __set__, and __set_name__.
    """

    def __init__(self, expected_type: type, default: Any = None):
        """
        Initialize typed descriptor.

        Args:
            expected_type: The expected type for this descriptor
            default: Default value (optional)
        """
        self.expected_type = expected_type
        self.default = default
        self.name: Optional[str] = None

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when descriptor is assigned to a class attribute."""
        self.name = name

    def __get__(self, instance: Any, owner: type) -> Any:
        """Get the value from the instance dictionary."""
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance: Any, value: Any) -> None:
        """Set the value after type validation."""
        if not isinstance(value, self.expected_type):
            raise InvalidTypeException(
                self.name or "unknown", self.expected_type, type(value)
            )
        instance.__dict__[self.name] = value


class NonNegativeFloat(TypedDescriptor):
    """
    Descriptor for non-negative floating point numbers.

    Validates that the value is a float and >= 0.
    Commonly used for volatility, time, and price parameters.
    """

    def __init__(self, default: float = 0.0):
        super().__init__(float, default)

    def __set__(self, instance: Any, value: Union[int, float]) -> None:
        """Set value after validating it's non-negative."""
        # Convert int to float if needed
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise InvalidTypeException(self.name or "unknown", float, type(value))

        if value < 0:
            raise NegativeValueException(self.name or "unknown", value)

        instance.__dict__[self.name] = value


class PositiveFloat(TypedDescriptor):
    """
    Descriptor for strictly positive floating point numbers.

    Validates that the value is a float and > 0.
    Used for parameters that cannot be zero (e.g., stock price, strike).
    """

    def __init__(self, default: float = 1.0):
        super().__init__(float, default)

    def __set__(self, instance: Any, value: Union[int, float]) -> None:
        """Set value after validating it's positive."""
        # Convert int to float if needed
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise InvalidTypeException(self.name or "unknown", float, type(value))

        if value <= 0:
            raise InvalidRangeException(self.name or "unknown", value, min_val=0.0)

        instance.__dict__[self.name] = value


class BoundedFloat(TypedDescriptor):
    """
    Descriptor for floating point numbers within a specific range.

    Validates that the value is within [min_val, max_val].
    Useful for probabilities, percentages, and other bounded parameters.
    """

    def __init__(self, min_val: float, max_val: float, default: float):
        super().__init__(float, default)
        self.min_val = min_val
        self.max_val = max_val

    def __set__(self, instance: Any, value: Union[int, float]) -> None:
        """Set value after validating it's within bounds."""
        # Convert int to float if needed
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise InvalidTypeException(self.name or "unknown", float, type(value))

        if value < self.min_val or value > self.max_val:
            raise InvalidRangeException(
                self.name or "unknown", value, self.min_val, self.max_val
            )

        instance.__dict__[self.name] = value


class PositiveInteger(TypedDescriptor):
    """
    Descriptor for strictly positive integers.

    Validates that the value is an integer and > 0.
    Used for counts, iterations, and simulation parameters.
    """

    def __init__(self, default: int = 1):
        super().__init__(int, default)

    def __set__(self, instance: Any, value: int) -> None:
        """Set value after validating it's a positive integer."""
        if not isinstance(value, int):
            raise InvalidTypeException(self.name or "unknown", int, type(value))

        if value <= 0:
            raise InvalidRangeException(self.name or "unknown", value, min_val=0)

        instance.__dict__[self.name] = value


class NonNegativeInteger(TypedDescriptor):
    """
    Descriptor for non-negative integers.

    Validates that the value is an integer and >= 0.
    Used for counts that can be zero (e.g., number of jumps).
    """

    def __init__(self, default: int = 0):
        super().__init__(int, default)

    def __set__(self, instance: Any, value: int) -> None:
        """Set value after validating it's a non-negative integer."""
        if not isinstance(value, int):
            raise InvalidTypeException(self.name or "unknown", int, type(value))

        if value < 0:
            raise NegativeValueException(self.name or "unknown", float(value))

        instance.__dict__[self.name] = value


class StringDescriptor(TypedDescriptor):
    """
    Descriptor for string values with optional constraints.

    Validates that the value is a non-empty string.
    Used for names, IDs, and other text parameters.
    """

    def __init__(self, default: str = "", allow_empty: bool = False):
        super().__init__(str, default)
        self.allow_empty = allow_empty

    def __set__(self, instance: Any, value: str) -> None:
        """Set value after validating it's a valid string."""
        if not isinstance(value, str):
            raise InvalidTypeException(self.name or "unknown", str, type(value))

        if not self.allow_empty and not value.strip():
            raise OptionPricingException(
                f"Parameter '{self.name}' cannot be an empty string"
            )

        instance.__dict__[self.name] = value


# ==============================================================================
# Validation Utilities
# ==============================================================================


def validate_positive(value: float, name: str) -> None:
    """
    Validate that a value is positive.

    Args:
        value: Value to validate
        name: Parameter name for error messages

    Raises:
        InvalidRangeException: If value is not positive
    """
    if value <= 0:
        raise InvalidRangeException(name, value, min_val=0.0)


def validate_non_negative(value: float, name: str) -> None:
    """
    Validate that a value is non-negative.

    Args:
        value: Value to validate
        name: Parameter name for error messages

    Raises:
        NegativeValueException: If value is negative
    """
    if value < 0:
        raise NegativeValueException(name, value)


def validate_range(value: float, name: str, min_val: float, max_val: float) -> None:
    """
    Validate that a value is within a specified range.

    Args:
        value: Value to validate
        name: Parameter name for error messages
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Raises:
        InvalidRangeException: If value is outside range
    """
    if value < min_val or value > max_val:
        raise InvalidRangeException(name, value, min_val, max_val)


def validate_type(value: Any, expected_type: type, name: str) -> None:
    """
    Validate that a value has the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        name: Parameter name for error messages

    Raises:
        InvalidTypeException: If value has wrong type
    """
    if not isinstance(value, expected_type):
        raise InvalidTypeException(name, expected_type, type(value))


# ==============================================================================
# Utility Functions
# ==============================================================================


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime object as a standard timestamp string.

    Args:
        dt: Datetime object (uses current time if None)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Perform division with zero-check protection.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Value to return if denominator is zero

    Returns:
        Result of division or default value
    """
    if abs(denominator) < 1e-10:  # Floating point comparison
        return default
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to be within a specified range.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


# ==============================================================================
# Constants
# ==============================================================================

# Numerical precision constants
EPSILON = 1e-10
MAX_ITERATIONS = 10000

# Option type constants
OPTION_CALL = "call"
OPTION_PUT = "put"

# Asset class constants
ASSET_EQUITY = "equity"
ASSET_FX = "fx"
ASSET_RATES = "rates"
ASSET_COMMODITY = "commodity"
ASSET_CRYPTO = "crypto"

# Pricing method constants
METHOD_BLACK_SCHOLES = "black_scholes"
METHOD_BLACK_SCHOLES_MERTON = "black_scholes_merton"
METHOD_BLACK = "black"
METHOD_BINOMIAL = "binomial"
METHOD_CRR = "crr"
METHOD_JARROW_RUDD = "jarrow_rudd"
METHOD_TRINOMIAL = "trinomial"
METHOD_EXPLICIT_FD = "explicit_fd"
METHOD_IMPLICIT_FD = "implicit_fd"
METHOD_CRANK_NICOLSON = "crank_nicolson"
METHOD_MONTE_CARLO = "monte_carlo"
METHOD_QUASI_MONTE_CARLO = "quasi_monte_carlo"
METHOD_LSMC = "lsmc"
METHOD_JUMP_DIFFUSION_MC = "jump_diffusion_mc"

# Greek calculation method constants
GREEK_ANALYTICAL = "analytical"
GREEK_BUMP_REVALUE = "bump_revalue"
GREEK_TREE = "tree"
GREEK_FD_GRID = "fd_grid"
GREEK_IMPLIED = "implied"


if __name__ == "__main__":
    # Demo usage of utilities
    print("=" * 60)
    print("Option Pricing Platform - Utilities Module")
    print("=" * 60)

    # Test logger
    logger.info("Testing logger functionality")

    # Test decorators
    @time_it
    @log_call
    def sample_calculation(x: float, y: float) -> float:
        """Sample calculation for testing decorators."""
        time.sleep(0.1)  # Simulate work
        return x + y

    result = sample_calculation(10.5, 20.3)
    print(f"\nSample calculation result: {result}")

    # Test descriptors in a sample class
    class SampleOption:
        price = PositiveFloat(default=100.0)
        volatility = NonNegativeFloat(default=0.2)
        time_to_maturity = PositiveFloat(default=1.0)
        simulations = PositiveInteger(default=10000)

        def __repr__(self) -> str:
            return (
                f"SampleOption(price={self.price}, vol={self.volatility}, "
                f"T={self.time_to_maturity}, sims={self.simulations})"
            )

    print("\n" + "=" * 60)
    print("Testing Descriptors")
    print("=" * 60)

    opt = SampleOption()
    print(f"Default values: {opt}")

    opt.price = 105.5
    opt.volatility = 0.25
    opt.time_to_maturity = 0.5
    opt.simulations = 50000
    print(f"Updated values: {opt}")

    # Test validation errors
    print("\nTesting validation errors:")
    try:
        opt.price = -100  # Should raise error
    except NegativeValueException as e:
        print(f"✓ Caught expected error: {e}")

    try:
        opt.volatility = "invalid"  # Should raise error
    except InvalidTypeException as e:
        print(f"✓ Caught expected error: {e}")

    try:
        opt.simulations = -5  # Should raise error
    except InvalidRangeException as e:
        print(f"✓ Caught expected error: {e}")

    print("\n" + "=" * 60)
    print("Utilities module ready for use!")
    print("=" * 60)
