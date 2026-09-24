"""Alternating polar/tangent projections and a Stiefel-constrained optimizer."""

import math

import torch
from torch import Tensor
from torch.optim import Optimizer


def _check_matrix(x: Tensor) -> None:
    if x.ndim != 2 or x.shape[0] < x.shape[1] or x.shape[1] == 0:
        raise ValueError("Expected a nonempty matrix with rows >= columns")
    if x.dtype not in (torch.float32, torch.float64):
        raise TypeError("Only real float32 and float64 matrices are supported")
    if not torch.isfinite(x).all():
        raise ValueError("Matrix must be finite")


def msign(a: Tensor) -> Tensor:
    """Return U @ Vh: a nearest column-orthogonal matrix in Frobenius norm.

    At deficient rank the orthogonal completion is nonunique. This is the
    full polar completion, not the partial isometry that sets sign(0) = 0.
    """
    _check_matrix(a)
    u, _, vh = torch.linalg.svd(a, full_matrices=False)
    return u @ vh


def project_tangent(x: Tensor, g: Tensor) -> Tensor:
    """Frobenius projection P_X(G); assumes X.T @ X = I."""
    xtg = x.T @ g
    return g - x @ ((xtg + xtg.T) * 0.5)


def _validate_options(max_iter: int, tol: float) -> None:
    if isinstance(max_iter, bool) or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be finite and positive")


@torch.no_grad()
def alternating_direction(
    x: Tensor, g: Tensor, *, max_iter: int = 100, tol: float = 1e-6
) -> tuple[Tensor, dict]:
    """Start at G, then repeat msign(P_X(D)) with X fixed.

    Except for a zero tangent gradient, returns a column-orthogonal direction.
    `converged` requires small iterate change and both constraint residuals.
    A truncated result may not lie in the tangent space. Small iterate change
    alone does not stop the loop or imply feasibility or global optimality.
    """
    _check_matrix(x)
    _check_matrix(g)
    _validate_options(max_iter, tol)
    if x.shape != g.shape or x.dtype != g.dtype or x.device != g.device:
        raise ValueError("X and G must have matching shape, dtype and device")
    eye = torch.eye(x.shape[1], dtype=x.dtype, device=x.device)
    scale = math.sqrt(x.shape[1])
    eps = torch.finfo(x.dtype).eps
    if (torch.linalg.vector_norm(x.T @ x - eye) / scale).item() > 100 * eps:
        raise ValueError("X must have orthonormal columns; initialize with msign(X)")

    tangent_g = project_tangent(x, g)
    # Do not turn a zero (or roundoff-only normal) gradient into an arbitrary
    # orthogonal completion produced by SVD.
    if tangent_g.norm().item() <= 10 * eps * g.norm().item():
        return torch.zeros_like(g), dict(
            iterations=0, change=0.0, orthogonality_error=1.0,
            tangent_error=0.0, converged=False, status="zero_tangent",
        )

    d = g
    status = "max_iter"
    for iteration in range(1, max_iter + 1):
        new_d = msign(project_tangent(x, d))
        change = ((new_d - d).norm() / d.norm().clamp_min(eps)).item()
        d = new_d
        orth_error = (torch.linalg.vector_norm(d.T @ d - eye) / scale).item()
        tangent_error = (torch.linalg.vector_norm(x.T @ d + d.T @ x) / scale).item()
        if change <= tol and tangent_error <= tol and orth_error <= tol:
            status = "converged"
            break

    return d, dict(
        iterations=iteration, change=change, orthogonality_error=orth_error,
        tangent_error=tangent_error,
        converged=status == "converged", status=status,
    )


class StiefelMsign(Optimizer):
    """X <- polar(X - lr * D), with D from alternating_direction.

    Initialize each parameter with orthonormal columns before constructing
    this optimizer. Only 2-D real float32/float64 parameters are supported.
    Per-parameter inner-loop diagnostics are saved in state[p]['diagnostics'].
    There is no line search or general convergence guarantee.
    """

    def __init__(self, params, lr: float = 1e-2, max_iter: int = 100,
                 tol: float = 1e-6):
        super().__init__(params, dict(lr=lr, max_iter=max_iter, tol=tol))
        for group in self.param_groups:
            self._validate_group(group)
            for p in group["params"]:
                _check_matrix(p)

    @staticmethod
    def _validate_group(group):
        if not math.isfinite(group["lr"]) or group["lr"] < 0:
            raise ValueError("lr must be finite and nonnegative")
        _validate_options(group["max_iter"], group["tol"])

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        for group in self.param_groups:
            self._validate_group(group)
            for p in group["params"]:
                if p.grad is None:
                    continue
                if p.grad.is_sparse:
                    raise ValueError("Sparse gradients are not supported")
                d, info = alternating_direction(
                    p, p.grad, max_iter=group["max_iter"], tol=group["tol"]
                )
                self.state[p]["diagnostics"] = info
                if group["lr"] != 0 and info["status"] != "zero_tangent":
                    p.copy_(msign(p - group["lr"] * d))
        return loss
