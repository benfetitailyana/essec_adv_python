"""Data IO utilities for trades and results."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from trading import Order, Trader


def read_trades_from_csv(path: Path, trader: Trader) -> List[Order]:
    orders: List[Order] = []
    with path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            orders.append(
                Order(
                    trader=trader,
                    underlier=row.get("underlier", "UNKNOWN"),
                    strike=float(row["strike"]),
                    maturity=float(row["maturity"]),
                    notional=int(row.get("notional", 1)),
                )
            )
    return orders
