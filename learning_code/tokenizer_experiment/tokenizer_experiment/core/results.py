from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WorkloadStats:
    span_count: int
    byte_count: int
    token_count: int
    checksum: int


@dataclass(frozen=True)
class VariantResult:
    variant: str
    context_chars: int
    repeats: int
    parallel_workers: int
    parallel_backend: str
    chunk_count: int
    stats: WorkloadStats
    timings: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
