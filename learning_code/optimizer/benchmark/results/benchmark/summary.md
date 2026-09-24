# Small MLP benchmark

Validation-selected learning rates; mean ± sample std over seeds.

| Method | LR | Test accuracy | Test CE | Training seconds | Orthogonality error |
|---|---:|---:|---:|---:|---:|
| sgd | 0.2 | 88.9974 ± 1.5787% | 0.2709 ± 0.0315 | 0.0151 ± 0.0004 | 1.86e+00 |
| riemannian_sgd | 0.2 | 85.7422 ± 1.7027% | 0.4717 ± 0.0153 | 0.0238 ± 0.0001 | 4.74e-07 |
| msign | 0.05 | 85.7422 ± 2.0391% | 0.4796 ± 0.0180 | 0.2872 ± 0.0031 | 5.55e-07 |

Synthetic teacher classification, 16→8→4 tanh MLP (172 parameters).
Train/validation/test: 1024/512/512. Identical initialization and batch order per seed.
CPU, float32, one thread. Time includes forward/backward/optimizer, excludes evaluation and initialization.
SGD is unconstrained. Riemannian SGD and msign constrain both weight matrices; biases use SGD.
Synthetic results and this finite LR grid do not establish general optimizer superiority.

Selected msign inner-loop diagnostics (last batch of each epoch, both matrices):
- Seed 0: mean iterations=20.00, statuses={'max_iter': 40}
- Seed 1: mean iterations=20.00, statuses={'max_iter': 40}
- Seed 2: mean iterations=20.00, statuses={'max_iter': 40}
Reaching max_iter means the inner loop has not met its convergence criterion.
