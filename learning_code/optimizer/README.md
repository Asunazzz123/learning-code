# Stiefel + msign 优化器

基于 PyTorch，约束实数参数矩阵 `X ∈ R^(n×p)`、`n >= p`、`X.T @ X = I`。
采用嵌入欧氏空间的 Frobenius 度量，支持 float32/float64。

每个优化步骤固定当前 X：

```text
P_X(G) = G - X sym(X.T G),  sym(A) = (A + A.T) / 2
D_0 = G
D_(k+1) = msign(P_X(D_k))
X_new = msign(X - lr D_final)
```

`msign(A) = U @ Vh` 使用 reduced SVD，实现到列正交矩阵集合的最近点映射。
秩亏时使用 SVD 给出的正交补全，结果不唯一；这区别于令零奇异值对应符号为零的 partial polar 定义。
零切向梯度直接跳过，避免 SVD 补全产生无意义更新。
参数更新的 msign 是 polar retraction；内循环最后一步也为 msign，与截图公式 (15) 一致。
除零切向梯度跳过外，返回方向保证列正交；有限迭代下可能还不在切空间。

```python
import torch
from stiefel_msign import StiefelMsign, msign

x = torch.nn.Parameter(msign(torch.randn(8, 3)))
target = torch.randn_like(x)
optimizer = StiefelMsign([x], lr=0.01, max_iter=100, tol=1e-6)
for _ in range(20):
    optimizer.zero_grad()
    loss = (x - target).square().sum()
    loss.backward()
    optimizer.step()
print(optimizer.state[x]["diagnostics"])
```

独立函数 `alternating_direction(x, g)` 返回方向和诊断信息。
迭代变化量为 `||D_new-D_old||_F / max(||D_old||_F, eps)`；
正交残差为 `||D.T D-I||_F / sqrt(p)`，切空间残差为
`||X.T D+D.T X||_F / sqrt(p)`。
只有变化量和两项残差均小于等于 tol 才标记 `converged`；其余状态为
`max_iter` 或 `zero_tangent`。变化很小但约束未满足时继续迭代至次数上限。
未收敛时仍使用最后的列正交方向更新，再将参数投回流形；此时不能称为严格的切向更新。

这是一种交替投影启发式，不保证交集存在、全局最近点或每步损失下降。
例如 X 为奇数阶正交方阵时，切向量 XΩ 中的反对称 Ω 必然奇异，不能同时列正交。
目前不包含动量、权重衰减、线搜索、批量矩阵或低精度支持；普通网络的偏置等参数需另用优化器。
每次内循环需要一次 SVD，适合作为正确性基线。

运行验证：

```sh
conda run -n agent python -m unittest -v test_stiefel_msign
```

SVD API：[PyTorch 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.linalg.svd.html)。

## 小模型训练 benchmark

```sh
MPLCONFIGDIR=/tmp/stiefel-mpl conda run -n agent python -m benchmark.benchmark
```

训练 `16→8→4` tanh MLP（172 个参数），用固定随机教师生成分类标签，无需下载数据。
训练/验证/测试集分别为 1024/512/512；默认 20 个 epoch、batch size 128，
CPU float32 单线程，随机种子为 0/1/2。

比较三种方法：

- `sgd`：标准 SGD，不施加正交约束。
- `riemannian_sgd`：矩阵梯度投影到切空间，SGD 更新后做 polar retraction。
- `msign`：本文优化器，内循环最多 20 次（可用 `--max-iter` 调整）。

两个受约束方法都约束两层权重，偏置使用普通 SGD。
各方法使用相同初始权重、批次顺序和学习率搜索预算，在 `[0.01, 0.05, 0.2]` 中
按跨种子的最终验证损失选择一个学习率，然后报告最终模型测试结果。
没有动量或权重衰减。各方法的学习率同时应用于权重和偏置；相同学习率不代表相同更新幅度。

从 optimizer 目录运行上述模块命令。结果保存在 `benchmark/results/benchmark_msign_last/`；
上一版以切空间投影结束的结果保留在 `benchmark/results/benchmark/`。

- `summary.md`：选中学习率及测试指标的均值、样本标准差。
- `results.json`：算法顺序、运行配置、环境、全部训练/验证曲线及抽样内循环残差与状态。
- `curves.png`：训练损失、验证准确率以及按训练时间对比的曲线。

计时包含前向、反向和优化器更新，排除初始化、评估、绘图和学习率搜索的其他试验。
运行前做独立预热。内循环诊断每个 epoch 最后一批抽样记录。
此实验适合检查算法行为与开销，不能据此断言真实数据集上的普遍优劣。

快速运行或调整参数：

```sh
MPLCONFIGDIR=/tmp/stiefel-mpl conda run -n agent python -m benchmark.benchmark --epochs 5 --seeds 0 --lrs 0.05 --output benchmark/results/smoke
```
