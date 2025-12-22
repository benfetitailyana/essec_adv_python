"""
Trade blotter container implementing collections.abc.MutableSequence.

Demonstrates:
- Custom container by inheriting from collections.abc.MutableSequence
- Implementation of all required abstract methods
- Utility methods for filtering and aggregation
- Rich dunder methods
"""

from typing import List, Optional, Iterator, Union
from collections.abc import MutableSequence
from datetime import datetime

from models import OrderInfo, TraderInfo
from interfaces import OptionType
from utils import logger


class Trade:
    """
    Represents a completed trade.

    Attributes:
        order: The order that was filled
        fill_price: Price at which the trade was executed
        fill_time: When the trade was executed
        trade_id: Unique trade identifier
    """

    def __init__(
        self,
        order: OrderInfo,
        fill_price: float,
        trade_id: Optional[str] = None,
        fill_time: Optional[datetime] = None,
    ):
        """Initialize trade from order."""
        self.order = order
        self.fill_price = fill_price
        self.trade_id = trade_id or f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.fill_time = fill_time or datetime.now()

        logger.debug(f"Trade created: {self}")

    @property
    def notional(self) -> float:
        """Calculate notional value of trade."""
        return abs(self.order.quantity) * self.fill_price

    @property
    def underlying(self) -> str:
        """Get underlying ticker."""
        return self.order.underlying

    @property
    def strike(self) -> float:
        """Get strike price."""
        return self.order.strike

    @property
    def trader(self) -> TraderInfo:
        """Get trader info."""
        return self.order.trader_info

    @property
    def option_type(self) -> OptionType:
        """Get option type."""
        return self.order.option_type

    def __repr__(self) -> str:
        return (
            f"Trade(id={self.trade_id}, order_id={self.order.order_id}, "
            f"price={self.fill_price:.4f}, notional={self.notional:.2f})"
        )

    def __str__(self) -> str:
        return (
            f"Trade {self.trade_id}: {abs(self.order.quantity)} contracts "
            f"@ {self.fill_price:.4f} (notional: {self.notional:.2f})"
        )


class TradeBlotter(MutableSequence):
    """
    Trade blotter as a custom container.

    Implements collections.abc.MutableSequence to behave like a list
    with additional domain-specific functionality.

    Required abstract methods from MutableSequence:
    - __getitem__
    - __setitem__
    - __delitem__
    - __len__
    - insert

    Inherited concrete methods from MutableSequence:
    - append, extend, pop, remove, clear, reverse, etc.

    Additional utility methods:
    - sum_notional: Calculate total notional value
    - filter_by_strike: Filter trades by strike price
    - filter_by_underlying: Filter by underlying asset
    - unique_underliers: Get unique underlying tickers
    - filter_by_trader: Filter by trader
    """

    def __init__(self, name: str = "Default Blotter"):
        """
        Initialize trade blotter.

        Args:
            name: Name of the blotter
        """
        self.name = name
        self._trades: List[Trade] = []
        logger.info(f"TradeBlotter '{name}' created")

    # ==========================================================================
    # Required abstract methods from MutableSequence
    # ==========================================================================

    def __getitem__(self, index: Union[int, slice]) -> Union[Trade, List[Trade]]:
        """
        Get trade by index or slice.

        Allows: trade = blotter[0] or trades = blotter[1:5]
        """
        return self._trades[index]

    def __setitem__(
        self, index: Union[int, slice], value: Union[Trade, List[Trade]]
    ) -> None:
        """
        Set trade at index or slice.

        Allows: blotter[0] = trade
        """
        self._trades[index] = value
        logger.debug(f"Trade(s) set at index {index}")

    def __delitem__(self, index: Union[int, slice]) -> None:
        """
        Delete trade at index or slice.

        Allows: del blotter[0]
        """
        del self._trades[index]
        logger.debug(f"Trade(s) deleted at index {index}")

    def __len__(self) -> int:
        """
        Return number of trades.

        Allows: count = len(blotter)
        """
        return len(self._trades)

    def insert(self, index: int, value: Trade) -> None:
        """
        Insert trade at specific index.

        Allows: blotter.insert(0, trade)
        """
        if not isinstance(value, Trade):
            raise TypeError(f"Can only insert Trade objects, got {type(value)}")

        self._trades.insert(index, value)
        logger.debug(f"Trade inserted at index {index}: {value.trade_id}")

    # ==========================================================================
    # Additional dunder methods
    # ==========================================================================

    def __iter__(self) -> Iterator[Trade]:
        """
        Iterate over trades.

        Allows: for trade in blotter: ...
        """
        return iter(self._trades)

    def __contains__(self, item: Trade) -> bool:
        """
        Check if trade is in blotter.

        Allows: if trade in blotter: ...
        """
        return item in self._trades

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"TradeBlotter(name='{self.name}', trades={len(self)})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Trade Blotter '{self.name}': {len(self)} trades, notional={self.sum_notional():.2f}"

    # ==========================================================================
    # Utility methods
    # ==========================================================================

    def sum_notional(self) -> float:
        """
        Calculate total notional value of all trades.

        Returns:
            Sum of notional values
        """
        return sum(trade.notional for trade in self._trades)

    def filter_by_strike(self, strike: float, tolerance: float = 0.01) -> List[Trade]:
        """
        Filter trades by strike price.

        Args:
            strike: Strike price to filter by
            tolerance: Tolerance for floating point comparison

        Returns:
            List of trades matching the strike
        """
        return [
            trade for trade in self._trades if abs(trade.strike - strike) < tolerance
        ]

    def filter_by_underlying(self, ticker: str) -> List[Trade]:
        """
        Filter trades by underlying ticker.

        Args:
            ticker: Underlying ticker symbol

        Returns:
            List of trades on that underlying
        """
        return [
            trade
            for trade in self._trades
            if trade.underlying.upper() == ticker.upper()
        ]

    def filter_by_trader(self, trader_id: str) -> List[Trade]:
        """
        Filter trades by trader ID.

        Args:
            trader_id: Trader identifier

        Returns:
            List of trades by that trader
        """
        return [trade for trade in self._trades if trade.trader.trader_id == trader_id]

    def filter_by_option_type(self, option_type: OptionType) -> List[Trade]:
        """
        Filter trades by option type (call/put).

        Args:
            option_type: OptionType.CALL or OptionType.PUT

        Returns:
            List of matching trades
        """
        return [trade for trade in self._trades if trade.option_type == option_type]

    def unique_underliers(self) -> List[str]:
        """
        Get list of unique underlying tickers.

        Returns:
            Sorted list of unique ticker symbols
        """
        return sorted(set(trade.underlying for trade in self._trades))

    def unique_traders(self) -> List[str]:
        """
        Get list of unique trader IDs.

        Returns:
            Sorted list of unique trader IDs
        """
        return sorted(set(trade.trader.trader_id for trade in self._trades))

    def get_summary(self) -> dict:
        """
        Get summary statistics for the blotter.

        Returns:
            Dictionary with summary statistics
        """
        if not self._trades:
            return {
                "num_trades": 0,
                "total_notional": 0.0,
                "unique_underliers": [],
                "unique_traders": [],
            }

        return {
            "num_trades": len(self),
            "total_notional": self.sum_notional(),
            "unique_underliers": self.unique_underliers(),
            "unique_traders": self.unique_traders(),
            "avg_notional": self.sum_notional() / len(self) if len(self) > 0 else 0,
        }

    def clear_all(self) -> None:
        """Clear all trades from blotter."""
        count = len(self)
        self._trades.clear()
        logger.info(f"Cleared {count} trades from blotter '{self.name}'")


