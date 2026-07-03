from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

from tokenizer_experiment.core.chunking import split_text_for_workers
from tokenizer_experiment.core.results import VariantResult, WorkloadStats
from tokenizer_experiment.core.timing import summarize_timings, timed_repeats
from tokenizer_experiment.core.variants import ExperimentVariant
from tokenizer_experiment.cpu.pretokenizer import RegexPretokenizer, split_without_pretokenizer
from tokenizer_experiment.cpu.workload import byte_workload, merge_stats


def run_cpu_variant(
    variant: ExperimentVariant,
    text: str,
    repeats: int,
    parallel_workers: int,
    chunk_count: int,
    parallel_backend: str = "process",
) -> VariantResult:
    if variant.uses_parallel:
        worker_count = max(1, parallel_workers)
        chunks = split_text_for_workers(text, chunk_count)
        result = timed_repeats(
            lambda: _run_parallel(variant, chunks, worker_count, parallel_backend),
            repeats=repeats,
        )
        backend_label = parallel_backend
    else:
        worker_count = 1
        chunks = [text]
        result = timed_repeats(
            lambda: _run_serial(variant, text),
            repeats=repeats,
        )
        backend_label = "serial"

    stats = result.value
    return VariantResult(
        variant=variant.name,
        context_chars=len(text),
        repeats=repeats,
        parallel_workers=worker_count,
        parallel_backend=backend_label,
        chunk_count=len(chunks),
        stats=stats,
        timings=summarize_timings(result.timings_s),
    )


def _run_serial(variant: ExperimentVariant, text: str) -> WorkloadStats:
    return _process_chunk((text, variant.uses_pretokenizer))


def _run_parallel(
    variant: ExperimentVariant,
    chunks: list[str],
    worker_count: int,
    parallel_backend: str,
) -> WorkloadStats:
    tasks = [(chunk, variant.uses_pretokenizer) for chunk in chunks]
    if parallel_backend == "thread":
        return _run_thread_pool(tasks, worker_count)
    if parallel_backend != "process":
        raise ValueError(f"unknown parallel backend: {parallel_backend}")
    try:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            return merge_stats(list(executor.map(_process_chunk, tasks)))
    except (NotImplementedError, OSError, PermissionError):
        return _run_thread_pool(tasks, worker_count)


def _run_thread_pool(tasks: list[tuple[str, bool]], worker_count: int) -> WorkloadStats:
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return merge_stats(list(executor.map(_process_chunk, tasks)))


def _process_chunk(task: tuple[str, bool]) -> WorkloadStats:
    text, use_pretokenizer = task
    if use_pretokenizer:
        spans = RegexPretokenizer().split(text)
    else:
        spans = split_without_pretokenizer(text)
    return byte_workload(spans)
