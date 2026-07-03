from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


Token = bytes
Word = tuple[Token, ...]
Merge = tuple[Token, Token]


@dataclass(frozen=True)
class ReferenceBpeArtifact:
    vocab_size: int
    merges: tuple[Merge, ...]
    word_count: int
    span_count: int
    byte_count: int

    @property
    def merge_ranks(self) -> dict[Merge, int]:
        return {merge: rank for rank, merge in enumerate(self.merges)}


def train_reference_bpe(spans: list[str], vocab_size: int) -> ReferenceBpeArtifact:
    if vocab_size < 256:
        raise ValueError(f"vocab_size must be at least 256, got {vocab_size}")

    word_counts = build_word_counts(spans)
    target_merges = vocab_size - 256
    merges: list[Merge] = []

    for _ in range(target_merges):
        pair_counts = count_pairs(word_counts)
        if not pair_counts:
            break
        best_pair = max(pair_counts.items(), key=lambda item: (item[1], item[0]))[0]
        merges.append(best_pair)
        word_counts = merge_pair_in_counts(word_counts, best_pair)

    return ReferenceBpeArtifact(
        vocab_size=256 + len(merges),
        merges=tuple(merges),
        word_count=len(word_counts),
        span_count=len(spans),
        byte_count=sum(len(span.encode("utf-8")) for span in spans),
    )


def build_word_counts(spans: list[str]) -> Counter[Word]:
    counts: Counter[Word] = Counter()
    for span in spans:
        raw = span.encode("utf-8")
        if raw:
            counts[tuple(bytes([byte]) for byte in raw)] += 1
    return counts


def merge_word_counts(items: list[Counter[Word]]) -> Counter[Word]:
    merged: Counter[Word] = Counter()
    for item in items:
        merged.update(item)
    return merged


def train_from_word_counts(word_counts: Counter[Word], span_count: int, vocab_size: int) -> ReferenceBpeArtifact:
    if vocab_size < 256:
        raise ValueError(f"vocab_size must be at least 256, got {vocab_size}")

    current = word_counts.copy()
    merges: list[Merge] = []
    for _ in range(vocab_size - 256):
        pair_counts = count_pairs(current)
        if not pair_counts:
            break
        best_pair = max(pair_counts.items(), key=lambda item: (item[1], item[0]))[0]
        merges.append(best_pair)
        current = merge_pair_in_counts(current, best_pair)

    return ReferenceBpeArtifact(
        vocab_size=256 + len(merges),
        merges=tuple(merges),
        word_count=len(current),
        span_count=span_count,
        byte_count=sum(sum(len(token) for token in word) * count for word, count in word_counts.items()),
    )


def count_pairs(word_counts: Counter[Word]) -> Counter[Merge]:
    pair_counts: Counter[Merge] = Counter()
    for word, count in word_counts.items():
        for pair in zip(word, word[1:], strict=False):
            pair_counts[pair] += count
    return pair_counts


def merge_pair_in_counts(word_counts: Counter[Word], pair_to_merge: Merge) -> Counter[Word]:
    merged_counts: Counter[Word] = Counter()
    new_token = pair_to_merge[0] + pair_to_merge[1]
    for word, count in word_counts.items():
        merged_counts[_merge_word(word, pair_to_merge, new_token)] += count
    return merged_counts


def encode_spans(spans: list[str], artifact: ReferenceBpeArtifact) -> list[Token]:
    merge_ranks = artifact.merge_ranks
    tokens: list[Token] = []
    for span in spans:
        tokens.extend(_encode_bytes(span.encode("utf-8"), merge_ranks))
    return tokens


def _encode_bytes(raw: bytes, merge_ranks: dict[Merge, int]) -> list[Token]:
    tokens = [bytes([byte]) for byte in raw]
    while len(tokens) >= 2:
        ranked_pairs = [
            ((tokens[index], tokens[index + 1]), merge_ranks[(tokens[index], tokens[index + 1])])
            for index in range(len(tokens) - 1)
            if (tokens[index], tokens[index + 1]) in merge_ranks
        ]
        if not ranked_pairs:
            break
        best_pair = min(ranked_pairs, key=lambda item: item[1])[0]
        tokens = list(_merge_word(tuple(tokens), best_pair, best_pair[0] + best_pair[1]))
    return tokens


def _merge_word(word: Word, pair_to_merge: Merge, new_token: Token) -> Word:
    output: list[Token] = []
    index = 0
    while index < len(word):
        if index < len(word) - 1 and (word[index], word[index + 1]) == pair_to_merge:
            output.append(new_token)
            index += 2
        else:
            output.append(word[index])
            index += 1
    return tuple(output)