if __name__ == "__main__":
    print("=" * 70)
    print("Trade Blotter - Custom Container (MutableSequence)")
    print("=" * 70)

    # Create sample trader
    trader = TraderInfo(trader_id="AJ001", name="Adam Jones", desk="JapanEQExotics")

    # Create sample orders
    from models import OrderInfo

    orders = [
        OrderInfo(
            order_id="ORD001",
            trader_info=trader,
            quantity=100,
            underlying="NIKKEI225",
            strike=28000.0,
            maturity=0.25,
            option_type=OptionType.CALL,
        ),
        OrderInfo(
            order_id="ORD002",
            trader_info=trader,
            quantity=50,
            underlying="NIKKEI225",
            strike=29000.0,
            maturity=0.25,
            option_type=OptionType.CALL,
        ),
        OrderInfo(
            order_id="ORD003",
            trader_info=trader,
            quantity=75,
            underlying="TOPIX",
            strike=2000.0,
            maturity=0.5,
            option_type=OptionType.PUT,
        ),
    ]

    # Create blotter
    blotter = TradeBlotter(name="Adam Jones Blotter")
    print(f"\nBlotter created: {blotter}")

    # Add trades
    print("\nAdding trades...")
    for i, order in enumerate(orders, 1):
        trade = Trade(order, fill_price=100.0 + i * 10)
        blotter.append(trade)
        print(f"  Added: {trade}")

    print(f"\nBlotter after trades: {blotter}")

    # Test sequence operations
    print(f"\nFirst trade: {blotter[0]}")
    print(f"Last trade: {blotter[-1]}")
    print(f"Number of trades: {len(blotter)}")

    # Test filtering
    print(f"\nNIKKEI225 trades: {len(blotter.filter_by_underlying('NIKKEI225'))}")
    print(f"Strike 28000 trades: {len(blotter.filter_by_strike(28000.0))}")
    print(f"Call options: {len(blotter.filter_by_option_type(OptionType.CALL))}")

    # Test aggregation
    print(f"\nTotal notional: {blotter.sum_notional():.2f}")
    print(f"Unique underliers: {blotter.unique_underliers()}")

    # Test summary
    print("\nSummary:")
    summary = blotter.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Test iteration
    print("\nIterating over trades:")
    for i, trade in enumerate(blotter, 1):
        print(f"  {i}. {trade.trade_id}: {trade.underlying}")

    print("\n" + "=" * 70)
