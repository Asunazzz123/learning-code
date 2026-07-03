from __future__ import annotations


def make_contexts(text: str, context_lengths: list[int]) -> list[str]:
    if not text:
        raise ValueError("input text is empty")
    contexts: list[str] = []
    for length in context_lengths:
        if length <= 0:
            raise ValueError(f"context length must be positive, got {length}")
        if length <= len(text):
            contexts.append(text[:length])
        else:
            repeats = (length // len(text)) + 1
            contexts.append((text * repeats)[:length])
    return contexts


def split_text_for_workers(text: str, chunk_count: int) -> list[str]:
    if chunk_count <= 1 or len(text) <= 1:
        return [text]

    chunk_count = min(chunk_count, len(text))
    boundaries = [0]

    for index in range(1, chunk_count):
        proposed = (len(text) * index) // chunk_count
        lower = boundaries[-1] + 1
        upper = len(text) - (chunk_count - index)
        boundaries.append(_nearest_soft_boundary(text, proposed, lower, upper))

    boundaries.append(len(text))
    return [
        text[start:end]
        for start, end in zip(boundaries[:-1], boundaries[1:], strict=True)
        if start < end
    ]


def _nearest_soft_boundary(text: str, proposed: int, lower: int, upper: int) -> int:
    proposed = min(max(proposed, lower), upper)
    for delta in range(65):
        for candidate in (proposed - delta, proposed + delta):
            if lower <= candidate <= upper and text[candidate - 1].isspace():
                return candidate
    return proposed
