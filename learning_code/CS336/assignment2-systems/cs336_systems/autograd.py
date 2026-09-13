import torch
from torch import nn

x = torch.randn((4,512,2560),requires_grad=True)

class RMSNorm(nn.Module):
    def __init__(
        self,
        hidden_size: int,
        eps: float = 1e-5,
        device : torch.device | None = None,
    ):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size,device=device))
        self.eps = eps

    def forward(self,x):
        # 前向传播的流程是 平方pow->求n个vector(对应tensor的后1维)均值mean->加扰动eps->rsqrt->归一化乘法并更新->乘weight并scale
        rms = torch.rsqrt(x.pow(2).mean(-1,keepdim=True) + self.eps)   # rms = 1/ sqrt{ 1/2560*sum xj^2 + eps }
        x = x*rms
        return self.weight * x

def pack_hook(t):
    shape,dtype,grad_fn = t.shape, t.dtype, t.grad_fn
    print(f"Saving residual:{shape=},{dtype=},{grad_fn=}")
    return t

def unpack_hook(t):
    shape,dtype,grad_fn = t.shape, t.dtype, t.grad_fn
    print(f"Loading residual:{shape=},{dtype=},{grad_fn=}")
    return t

if __name__ == "__main__":
    mode = "Fusion"
    if mode == "Fusion":
        # 编译RMSNorm 的计算图前向计算图
        # torch.compile 的模式:
        # 1. eager模式: TorchDynamo 捕获前向计算并生成FX/ATen 前向计算图，通过pytorch eager kernels 执行
        # 2. aot_eager模式: 根据TorchDynamo 的前向计算图，AOTAutograd 联合构造前向-反向计算图并划分为前向计算图和反向计算图，由eager kernels 执行
        # 3. inductor: Dynamo 和 AOTautograd 的计算图并由TorchInductor进行算子的生成, 调度和算子融合
        ln = torch.compile(RMSNorm(x.shape[-1]),backend="inductor")
    else:
        ln = RMSNorm(x.shape[-1])

    with torch.autograd.graph.saved_tensors_hooks(pack_hook,unpack_hook):
        y = ln(x)
        y.sum().backward()
