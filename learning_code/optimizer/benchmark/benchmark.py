"""Reproducible CPU benchmark; no dataset downloads or extra ML packages."""

import argparse
import copy
import json
import math
import platform
import statistics
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

from stiefel_msign import StiefelMsign, msign, project_tangent

METHODS = ("sgd", "riemannian_sgd", "msign", "adam", "muon")


def make_optimizers(model, method, lr, max_iter):
    if method == "msign":
        return [StiefelMsign(model.matrices(), lr=lr, max_iter=max_iter),
                torch.optim.SGD([model.b1, model.b2], lr=lr)]
    if method == "adam":
        return [torch.optim.Adam(model.parameters(), lr=lr, weight_decay=0)]
    if method == "muon":
        return [torch.optim.Muon(model.matrices(), lr=lr, weight_decay=0,
                                 momentum=0.95, nesterov=True, ns_steps=5,
                                 adjust_lr_fn="original"),
                torch.optim.Adam([model.b1, model.b2], lr=lr * 0.1, weight_decay=0)]
    if method in ("sgd", "riemannian_sgd"):
        return [torch.optim.SGD(model.parameters(), lr=lr)]
    raise ValueError(f"Unknown method: {method}")


class SmallMLP(nn.Module):
    def __init__(self):
        super().__init__()
        # Store weights as input x output so both are tall Stiefel matrices.
        self.w1 = nn.Parameter(msign(torch.randn(16, 8)))
        self.b1 = nn.Parameter(torch.zeros(8))
        self.w2 = nn.Parameter(msign(torch.randn(8, 4)))
        self.b2 = nn.Parameter(torch.zeros(4))

    def forward(self, x):
        return 3.0 * (torch.tanh(x @ self.w1 + self.b1) @ self.w2 + self.b2)

    def matrices(self):
        return [self.w1, self.w2]


def make_data():
    # Independent, fixed data and teacher for all initialization seeds.
    with torch.random.fork_rng():
        torch.manual_seed(2026)
        teacher = SmallMLP()
        x = torch.randn(2048, 16)
        with torch.no_grad():
            y = teacher(x).argmax(dim=1)
    return (x[:1024], y[:1024]), (x[1024:1536], y[1024:1536]), (x[1536:], y[1536:])


@torch.no_grad()
def evaluate(model, data):
    logits = model(data[0])
    return dict(loss=F.cross_entropy(logits, data[1]).item(),
                accuracy=(logits.argmax(1) == data[1]).float().mean().item())


@torch.no_grad()
def orthogonality_error(model):
    return max((w.T @ w - torch.eye(w.shape[1])).norm().item() / math.sqrt(w.shape[1])
               for w in model.matrices())


def train(method, lr, seed, data, args):
    torch.manual_seed(seed)
    model = SmallMLP()
    matrices = model.matrices()
    optimizers = make_optimizers(model, method, lr, args.max_iter)
    optimizer_config = [dict(type=type(opt).__name__, groups=[
        {k: v for k, v in group.items() if k != "params"}
        for group in opt.param_groups]) for opt in optimizers]
    # Same batch order at each epoch across methods and learning rates.
    generator = torch.Generator().manual_seed(seed + 10000)
    history = []
    elapsed = 0.0
    inner_iterations = []
    inner_residuals = []
    statuses = {}
    for epoch in range(args.epochs + 1):
        if epoch:
            order = torch.randperm(len(data[0][0]), generator=generator)
            start = time.perf_counter()
            for batch in order.split(args.batch_size):
                for opt in optimizers:
                    opt.zero_grad(set_to_none=True)
                loss = F.cross_entropy(model(data[0][0][batch]), data[0][1][batch])
                if not torch.isfinite(loss):
                    raise RuntimeError(f"Nonfinite loss: {method}, lr={lr}, seed={seed}")
                loss.backward()
                if method == "riemannian_sgd":
                    with torch.no_grad():
                        for w in matrices:
                            w.grad.copy_(project_tangent(w, w.grad))
                for opt in optimizers:
                    opt.step()
                if method == "riemannian_sgd":
                    with torch.no_grad():
                        for w in matrices:
                            w.copy_(msign(w))
            elapsed += time.perf_counter() - start
            # Diagnostics are sampled at the last batch of each epoch.
            if method == "msign":
                for w in matrices:
                    info = optimizers[0].state[w]["diagnostics"]
                    inner_iterations.append(info["iterations"])
                    inner_residuals.append(dict(epoch=epoch, matrix_shape=list(w.shape),
                                                **info))
                    statuses[info["status"]] = statuses.get(info["status"], 0) + 1
        history.append(dict(epoch=epoch, train_seconds=elapsed,
                            train=evaluate(model, data[0]), val=evaluate(model, data[1]),
                            orthogonality_error=orthogonality_error(model)))
    return dict(method=method, lr=lr, seed=seed, history=history, optimizer_config=optimizer_config,
                sampled_inner_iterations=statistics.mean(inner_iterations) if inner_iterations else None,
                sampled_statuses=statuses, sampled_inner_diagnostics=inner_residuals), copy.deepcopy(model.state_dict())


