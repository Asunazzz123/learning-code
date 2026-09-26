import unittest
from types import SimpleNamespace

import torch

from benchmark.benchmark import SmallMLP, make_data, make_optimizers, train


class BenchmarkTests(unittest.TestCase):
    def test_adam_muon_parameter_coverage_and_training(self):
        torch.set_num_threads(1)
        data = make_data()
        args = SimpleNamespace(epochs=2, batch_size=128, max_iter=20)
        for method, lr in (("adam", 0.005), ("muon", 0.01)):
            with self.subTest(method=method):
                torch.manual_seed(0)
                model = SmallMLP()
                initial = {k: v.detach().clone() for k, v in model.state_dict().items()}
                opts = make_optimizers(model, method, lr, 20)
                parameters = [p for opt in opts for group in opt.param_groups for p in group["params"]]
                self.assertEqual(len(parameters), len(set(map(id, parameters))))
                self.assertEqual(set(map(id, parameters)), set(map(id, model.parameters())))
                run, state = train(method, lr, 0, data, args)
                self.assertLess(run["history"][-1]["train"]["loss"], run["history"][0]["train"]["loss"])
                for name, value in state.items():
                    self.assertTrue(torch.isfinite(value).all())
                    self.assertFalse(torch.equal(value, initial[name]), name)
                repeated, repeated_state = train(method, lr, 0, data, args)
                self.assertEqual(run["history"][-1]["val"], repeated["history"][-1]["val"])
                for name in state:
                    self.assertTrue(torch.equal(state[name], repeated_state[name]))


if __name__ == "__main__":
    unittest.main()
