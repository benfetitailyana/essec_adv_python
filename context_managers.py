"""Context managers for pricing sessions and CSV IO."""
from __future__ import annotations

import csv
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


@dataclass
class PricingSession:
    session_name: str

    def __enter__(self) -> "PricingSession":
        logger.info("Starting session %s", self.session_name)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc:
            logger.exception("Session %s raised %s", self.session_name, exc)
        else:
            logger.info("Session %s completed", self.session_name)
        return False


@contextmanager
def csv_writer(path: Path, fieldnames: list[str]) -> Iterator[csv.DictWriter]:
    logger.info("Opening CSV writer at %s", path)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        yield writer
