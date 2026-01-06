"""Data IO utilities for trades and results."""
from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Iterable, List

from trading import Order, Trader



def read_trades_from_csv(path: Path, trader: Trader) -> List[Order]:
    orders: List[Order] = []
    with path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            side = row.get("side", "BUY").strip().upper()
            if side not in ("BUY", "SELL"):
                side = "BUY"

            orders.append(
                Order(
                    trader=trader,
                    underlier=row.get("underlier", "UNKNOWN"),
                    strike=float(row["strike"]),
                    maturity=float(row["maturity"]),
                    notional=float(row.get("notional", 1)),
                    timestamp=float(row.get("timestamp", time.time())),
                    side=side,
                )
            )
    return orders
