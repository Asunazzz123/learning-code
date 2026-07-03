from __future__ import annotations

from tokenizer_experiment.core.results import WorkloadStats


FNV_OFFSET_BASIS_64 = 1469598103934665603
FNV_PRIME_64 = 1099511628211
MASK_64 = (1 << 64) - 1


def byte_workload(spans: list[str]) -> WorkloadStats:
    byte_count = 0
    token_count = 0
    checksum = FNV_OFFSET_BASIS_64

    for span in spans:
        raw = span.encode("utf-8")
        byte_count += len(raw)
        token_count += len(raw)
        checksum = _mix_bytes(checksum, raw)

    return WorkloadStats(
        span_count=len(spans),
        byte_count=byte_count,
        token_count=token_count,
        checksum=checksum,
    )


def merge_stats(stats: list[WorkloadStats]) -> WorkloadStats:
    span_count = sum(item.span_count for item in stats)
    byte_count = sum(item.byte_count for item in stats)
    token_count = sum(item.token_count for item in stats)
    checksum = FNV_OFFSET_BASIS_64
    for item in stats:
        checksum ^= item.checksum
        checksum = (checksum * FNV_PRIME_64) & MASK_64
    return WorkloadStats(
        span_count=span_count,
        byte_count=byte_count,
        token_count=token_count,
        checksum=checksum,
    )


def _mix_bytes(seed: int, raw: bytes) -> int:
    value = seed
    for byte in raw:
        value ^= byte
        value = (value * FNV_PRIME_64) & MASK_64
    return value
