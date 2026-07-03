from tokenizer_experiment.benchmarks.run_cpu import CpuBenchmarkConfig, run_benchmark
from tokenizer_experiment.core.variants import ALL_VARIANTS
from tokenizer_experiment.cpu.baseline import run_training_baseline


def test_training_baseline_reports_all_variants() -> None:
    text = "aa aa bb bb aa"
    results = [
        run_training_baseline(
            variant=variant,
            text=text,
            vocab_size=270,
            repeats=1,
            parallel_workers=2,
            chunk_count=2,
            parallel_backend="thread",
        )
        for variant in ALL_VARIANTS
    ]

    assert [result["variant"] for result in results] == [
        "with_pretokenizer_serial",
        "without_pretokenizer_serial",
        "with_pretokenizer_parallel",
        "without_pretokenizer_parallel",
    ]
    assert all(result["phase"] == "train" for result in results)
    assert all(result["training"]["merge_count"] > 0 for result in results)
    assert results[0]["training"]["initial_word_count"] >= results[1]["training"]["initial_word_count"]


def test_run_benchmark_includes_train_and_encode_phases(tmp_path) -> None:
    config = CpuBenchmarkConfig(
        input_text="abc abc 123\n",
        context_lengths=[16],
        repeats=1,
        parallel_workers=2,
        parallel_backend="thread",
        chunk_count=2,
        output_dir=tmp_path,
        train_vocab_size=270,
        train_input_limit=64,
    )

    payload = run_benchmark(config)
    phases = {result["phase"] for result in payload["results"]}

    assert phases == {"train", "encode"}
    assert len([item for item in payload["results"] if item["phase"] == "train"]) == 4
    assert len([item for item in payload["results"] if item["phase"] == "encode"]) == 4
