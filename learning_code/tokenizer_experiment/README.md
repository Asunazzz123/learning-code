# Tokenizer Parallelization Experiment

This is an independent research scaffold for tokenizer CPU/GPU experiments. It is inspired by
CS336 assignment questions about byte-level tokenization and pretokenization, but it does not
import or copy assignment code.

The first milestone focuses on the experiment harness:

- with regex-compiled pretokenizer, without parallel execution
- without pretokenizer, without parallel execution
- with regex-compiled pretokenizer, with parallel execution
- without pretokenizer, with parallel execution

The CPU backend now has two baseline phases:

- `train`: a small reference BPE training workload that measures pretokenization, word-count
  construction, and merge-loop cost.
- `encode`: an artifact-driven encoding workload that measures long-context encoding with the
  training artifact produced by the same variant.

This is still a research benchmark scaffold, not a production tokenizer. GPU directories are
reserved for later CUDA and cuDF baselines.

## Quick Start

Run the smoke benchmark:

```sh
conda run -n agent python -m tokenizer_experiment.benchmarks.run_cpu \
  --config experiments/configs/smoke.json
```

Run tests:

```sh
conda run -n agent python -m pytest
```

Outputs are written under `results/` by default:

- `cpu_baseline.json`
- `cpu_baseline.csv`
- `cpu_benchmark.json`
- `cpu_benchmark.csv`

`cpu_benchmark.*` is kept as a compatibility alias for the earlier smoke output. Prefer
`cpu_baseline.*` for new analysis.

The smoke config uses the thread backend so it works in restricted local sandboxes. For real CPU
parallelism on a normal workstation, pass `--parallel-backend process`.

Useful CPU options:

```sh
conda run -n agent python -B -m tokenizer_experiment.benchmarks.run_cpu \
  --config experiments/configs/smoke.json \
  --train-vocab-size 512 \
  --train-input-limit 65536 \
  --context-lengths 4096,16384,65536 \
  --parallel-workers 8 \
  --parallel-backend process
```

## Project Layout

- `tokenizer_experiment/core/`: shared experiment variants, chunking, timing, and result types
- `tokenizer_experiment/cpu/`: CPU reference backend for the four experiment variants
- `tokenizer_experiment/benchmarks/`: command-line benchmark entry points
- `tokenizer_experiment/analysis/`: helpers for compact summaries and CSV output
- `experiments/configs/`: reproducible experiment configs
- `gpu/cuda/`: future custom CUDA tokenizer kernels
- `gpu/cudf/`: future RAPIDS/cuDF regex and string baselines
- `data/`: local corpora, intentionally not populated by default
- `results/`: generated benchmark outputs

## Notes

For real GPU tokenizer work, keep pretokenization and BPE merge experiments separate at first.
Regex compatibility, host/device transfer overhead, and parallel merge scheduling are distinct
sources of performance behavior.
