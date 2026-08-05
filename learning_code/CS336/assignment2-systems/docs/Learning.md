
# Problem Benchmarking Script

[Benchmarking](../cs336_systems/benchmark.py) 

- 通过`torch.randint` 初始化，初始化n+1 elements
- Benchmarking warm-up: 进行初始化几次相同计算但不计入时间，让CUDA context，缓存与显存，kernel等进入稳定状态

