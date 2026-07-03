from tokenizer_experiment.core.variants import variant_names


def test_variant_matrix_names_are_stable() -> None:
    assert variant_names() == [
        "with_pretokenizer_serial",
        "without_pretokenizer_serial",
        "with_pretokenizer_parallel",
        "without_pretokenizer_parallel",
    ]
