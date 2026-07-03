from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cs336_basics.tokenizer import TokenizerNoRegex, TokenizerWithRegex, train


DEFAULT_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "tinystories_sample_5M.txt"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"
DEFAULT_SPECIAL_TOKENS = ["<|endoftext|>"]


def token_bytes_to_display(token: bytes) -> str:
    return token.decode("utf-8", errors="replace")


def serialize_vocab(vocab: dict[int, bytes]) -> dict[str, str]:
    return {str(token_id): token_bytes_to_display(token) for token_id, token in vocab.items()}


def serialize_merge(pair: tuple[bytes, bytes]) -> list[str]:
    return [token_bytes_to_display(pair[0]), token_bytes_to_display(pair[1])]


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_merges(path: Path, merges: list[tuple[bytes, bytes]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(serialize_merge(pair)) for pair in merges]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def train_variant(
    input_path: Path,
    vocab_size: int,
    special_tokens: list[str],
    use_pretokenization: bool,
) -> tuple[dict[int, bytes], list[tuple[bytes, bytes]], float]:
    start = time.perf_counter()
    vocab, merges = train(
        input_path=input_path,
        vocab_size=vocab_size,
        special_tokens=special_tokens,
        use_pretokenization=use_pretokenization,
    )
    return vocab, merges, time.perf_counter() - start


def compare_tokenizer_artifacts(
    vocab_with_regex: dict[int, bytes],
    merges_with_regex: list[tuple[bytes, bytes]],
    vocab_no_regex: dict[int, bytes],
    merges_no_regex: list[tuple[bytes, bytes]],
    top_k: int = 25,
) -> dict[str, object]:
    with_regex_tokens = set(vocab_with_regex.values())
    no_regex_tokens = set(vocab_no_regex.values())
    with_regex_merges = set(merges_with_regex)
    no_regex_merges = set(merges_no_regex)

    only_with_regex_tokens = sorted(with_regex_tokens - no_regex_tokens, key=lambda token: (len(token), token))
    only_no_regex_tokens = sorted(no_regex_tokens - with_regex_tokens, key=lambda token: (len(token), token))
    only_with_regex_merges = sorted(with_regex_merges - no_regex_merges, key=lambda pair: (pair[0], pair[1]))
    only_no_regex_merges = sorted(no_regex_merges - with_regex_merges, key=lambda pair: (pair[0], pair[1]))

    return {
        "vocab_size": {
            "with_regex": len(vocab_with_regex),
            "without_regex": len(vocab_no_regex),
        },
        "merge_count": {
            "with_regex": len(merges_with_regex),
            "without_regex": len(merges_no_regex),
        },
        "shared_vocab_tokens": len(with_regex_tokens & no_regex_tokens),
        "only_with_regex_vocab_tokens": [token_bytes_to_display(token) for token in only_with_regex_tokens[:top_k]],
        "only_without_regex_vocab_tokens": [token_bytes_to_display(token) for token in only_no_regex_tokens[:top_k]],
        "shared_merges": len(with_regex_merges & no_regex_merges),
        "only_with_regex_merges": [serialize_merge(pair) for pair in only_with_regex_merges[:top_k]],
        "only_without_regex_merges": [serialize_merge(pair) for pair in only_no_regex_merges[:top_k]],
    }


def timed_call(fn, repeats: int) -> tuple[object, list[float]]:
    result = None
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        timings.append(time.perf_counter() - start)
    return result, timings


def summarize_timings(timings: Iterable[float]) -> dict[str, float]:
    values = list(timings)
    return {
        "min_s": min(values),
        "median_s": statistics.median(values),
        "mean_s": statistics.fmean(values),
    }


def benchmark_tokenizer(name: str, tokenizer, text: str, repeats: int) -> dict[str, object]:
    ids, encode_timings = timed_call(lambda: tokenizer.encode(text), repeats)
    decoded, decode_timings = timed_call(lambda: tokenizer.decode(ids), repeats)
    token_count = len(ids)
    byte_count = len(text.encode("utf-8"))

    return {
        "name": name,
        "char_count": len(text),
        "byte_count": byte_count,
        "token_count": token_count,
        "bytes_per_token": byte_count / token_count if token_count else 0.0,
        "encode": summarize_timings(encode_timings),
        "decode": summarize_timings(decode_timings),
        "roundtrip_ok": decoded == text,
    }


def benchmark_long_contexts(
    text: str,
    vocab_with_regex: dict[int, bytes],
    merges_with_regex: list[tuple[bytes, bytes]],
    vocab_no_regex: dict[int, bytes],
    merges_no_regex: list[tuple[bytes, bytes]],
    context_lengths: list[int],
    repeats: int,
) -> list[dict[str, object]]:
    tokenizers = [
        ("with_regex", TokenizerWithRegex(vocab_with_regex, merges_with_regex, DEFAULT_SPECIAL_TOKENS)),
        ("without_regex", TokenizerNoRegex(vocab_no_regex, merges_no_regex, DEFAULT_SPECIAL_TOKENS)),
    ]
    results = []
    for context_length in context_lengths:
        context = text[:context_length]
        row = {"context_chars": len(context), "variants": []}
        for name, tokenizer in tokenizers:
            row["variants"].append(benchmark_tokenizer(name, tokenizer, context, repeats))
        results.append(row)
    return results


def save_artifacts(
    output_dir: Path,
    vocab_with_regex: dict[int, bytes],
    merges_with_regex: list[tuple[bytes, bytes]],
    vocab_no_regex: dict[int, bytes],
    merges_no_regex: list[tuple[bytes, bytes]],
) -> None:
    write_json(output_dir / "vocab_with_regex.json", serialize_vocab(vocab_with_regex))
    write_json(output_dir / "vocab_without_regex.json", serialize_vocab(vocab_no_regex))
    write_merges(output_dir / "merges_with_regex.txt", merges_with_regex)
    write_merges(output_dir / "merges_without_regex.txt", merges_no_regex)


def format_seconds(value: float) -> str:
    return f"{value:.4f}s"


def print_benchmark_summary(results: list[dict[str, object]]) -> None:
    print("\nLong-context encode/decode benchmark")
    print("context_chars\tvariant\ttokens\tbytes/token\tencode_median\tdecode_median\troundtrip")
    for row in results:
        for variant in row["variants"]:
            print(
                "\t".join(
                    [
                        str(row["context_chars"]),
                        variant["name"],
                        str(variant["token_count"]),
                        f"{variant['bytes_per_token']:.3f}",
                        format_seconds(variant["encode"]["median_s"]),
                        format_seconds(variant["decode"]["median_s"]),
                        str(variant["roundtrip_ok"]),
                    ]
                )
            )


def parse_context_lengths(raw_lengths: str) -> list[int]:
    return [int(item) for item in raw_lengths.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare BPE training and long-context encoding with and without regex pre-tokenization."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--vocab-size", type=int, default=1000)
    parser.add_argument("--context-lengths", default="4096,16384,65536,262144")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context_lengths = parse_context_lengths(args.context_lengths)
    text = args.input.read_text(encoding="utf-8")

    print(f"Input: {args.input}")
    print(f"Output: {args.output_dir}")
    print(f"Vocab size: {args.vocab_size}")

    vocab_with_regex, merges_with_regex, train_with_regex_s = train_variant(
        args.input,
        args.vocab_size,
        DEFAULT_SPECIAL_TOKENS,
        use_pretokenization=True,
    )
    vocab_no_regex, merges_no_regex, train_no_regex_s = train_variant(
        args.input,
        args.vocab_size,
        DEFAULT_SPECIAL_TOKENS,
        use_pretokenization=False,
    )

    save_artifacts(
        args.output_dir,
        vocab_with_regex,
        merges_with_regex,
        vocab_no_regex,
        merges_no_regex,
    )

    comparison = compare_tokenizer_artifacts(
        vocab_with_regex,
        merges_with_regex,
        vocab_no_regex,
        merges_no_regex,
        top_k=args.top_k,
    )
    comparison["training_time_s"] = {
        "with_regex": train_with_regex_s,
        "without_regex": train_no_regex_s,
    }
    write_json(args.output_dir / "comparison.json", comparison)

    benchmarks = benchmark_long_contexts(
        text,
        vocab_with_regex,
        merges_with_regex,
        vocab_no_regex,
        merges_no_regex,
        context_lengths,
        repeats=args.repeats,
    )
    write_json(args.output_dir / "long_context_benchmark.json", benchmarks)

    print("\nTraining time")
    print(f"with_regex\t{format_seconds(train_with_regex_s)}")
    print(f"without_regex\t{format_seconds(train_no_regex_s)}")
    print_benchmark_summary(benchmarks)
    print(f"\nSaved artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
