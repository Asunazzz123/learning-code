# BPE Pre-Tokenization Experiment

This folder compares BPE training and long-context encode/decode performance
with and without GPT-2 regex pre-tokenization.

Run a quick smoke test:

```sh
conda run -n agent python bpe_pretok_experiments/run_experiment.py \
  --vocab-size 300 \
  --context-lengths 1024,4096 \
  --repeats 1 \
  --output-dir bpe_pretok_experiments/results_smoke
```

Run the default experiment on `tests/fixtures/tinystories_sample_5M.txt`:

```sh
conda run -n agent python bpe_pretok_experiments/run_experiment.py
```

Outputs:

- `vocab_with_regex.json`
- `vocab_without_regex.json`
- `merges_with_regex.txt`
- `merges_without_regex.txt`
- `comparison.json`
- `long_context_benchmark.json`
