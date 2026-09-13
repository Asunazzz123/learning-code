class GraphModule(torch.nn.Module):
    def forward(self, primals_1: "f32[4, 512, 2560]", primals_2: "f32[2560]", rsqrt: "f32[4, 512, 1]", tangents_1: "f32[4, 512, 2560]"):
        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:21 in forward, code: return self.weight * x
        mul_2: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(tangents_1, primals_2);  primals_2 = None

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:20 in forward, code: x = x*rms
        mul: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(primals_1, rsqrt)

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:21 in forward, code: return self.weight * x
        mul_3: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(tangents_1, mul);  tangents_1 = mul = None
        sum_1: "f32[1, 1, 2560]" = torch.ops.aten.sum.dim_IntList(mul_3, [0, 1], True);  mul_3 = None
        view: "f32[2560]" = torch.ops.aten.reshape.default(sum_1, [2560]);  sum_1 = None

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:20 in forward, code: x = x*rms
        mul_4: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(mul_2, primals_1)
        mul_5: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(mul_2, rsqrt);  mul_2 = None
        sum_2: "f32[4, 512, 1]" = torch.ops.aten.sum.dim_IntList(mul_4, [2], True);  mul_4 = None

        # File: /Users/asuna/Asuna/study&work/git/Learn/learning_code/CS336/assignment2-systems/cs336_systems/autograd.py:19 in forward, code: rms = torch.rsqrt(x.pow(2).mean(-1,keepdim=True) + self.eps)   # rms = 1/ sqrt{ 1/2560*sum xj^2 + eps }
        mul_6: "f32[4, 512, 1]" = torch.ops.aten.mul.Scalar(sum_2, -0.5);  sum_2 = None
        pow_2: "f32[4, 512, 1]" = torch.ops.aten.pow.Tensor_Scalar(rsqrt, 3);  rsqrt = None
        mul_7: "f32[4, 512, 1]" = torch.ops.aten.mul.Tensor(mul_6, pow_2);  mul_6 = pow_2 = None
        expand: "f32[4, 512, 2560]" = torch.ops.aten.expand.default(mul_7, [4, 512, 2560]);  mul_7 = None
        div: "f32[4, 512, 2560]" = torch.ops.aten.div.Scalar(expand, 2560);  expand = None
        pow_3: "f32[4, 512, 2560]" = torch.ops.aten.pow.Tensor_Scalar(primals_1, 1.0);  primals_1 = None
        mul_8: "f32[4, 512, 2560]" = torch.ops.aten.mul.Scalar(pow_3, 2.0);  pow_3 = None
        mul_9: "f32[4, 512, 2560]" = torch.ops.aten.mul.Tensor(div, mul_8);  div = mul_8 = None
        add_1: "f32[4, 512, 2560]" = torch.ops.aten.add.Tensor(mul_5, mul_9);  mul_5 = mul_9 = None
        return (add_1, view)
