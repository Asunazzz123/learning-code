from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tokenizer_experiment.analysis.io import flatten_results, write_csv, write_json
from tokenizer_experiment.core.chunking import make_contexts
from tokenizer_experiment.core.variants import ALL_VARIANTS
from tokenizer_experiment.cpu.baseline import (
    run_encoding_baseline,
    run_training_baseline,
    strip_runtime_objects,
)


DEFAULT_CONFIG = Path("experiments/configs/smoke.json")


@dataclass(frozen=True)
class CpuBenchmarkConfig:
    input_text: str
    context_lengths: list[int]
    repeats: int
    parallel_workers: int
    parallel_backend: str
    chunk_count: int
    output_dir: Path
    train_vocab_size: int
    train_input_limit: int | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CPU tokenizer parallelization benchmarks.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--input-path", type=Path)
    parser.add_argument("--context-lengths")
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--parallel-workers", type=int)
    parser.add_argument("--parallel-backend", choices=["process", "thread"])
    parser.add_argument("--chunk-count", type=int)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--train-vocab-size", type=int)
    parser.add_argument("--train-input-limit", type=int)
    return parser.parse_args()


def load_config(args: argparse.Namespace) -> CpuBenchmarkConfig:
    raw = _load_json(args.config)
    input_text = _read_input_text(args.input_path, raw)
    context_lengths = _parse_context_lengths(args.context_lengths, raw["context_lengths"])
    repeats = args.repeats if args.repeats is not None else int(raw["repeats"])
    parallel_workers = (
        args.parallel_workers if args.parallel_workers is not None else int(raw["parallel_workers"])
    )
    parallel_backend = args.parallel_backend or str(raw.get("parallel_backend", "process"))
    chunk_count = args.chunk_count if args.chunk_count is not None else int(raw["chunk_count"])
    output_dir = args.output_dir if args.output_dir is not None else Path(raw["output_dir"])
    train_vocab_size = (
        args.train_vocab_size if args.train_vocab_size is not None else int(raw["train_vocab_size"])
    )
    train_input_limit = (
        args.train_input_limit
        if args.train_input_limit is not None
        else _optional_int(raw.get("train_input_limit"))
    )

    return CpuBenchmarkConfig(
        input_text=input_text,
        context_lengths=context_lengths,
        repeats=repeats,
        parallel_workers=parallel_workers,
        parallel_backend=parallel_backend,
        chunk_count=chunk_count,
        output_dir=output_dir,
        train_vocab_size=train_vocab_size,
        train_input_limit=train_input_limit,
    )


def run_benchmark(config: CpuBenchmarkConfig) -> dict[str, Any]:
    contexts = make_contexts(config.input_text, config.context_lengths)
    train_text = _limit_text(config.input_text, config.train_input_limit)
    results: list[dict[str, Any]] = []

    for variant in ALL_VARIANTS:
        training_result = run_training_baseline(
            variant=variant,
            text=train_text,
            vocab_size=config.train_vocab_size,
            repeats=config.repeats,
            parallel_workers=config.parallel_workers,
            parallel_backend=config.parallel_backend,
            chunk_count=config.chunk_count,
        )
        artifact = training_result["artifact"]
        results.append(strip_runtime_objects(training_result))

        for context in contexts:
            result = run_encoding_baseline(
                variant=variant,
                text=context,
                artifact=artifact,
                repeats=config.repeats,
                parallel_workers=config.parallel_workers,
                parallel_backend=config.parallel_backend,
                chunk_count=config.chunk_count,
            )
            results.append(result)

    return {
        "backend": "cpu_reference_bpe",
        "config": _config_to_dict(config),
        "results": results,
    }


def main() -> None:
    args = parse_args()
    config = load_config(args)
    payload = run_benchmark(config)
    rows = flatten_results(payload["results"])

    write_json(config.output_dir / "cpu_baseline.json", payload)
    write_csv(config.output_dir / "cpu_baseline.csv", rows)
    write_json(config.output_dir / "cpu_benchmark.json", payload)
    write_csv(config.output_dir / "cpu_benchmark.csv", rows)
    _print_summary(rows)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_input_text(input_path: Path | None, raw_config: dict[str, Any]) -> str:
    if input_path is not None:
        return input_path.read_text(encoding="utf-8")
    if "input_path" in raw_config:
        return Path(raw_config["input_path"]).read_text(encoding="utf-8")
    return str(raw_config["input_text"])


def _parse_context_lengths(raw_arg: str | None, default: list[int]) -> list[int]:
    if raw_arg is None:
        return [int(item) for item in default]
    return [int(item.strip()) for item in raw_arg.split(",") if item.strip()]


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _limit_text(text: str, limit: int | None) -> str:
    if limit is None:
        return text
    if limit <= 0:
        raise ValueError(f"train_input_limit must be positive, got {limit}")
    return text[:limit]


def _config_to_dict(config: CpuBenchmarkConfig) -> dict[str, Any]:
    return {
        "context_lengths": config.context_lengths,
        "repeats": config.repeats,
        "parallel_workers": config.parallel_workers,
        "parallel_backend": config.parallel_backend,
        "chunk_count": config.chunk_count,
        "output_dir": str(config.output_dir),
        "train_vocab_size": config.train_vocab_size,
        "train_input_limit": config.train_input_limit,
    }


def _print_summary(rows: list[dict[str, Any]]) -> None:
    print("phase\tvariant\tcontext_chars\tmedian_s\tbytes/s\tspans")
    for row in rows:
        print(
            "\t".join(
                [
                    row["phase"],
                    row["variant"],
                    str(row["context_chars"]),
                    f"{row['median_s']:.6f}",
                    f"{row['bytes_per_median_s']:.2f}",
                    str(row["span_count"]),
                ]
            )
        )


if __name__ == "__main__":
    main()
