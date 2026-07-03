import json

from tokenizer_experiment.benchmarks.run_cpu import CpuBenchmarkConfig, run_benchmark


def test_run_benchmark_returns_serializable_results(tmp_path) -> None:
    config = CpuBenchmarkConfig(
        input_text="abc 123\n",
        context_lengths=[8, 32],
        repeats=1,
        parallel_workers=2,
        parallel_backend="thread",
        chunk_count=2,
        output_dir=tmp_path,
        train_vocab_size=270,
        train_input_limit=32,
    )

    payload = run_benchmark(config)
    results = payload["results"]

    assert payload["backend"] == "cpu_reference_bpe"
    assert len(results) == 12
    assert {result["phase"] for result in results} == {"train", "encode"}
    assert {result["context_chars"] for result in results} == {8, 32}
    json.dumps(payload)
