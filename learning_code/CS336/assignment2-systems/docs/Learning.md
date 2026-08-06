
# Problem Benchmarking Script

[Benchmarking](../cs336_systems/benchmark.py) 

- 通过`torch.randint` 初始化，初始化n+1 elements
- Benchmarking warm-up: 进行初始化几次相同计算但不计入时间，让CUDA context，缓存与显存，kernel等进入稳定状态


## Warmup Test

warmup test 分为 Forward-Only 、 Forward and backward 、 Forward and backward with optimizer

分别记录 前向传播的耗时、前向和反向传播的耗时以及 前向+反向+梯度下降优化总耗时

作为`torch.nn.Module`绑定，model的前向传播可以直接使用`model(x)`，而不使用 `model.forward(x)` forward通常作为private 函数。 对于某个量的backward 不需要手动实现，通过绑定 `loss.backward()` 实现

`torch.cuda.synchronize()` 停止CPU等待 GPU任务结束， 从而精确记录GPU计算时间


### `torch.nn.Module`对象的`zero_grad()`与 `torch.optim.Optimizer`对象的 `zero_grad()`实现的区别


