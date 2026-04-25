"""Shared caching utilities."""

from collections.abc import Callable
from functools import lru_cache
from typing import TypeVar

T = TypeVar("T")


def fast_cache(maxsize: int = 128) -> Callable[[T], T]:
    """LRU cache decorator optimized for engineering calculations."""
    return lru_cache(maxsize=maxsize)
