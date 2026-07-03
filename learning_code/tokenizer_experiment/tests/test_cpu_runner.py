from tokenizer_experiment.core.variants import ALL_VARIANTS
from tokenizer_experiment.cpu.runner import run_cpu_variant


def test_cpu_runner_executes_all_variants() -> None:
    text = "Hello tokenizer world. 12345\n" * 3

    results = [
        run_cpu_variant(
            variant=variant,
            text=text,
            repeats=1,
            parallel_workers=2,
            parallel_backend="thread",
            chunk_count=3,
        )
        for variant in ALL_VARIANTS
    ]

    assert [result.variant for result in results] == [
        "with_pretokenizer_serial",
        "without_pretokenizer_serial",
        "with_pretokenizer_parallel",
        "without_pretokenizer_parallel",
    ]
    assert all(result.stats.byte_count == len(text.encode("utf-8")) for result in results)
    assert results[0].stats.span_count > results[1].stats.span_count
    assert results[2].parallel_workers == 2
    assert results[3].chunk_count > 1
