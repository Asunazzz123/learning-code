from __future__ import annotations

import regex


GPT2_LIKE_PRETOKEN_PATTERN = (
    r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
)

COMPILED_GPT2_LIKE_PRETOKEN_PATTERN = regex.compile(GPT2_LIKE_PRETOKEN_PATTERN)


class RegexPretokenizer:
    def __init__(self, pattern: str = GPT2_LIKE_PRETOKEN_PATTERN) -> None:
        self.pattern = pattern
        if pattern == GPT2_LIKE_PRETOKEN_PATTERN:
            self._compiled = COMPILED_GPT2_LIKE_PRETOKEN_PATTERN
        else:
            self._compiled = regex.compile(pattern)

    def split(self, text: str) -> list[str]:
        return [match.group() for match in self._compiled.finditer(text)]


def split_without_pretokenizer(text: str) -> list[str]:
    return [text] if text else []