def plot_results(selected, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for method, runs in selected.items():
        count = len(runs[0]["history"])
        epochs = list(range(count))
        losses = [statistics.mean(r["history"][i]["train"]["loss"] for r in runs) for i in epochs]
        accuracies = [statistics.mean(r["history"][i]["val"]["accuracy"] for r in runs) for i in epochs]
        seconds = [statistics.mean(r["history"][i]["train_seconds"] for r in runs) for i in epochs]
        axes[0].plot(epochs, losses, label=method)
        axes[1].plot(epochs, accuracies, label=method)
        axes[2].plot(seconds, accuracies, label=method)
    for ax, xlabel, ylabel in zip(axes, ["Epoch", "Epoch", "Training seconds"],
                                  ["Train cross entropy", "Validation accuracy", "Validation accuracy"]):
        ax.set(xlabel=xlabel, ylabel=ylabel)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "curves.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--max-iter", type=int, default=20)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--lrs", type=float, nargs="+", default=[0.01, 0.05, 0.2])
    parser.add_argument("--adam-lrs", type=float, nargs="+", default=[0.001, 0.005, 0.02])
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results/benchmark_five_optimizers")
    args = parser.parse_args()
    if min(args.epochs, args.batch_size, args.max_iter) < 1:
        parser.error("epochs, batch-size and max-iter must be positive")
    if any(not math.isfinite(lr) or lr <= 0 for lr in args.lrs + args.adam_lrs):
        parser.error("learning rates must be finite and positive")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    args.output.mkdir(parents=True, exist_ok=True)
    data = make_data()
    trials, selected, summary = [], {}, {}
    for method in METHODS:
        learning_rates = args.adam_lrs if method == "adam" else args.lrs
        # Independent warmup for each optimizer, discarded from all results.
        warm_args = copy.copy(args)
        warm_args.epochs = 1
        train(method, learning_rates[0], 42, data, warm_args)
        candidates = []
        for lr in learning_rates:
            runs, states = [], []
            for seed in args.seeds:
                run, state = train(method, lr, seed, data, args)
                runs.append(run)
                states.append(state)
                print(f"{method:15s} lr={lr:g} seed={seed} "
                      f"val_acc={run['history'][-1]['val']['accuracy']:.3f} "
                      f"time={run['history'][-1]['train_seconds']:.2f}s", flush=True)
            candidates.append((statistics.mean(r["history"][-1]["val"]["loss"] for r in runs), lr, runs, states))
            trials.extend(runs)
        # Select one LR per method using mean final validation loss, never test.
        _, best_lr, best_runs, best_states = min(candidates, key=lambda c: c[0])
        selected[method] = best_runs
        for run, state in zip(best_runs, best_states):
            model = SmallMLP()
            model.load_state_dict(state)
            run["test"] = evaluate(model, data[2])
        def aggregate(values):
            return dict(mean=statistics.mean(values), std=statistics.stdev(values) if len(values) > 1 else 0.0)
        summary[method] = dict(lr=best_lr,
            test_accuracy=aggregate([r["test"]["accuracy"] for r in best_runs]),
            test_loss=aggregate([r["test"]["loss"] for r in best_runs]),
            train_seconds=aggregate([r["history"][-1]["train_seconds"] for r in best_runs]),
            orthogonality_error=aggregate([r["history"][-1]["orthogonality_error"] for r in best_runs]))
    result = dict(algorithm="D0=G; D_next=msign(P_X(D)); stop on change and both residuals",
                  config={**vars(args), "output": str(args.output)},
                  environment=dict(torch=torch.__version__, python=platform.python_version(),
                                   platform=platform.platform(), device="cpu", threads=1),
                  class_counts=[torch.bincount(part[1], minlength=4).tolist() for part in data],
                  summary=summary, trials=trials)
    (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Small MLP benchmark", "", "Validation-selected learning rates; mean ± sample std over seeds.", "",
             "| Method | LR | Test accuracy | Test CE | Training seconds | Orthogonality error |",
             "|---|---:|---:|---:|---:|---:|"]
    for method, values in summary.items():
        def fmt(key, factor=1):
            v = values[key]
            return f"{factor*v['mean']:.4f} ± {factor*v['std']:.4f}"
        lines.append(f"| {method} | {values['lr']} | {fmt('test_accuracy', 100)}% | "
                     f"{fmt('test_loss')} | {fmt('train_seconds')} | {values['orthogonality_error']['mean']:.2e} |")
    lines += ["", "Synthetic teacher classification, 16→8→4 tanh MLP (172 parameters).",
              "Train/validation/test: 1024/512/512. Identical initialization and batch order per seed.",
              "CPU, float32, one thread. Time includes forward/backward/optimizer, excludes evaluation and initialization.",
              "SGD is unconstrained. Riemannian SGD and msign constrain both weight matrices; biases use SGD.",
              "Adam updates all parameters. Muon updates both matrices; Adam updates biases at 0.1 × Muon LR.",
              "Muon: torch.optim.Muon, momentum=0.95, Nesterov, 5 Newton–Schulz steps, original LR scaling.",
              "All methods use zero weight decay; Adam and Muon do not constrain weight orthogonality.",
              f"LR grids: Adam={args.adam_lrs}; other methods={args.lrs}. Each optimizer is independently warmed up.",
              "Synthetic results and this finite LR grid do not establish general optimizer superiority."]
    lines += ["", "Selected msign inner-loop diagnostics (last batch of each epoch, both matrices):"]
    for run in selected["msign"]:
        lines.append(f"- Seed {run['seed']}: mean iterations={run['sampled_inner_iterations']:.2f}, "
                     f"statuses={run['sampled_statuses']}, "
                     f"mean tangent residual={statistics.mean(d['tangent_error'] for d in run['sampled_inner_diagnostics']):.3e}")
    lines.append("Reaching max_iter means the inner loop has not met its convergence criterion.")
    (args.output / "summary.md").write_text("\n".join(lines) + "\n")
    plot_results(selected, args.output)
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
