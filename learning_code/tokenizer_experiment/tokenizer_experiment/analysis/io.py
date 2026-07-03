from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def flatten_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        timings = result["timings"]
        base = {
            "phase": result.get("phase", "workload"),
            "variant": result["variant"],
            "context_chars": result["context_chars"],
            "repeats": result["repeats"],
            "parallel_workers": result["parallel_workers"],
            "parallel_backend": result["parallel_backend"],
            "chunk_count": result["chunk_count"],
            "min_s": timings["min_s"],
            "median_s": timings["median_s"],
            "mean_s": timings["mean_s"],
        }
        if result.get("phase") == "train":
            training = result["training"]
            byte_count = training["byte_count"]
            rows.append(
                {
                    **base,
                    "span_count": training["span_count"],
                    "byte_count": byte_count,
                    "token_count": "",
                    "checksum": "",
                    "bytes_per_token": "",
                    "merge_count": training["merge_count"],
                    "vocab_size": training["vocab_size"],
                    "initial_word_count": training["initial_word_count"],
                    "bytes_per_median_s": _safe_rate(byte_count, timings["median_s"]),
                    "tokens_per_median_s": "",
                }
            )
        elif result.get("phase") == "encode":
            encoding = result["encoding"]
            rows.append(
                {
                    **base,
                    "span_count": encoding["span_count"],
                    "byte_count": encoding["byte_count"],
                    "token_count": encoding["token_count"],
                    "checksum": encoding["checksum"],
                    "bytes_per_token": encoding["bytes_per_token"],
                    "merge_count": "",
                    "vocab_size": "",
                    "initial_word_count": "",
                    "bytes_per_median_s": _safe_rate(encoding["byte_count"], timings["median_s"]),
                    "tokens_per_median_s": _safe_rate(encoding["token_count"], timings["median_s"]),
                }
            )
        else:
            stats = result["stats"]
            rows.append(
                {
                    **base,
                    "span_count": stats["span_count"],
                    "byte_count": stats["byte_count"],
                    "token_count": stats["token_count"],
                    "checksum": stats["checksum"],
                    "bytes_per_token": "",
                    "merge_count": "",
                    "vocab_size": "",
                    "initial_word_count": "",
                    "bytes_per_median_s": _safe_rate(stats["byte_count"], timings["median_s"]),
                    "tokens_per_median_s": _safe_rate(stats["token_count"], timings["median_s"]),
                }
            )
    return rows


def _safe_rate(numerator: int, seconds: float) -> float:
    return numerator / seconds if seconds > 0 else 0.0
