from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any

from tokenizer_experiment.core.chunking import split_text_for_workers
from tokenizer_experiment.core.timing import summarize_timings, timed_repeats
from tokenizer_experiment.core.variants import ExperimentVariant
from tokenizer_experiment.cpu.bpe_reference import (
    ReferenceBpeArtifact,
    Word,
    build_word_counts,
    encode_spans,
    merge_word_counts,
    train_from_word_counts,
    train_reference_bpe,
)
from tokenizer_experiment.cpu.pretokenizer import RegexPretokenizer, split_without_pretokenizer
from tokenizer_experiment.cpu.workload import FNV_OFFSET_BASIS_64, FNV_PRIME_64, MASK_64


def run_training_baseline(
    variant: ExperimentVariant,
    text: str,
    vocab_size: int,
    repeats: int,
    parallel_workers: int,
    chunk_count: int,
    parallel_backend: str = "process",
) -> dict[str, Any]:
    if variant.uses_parallel:
        worker_count = max(1, parallel_workers)
        chunks = split_text_for_workers(text, chunk_count)
        timed = timed_repeats(
            lambda: _train_parallel(variant, chunks, vocab_size, worker_count, parallel_backend),
            repeats=repeats,
        )
        backend_label = parallel_backend
    else:
        worker_count = 1
        chunks = [text]
        timed = timed_repeats(
            lambda: _train_serial(variant, text, vocab_size),
            repeats=repeats,
        )
        backend_label = "serial"

    artifact = timed.value
    return {
        "phase": "train",
        "variant": variant.name,
        "context_chars": len(text),
        "repeats": repeats,
        "parallel_workers": worker_count,
        "parallel_backend": backend_label,
        "chunk_count": len(chunks),
        "timings": summarize_timings(timed.timings_s),
        "training": _artifact_summary(artifact),
        "artifact": artifact,
    }


def run_encoding_baseline(
    variant: ExperimentVariant,
    text: str,
    artifact: ReferenceBpeArtifact,
    repeats: int,
    parallel_workers: int,
    chunk_count: int,
    parallel_backend: str = "process",
) -> dict[str, Any]:
    if variant.uses_parallel:
        worker_count = max(1, parallel_workers)
        chunks = split_text_for_workers(text, chunk_count)
        timed = timed_repeats(
            lambda: _encode_parallel(variant, chunks, artifact, worker_count, parallel_backend),
            repeats=repeats,
        )
        backend_label = parallel_backend
    else:
        worker_count = 1
        chunks = [text]
        timed = timed_repeats(
            lambda: _encode_serial(variant, text, artifact),
            repeats=repeats,
        )
        backend_label = "serial"

    stats = timed.value
    return {
        "phase": "encode",
        "variant": variant.name,
        "context_chars": len(text),
        "repeats": repeats,
        "parallel_workers": worker_count,
        "parallel_backend": backend_label,
        "chunk_count": len(chunks),
        "timings": summarize_timings(timed.timings_s),
        "encoding": stats,
    }


def strip_runtime_objects(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "artifact"}


def _train_serial(
    variant: ExperimentVariant,
    text: str,
    vocab_size: int,
) -> ReferenceBpeArtifact:
    spans = _split_for_variant(variant, text)
    return train_reference_bpe(spans, vocab_size)


def _train_parallel(
    variant: ExperimentVariant,
    chunks: list[str],
    vocab_size: int,
    worker_count: int,
    parallel_backend: str,
) -> ReferenceBpeArtifact:
    tasks = [(chunk, variant.uses_pretokenizer) for chunk in chunks]
    counters = _map_tasks(_word_count_chunk, tasks, worker_count, parallel_backend)
    word_counts = merge_word_counts(counters)
    span_count = sum(sum(counter.values()) for counter in counters)
    return train_from_word_counts(word_counts, span_count=span_count, vocab_size=vocab_size)


def _encode_serial(
    variant: ExperimentVariant,
    text: str,
    artifact: ReferenceBpeArtifact,
) -> dict[str, int | float]:
    spans = _split_for_variant(variant, text)
    return _summarize_tokens(spans, encode_spans(spans, artifact))


def _encode_parallel(
    variant: ExperimentVariant,
    chunks: list[str],
    artifact: ReferenceBpeArtifact,
    worker_count: int,
    parallel_backend: str,
) -> dict[str, int | float]:
    tasks = [(chunk, variant.uses_pretokenizer, artifact) for chunk in chunks]
    partials = _map_tasks(_encode_chunk, tasks, worker_count, parallel_backend)
    return _merge_encoding_stats(partials)


def _word_count_chunk(task: tuple[str, bool]) -> Counter[Word]:
    text, use_pretokenizer = task
    spans = _split_text(text, use_pretokenizer)
    return build_word_counts(spans)


def _encode_chunk(task: tuple[str, bool, ReferenceBpeArtifact]) -> dict[str, int | float]:
    text, use_pretokenizer, artifact = task
    spans = _split_text(text, use_pretokenizer)
    return _summarize_tokens(spans, encode_spans(spans, artifact))


def _split_for_variant(variant: ExperimentVariant, text: str) -> list[str]:
    return _split_text(text, variant.uses_pretokenizer)


def _split_text(text: str, use_pretokenizer: bool) -> list[str]:
    if use_pretokenizer:
        return RegexPretokenizer().split(text)
    return split_without_pretokenizer(text)


def _map_tasks(fn, tasks, worker_count: int, parallel_backend: str):
    if parallel_backend == "thread":
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            return list(executor.map(fn, tasks))
    if parallel_backend != "process":
        raise ValueError(f"unknown parallel backend: {parallel_backend}")
    try:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            return list(executor.map(fn, tasks))
    except (NotImplementedError, OSError, PermissionError):
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            return list(executor.map(fn, tasks))


def _artifact_summary(artifact: ReferenceBpeArtifact) -> dict[str, int]:
    return {
        "span_count": artifact.span_count,
        "initial_word_count": artifact.word_count,
        "byte_count": artifact.byte_count,
        "merge_count": len(artifact.merges),
        "vocab_size": artifact.vocab_size,
    }


def _summarize_tokens(spans: list[str], tokens: list[bytes]) -> dict[str, int | float]:
    byte_count = sum(len(span.encode("utf-8")) for span in spans)
    token_count = len(tokens)
    checksum = _token_checksum(tokens)
    return {
        "span_count": len(spans),
        "byte_count": byte_count,
        "token_count": token_count,
        "bytes_per_token": byte_count / token_count if token_count else 0.0,
        "checksum": checksum,
    }


def _merge_encoding_stats(items: list[dict[str, int | float]]) -> dict[str, int | float]:
    span_count = sum(int(item["span_count"]) for item in items)
    byte_count = sum(int(item["byte_count"]) for item in items)
    token_count = sum(int(item["token_count"]) for item in items)
    checksum = FNV_OFFSET_BASIS_64
    for item in items:
        checksum ^= int(item["checksum"])
        checksum = (checksum * FNV_PRIME_64) & MASK_64
    return {
        "span_count": span_count,
        "byte_count": byte_count,
        "token_count": token_count,
        "bytes_per_token": byte_count / token_count if token_count else 0.0,
        "checksum": checksum,
    }


def _token_checksum(tokens: list[bytes]) -> int:
    value = FNV_OFFSET_BASIS_64
    for token in tokens:
        for byte in token:
            value ^= byte
            value = (value * FNV_PRIME_64) & MASK_64
        value ^= len(token)
        value = (value * FNV_PRIME_64) & MASK_64
    return value
