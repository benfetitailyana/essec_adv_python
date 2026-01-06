"""Trader, orders, and TradeBlotter container."""
from __future__ import annotations

import time
from collections.abc import MutableSequence
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Literal

from decorators import log_call


@dataclass
class Trader:
    trader_id: str
    name: str
    desk: str


@dataclass
class Order:
    trader: Trader
    underlier: str
    strike: float
    maturity: float
    notional: int
    timestamp: float = field(default_factory=time.time)
    side: Literal["BUY", "SELL"] = "BUY"


class TradeBlotter(MutableSequence[Order]):
    def __init__(self, orders: Iterable[Order] | None = None):
        self._orders: list[Order] = list(orders or [])

    def __len__(self) -> int:
        return len(self._orders)

    def __getitem__(self, index):
        return self._orders[index]

    def __delitem__(self, index):
        del self._orders[index]

    def __setitem__(self, index, value: Order):
        self._orders[index] = value

    def insert(self, index: int, value: Order) -> None:
        self._orders.insert(index, value)

    def sum_notional(self) -> int:
        return sum(order.notional for order in self._orders)

    def filter_by_strike(self, strike: float) -> list[Order]:
        return [order for order in self._orders if order.strike == strike]

    def unique_underlier(self) -> set[str]:
        return {order.underlier for order in self._orders}

    @log_call
    def add_order(self, order: Order) -> None:
        self.append(order)

    def __iter__(self) -> Iterator[Order]:  # pragma: no cover - delegation
        return iter(self._orders)
