class GraphModule(torch.nn.Module):
    def forward(self, primals_1: "f32[4, 512, 2560]", primals_2: "f32[2560]"):
        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:19 in forward, code: rms = torch.rsqrt(x.pow(2).mean(-1,keepdim=True) + self.eps)   # rms = 1/ sqrt{ 1/2560*sum xj^2 + eps }
        pow_1: "f32[4, 512, 2560]" = torch.ops.aten.pow.Tensor_Scalar(primals_1, 2)
        mean: "f32[4, 512, 1]" = torch.ops.aten.mean.dim(pow_1, [-1], True);  pow_1 = None
        add: "f32[4, 512, 1]" = torch.ops.aten.add.Tensor(mean, 1e-05);  mean = None
        rsqrt: "f32[4, 512, 1]" = torch.ops.aten.rsqrt.default(add);  add = None

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:20 in forward, code: x = x*rms
        mul: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(primals_1, rsqrt)

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:21 in forward, code: return self.weight * x
        mul_1: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(primals_2, mul);  mul = None
        return (mul_1, primals_1, primals_2, rsqrt)
