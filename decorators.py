"""Decorators for logging and timing."""
from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def time_it(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000
        logger.info("%s executed in %.2f ms", func.__name__, duration)
        return result

    return wrapper  # type: ignore[return-value]


def log_call(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        logger.info("Calling %s with args=%s kwargs=%s", func.__name__, args, kwargs)
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Error in %s", func.__name__)
            raise

    return wrapper  # type: ignore[return-value]
