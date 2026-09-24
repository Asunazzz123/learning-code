import unittest

import torch

from stiefel_msign import StiefelMsign, alternating_direction, msign, project_tangent


class StiefelTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)
        self.x = msign(torch.randn(8, 3, dtype=torch.float64))

    def test_projection_geometry(self):
        g = torch.randn_like(self.x)
        d = project_tangent(self.x, g)
        torch.testing.assert_close(self.x.T @ d + d.T @ self.x, torch.zeros(3, 3, dtype=d.dtype))
        torch.testing.assert_close(project_tangent(self.x, d), d)
        self.assertAlmostEqual(((g - d) * d).sum().item(), 0, places=12)

    def test_feasible_fixed_point(self):
        x = torch.eye(6, dtype=torch.float64)[:, :3]
        g = torch.eye(6, dtype=torch.float64)[:, 3:]
        d, info = alternating_direction(x, g)
        torch.testing.assert_close(d, g)
        self.assertTrue(info["converged"])

    def test_infeasible_odd_square(self):
        x = torch.eye(3, dtype=torch.float64)
        g = torch.tensor([[0., -1., 0.], [1., 0., 0.], [0., 0., 0.]], dtype=x.dtype)
        d, info = alternating_direction(x, g, max_iter=10)
        self.assertFalse(info["converged"])
        self.assertGreater(info["tangent_error"], 0.5)
        torch.testing.assert_close(d.T @ d, x)
        self.assertEqual(info["iterations"], 10)
        self.assertEqual(info["status"], "max_iter")

    def test_truncation_returns_orthogonal_not_tangent_direction(self):
        g = torch.randn_like(self.x)
        d, info = alternating_direction(self.x, g, max_iter=1)
        torch.testing.assert_close(d.T @ d, torch.eye(3, dtype=d.dtype))
        self.assertGreater(info["tangent_error"], 1e-3)
        # The polar factor maximizes the linear objective over Stiefel.
        projected = project_tangent(self.x, g)
        self.assertAlmostEqual((projected * d).sum().item(),
                               torch.linalg.svdvals(projected).sum().item(), places=12)

    def test_zero_and_normal_gradients_do_not_move(self):
        for g in (torch.zeros_like(self.x), self.x @ torch.diag(torch.tensor([1., 2., 3.], dtype=self.x.dtype))):
            x = torch.nn.Parameter(self.x.clone())
            opt = StiefelMsign([x])
            x.grad = g
            opt.step()
            self.assertTrue(torch.equal(x, self.x))
            self.assertEqual(opt.state[x]["diagnostics"]["status"], "zero_tangent")

    def test_optimizer_retraction_and_descent(self):
        for dtype in (torch.float32, torch.float64):
            x = torch.nn.Parameter(self.x.to(dtype))
            target = torch.randn_like(x)
            opt = StiefelMsign([x], lr=0.01, max_iter=30)
            before = ((x - target) ** 2).sum().item()

            def closure():
                opt.zero_grad()
                loss = ((x - target) ** 2).sum()
                loss.backward()
                return loss

            for _ in range(10):
                opt.step(closure)
                torch.testing.assert_close(x.T @ x, torch.eye(3, dtype=dtype), atol=2e-6, rtol=2e-6)
            self.assertLess(((x - target) ** 2).sum().item(), before)

    def test_validation_and_zero_lr(self):
        with self.assertRaises(ValueError):
            alternating_direction(self.x * 2, self.x)
        with self.assertRaises(ValueError):
            StiefelMsign([torch.nn.Parameter(self.x)], max_iter=0)
        x = torch.nn.Parameter(self.x.clone())
        x.grad = torch.randn_like(x)
        StiefelMsign([x], lr=0).step()
        self.assertTrue(torch.equal(x, self.x))


if __name__ == "__main__":
    unittest.main()
