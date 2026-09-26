# Small MLP benchmark

Validation-selected learning rates; mean ± sample std over seeds.

| Method | LR | Test accuracy | Test CE | Training seconds | Orthogonality error |
|---|---:|---:|---:|---:|---:|
| sgd | 0.2 | 88.9974 ± 1.5787% | 0.2709 ± 0.0315 | 0.0223 ± 0.0029 | 1.86e+00 |
| riemannian_sgd | 0.2 | 85.7422 ± 1.7027% | 0.4717 ± 0.0153 | 0.0387 ± 0.0120 | 4.74e-07 |
| msign | 0.05 | 85.7422 ± 2.0391% | 0.4796 ± 0.0180 | 0.6483 ± 0.0395 | 4.32e-07 |
| adam | 0.02 | 89.3229 ± 1.8148% | 0.2751 ± 0.0200 | 0.0407 ± 0.0057 | 2.49e+00 |
| muon | 0.01 | 88.2812 ± 1.0335% | 0.2919 ± 0.0296 | 0.0423 ± 0.0003 | 1.75e+00 |

Synthetic teacher classification, 16→8→4 tanh MLP (172 parameters).
Train/validation/test: 1024/512/512. Identical initialization and batch order per seed.
CPU, float32, one thread. Time includes forward/backward/optimizer, excludes evaluation and initialization.
SGD is unconstrained. Riemannian SGD and msign constrain both weight matrices; biases use SGD.
Adam updates all parameters. Muon updates both matrices; Adam updates biases at 0.1 × Muon LR.
Muon: torch.optim.Muon, momentum=0.95, Nesterov, 5 Newton–Schulz steps, original LR scaling.
All methods use zero weight decay; Adam and Muon do not constrain weight orthogonality.
LR grids: Adam=[0.001, 0.005, 0.02]; other methods=[0.01, 0.05, 0.2]. Each optimizer is independently warmed up.
Synthetic results and this finite LR grid do not establish general optimizer superiority.

Selected msign inner-loop diagnostics (last batch of each epoch, both matrices):
- Seed 0: mean iterations=20.00, statuses={'max_iter': 40}, mean tangent residual=1.957e-02
- Seed 1: mean iterations=20.00, statuses={'max_iter': 40}, mean tangent residual=2.253e-02
- Seed 2: mean iterations=20.00, statuses={'max_iter': 40}, mean tangent residual=2.117e-02
Reaching max_iter means the inner loop has not met its convergence criterion.
