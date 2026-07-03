from __future__ import annotations

import json

from cs336_basics.tokenizer import TokenizerNoRegex, TokenizerWithRegex, train


def test_train_can_disable_regex_pretokenization(tmp_path):
    corpus_path = tmp_path / "toy.txt"
    corpus_path.write_text("aa aa", encoding="utf-8")

    vocab_with_regex, merges_with_regex = train(
        corpus_path,
        vocab_size=258,
        special_tokens=[],
        use_pretokenization=True,
    )
    vocab_no_regex, merges_no_regex = train(
        corpus_path,
        vocab_size=258,
        special_tokens=[],
        use_pretokenization=False,
    )

    assert merges_with_regex == [(b"a", b"a"), (b" ", b"aa")]
    assert merges_no_regex == [(b"a", b"a"), (b"aa", b" ")]
    assert b"aa " in vocab_no_regex.values()
    assert b"aa " not in vocab_with_regex.values()


def test_experiment_helpers_return_serializable_comparison(tmp_path):
    from bpe_pretok_experiments.run_experiment import (
        benchmark_tokenizer,
        compare_tokenizer_artifacts,
    )

    text = "a1 a1 a1"
    vocab_with_regex = {0: b"a", 1: b"1", 2: b" ", 3: b"a1"}
    merges_with_regex = [(b"a", b"1")]
    vocab_no_regex = {0: b"a", 1: b"1", 2: b" ", 3: b"a1", 4: b"a1 "}
    merges_no_regex = [(b"a", b"1"), (b"a1", b" ")]

    comparison = compare_tokenizer_artifacts(
        vocab_with_regex,
        merges_with_regex,
        vocab_no_regex,
        merges_no_regex,
        top_k=5,
    )
    benchmark = benchmark_tokenizer(
        "with_regex",
        TokenizerWithRegex(vocab_with_regex, merges_with_regex),
        text,
        repeats=1,
    )

    assert comparison["merge_count"]["with_regex"] == 1
    assert comparison["merge_count"]["without_regex"] == 2
    assert comparison["shared_vocab_tokens"] == 4
    assert benchmark["roundtrip_ok"] is True
    assert benchmark["token_count"] == 8
    json.dumps({"comparison": comparison, "benchmark": benchmark})
