from tokenizer_experiment.core.chunking import make_contexts, split_text_for_workers


def test_make_contexts_repeats_short_input() -> None:
    assert make_contexts("abc", [2, 8]) == ["ab", "abcabcab"]


def test_split_text_for_workers_preserves_text() -> None:
    text = "hello tokenizer world " * 5
    chunks = split_text_for_workers(text, chunk_count=4)

    assert "".join(chunks) == text
    assert 1 < len(chunks) <= 4
