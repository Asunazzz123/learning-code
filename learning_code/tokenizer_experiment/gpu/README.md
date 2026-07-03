# GPU Backends

GPU experiments are intentionally separated from the CPU benchmark harness.

Suggested milestones:

1. cuDF regex baseline: measure supported regex pretokenization operations and host/device
   transfer overhead separately.
2. CUDA byte-workload baseline: port the deterministic byte workload used by the CPU harness.
3. CUDA BPE merge prototype: test pair lookup, rank reduction, and compaction independently from
   regex pretokenization.

Keep each GPU benchmark compatible with the same four variant names used by the CPU harness.
