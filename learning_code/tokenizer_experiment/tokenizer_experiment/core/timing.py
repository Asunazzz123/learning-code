from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class TimedResult(Generic[T]):
    value: T
    timings_s: list[float]


def timed_repeats(fn: Callable[[], T], repeats: int) -> TimedResult[T]:
    if repeats <= 0:
        raise ValueError(f"repeats must be positive, got {repeats}")

    value: T | None = None
    timings: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        value = fn()
        timings.append(time.perf_counter() - start)

    return TimedResult(value=value, timings_s=timings)  # type: ignore[arg-type]


def summarize_timings(timings_s: list[float]) -> dict[str, float]:
    if not timings_s:
        raise ValueError("cannot summarize empty timings")
    return {
        "min_s": min(timings_s),
        "median_s": statistics.median(timings_s),
        "mean_s": statistics.fmean(timings_s),
    }
