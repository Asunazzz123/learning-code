# 基础 on-policy GRPO 训练入口

`train_grpo.py` 已实现题目读取、epoch 内无重复取题、Transformers/vLLM rollout、一次参数更新、验证、JSONL 日志和 checkpoint。第一版每批回答只更新一次，使用 `importance_reweighting_method="none"`。

## 启动

在 assignment5-alignment 目录，使用已下载的模型目录，或可访问的 Hugging Face 模型 ID：

```bash
conda run -n agent python scripts/train_grpo.py \
  --model-id /path/to/model \
  --device cuda:0 --dtype bfloat16 \
  --generation-backend transformers \
  --optimizer-name adamw \
  --num-steps 2 --prompts-per-batch 2 --group-size 2 \
  --gradient-accumulation-steps 2 --generation-batch-size 2 \
  --max-new-tokens 256 --eval-examples 4 \
  --reward-type gsm8k_numeric \
  --output-dir outputs/grpo-smoke
```

CPU 调试改用 `--device cpu --dtype float32`。默认小参数用于检查流程，正式 GSM8K 推理可能需要更长生成长度和更强的初始模型。初始模型如果没有任何正确回答，组内优势可能全为零，不会产生有效学习信号。

`random` 采样策略每轮打乱一次后按窗口取题；`order` 按原顺序取题；两者都丢弃每轮不足一个窗口的尾部。

## 奖励模式

- `gsm8k_numeric`：无需原数学评分器的额外依赖。提取明确的 `\\boxed{...}` 或答案标签内的数字，以 Decimal 比较；不支持分数、一般 LaTeX 数学表达式等价判定。此模式不等价于作业官方评测。
- `r1_zero` / `question_only`：使用现有 `drgrpo_grader.py`。缺少依赖时显式报错，不静默改用数值评分器。

默认使用已有的 r1_zero prompt。若使用 question_only 模板，也应匹配相应 reward 模式。生成文本保留答案结束标签，不给长度截断的回答附加伪造 EOS。

## 优化器与日志

`--optimizer-name adam/adamw/muon` 控制创建方式。Muon 使用 PyTorch 自带实现，隐藏层二维矩阵采用 Muon，embedding、输出层和非矩阵参数采用 AdamW；不支持 Muon 的 PyTorch 环境会明确报错。此分组是基础比较配置，各优化器仍需要单独调学习率。

日志位于 `metrics.jsonl`，包含训练 loss、奖励、token entropy、梯度范数、生成/更新耗时和部分回答；验证采用固定题目和贪心生成。checkpoint 保存模型、tokenizer、优化器和随机状态。尚未提供恢复完整训练状态的 CLI；可以从 checkpoint 目录加载权重开始新实验。

输出目录必须为空，以免覆盖之前的实验。`cs336_alignment/grpo.py` 是训练与测试共用的实现，`tests/adapters.py` 引用它。

## vLLM

```bash
conda run -n agent python scripts/train_grpo.py \
  --model-id /path/to/model --device cuda:0 --dtype bfloat16 \
  --generation-backend vllm --vllm-gpu 1 --vllm-port 8000 \
  --reward-type r1_zero --output-dir outputs/grpo-vllm
```

该路径使用项目现有服务及 NCCL 权重同步工具，要求对应 vLLM 依赖和两块不同的 CUDA GPU。只停止本次创建的服务，端口占用时报错。当前 macOS 环境未验证实际 vLLM/GPU 运行。

## 验证

```bash
conda run -n agent python -m pytest tests -q
conda run -n agent python scripts/train_grpo.py --help
```

新增测试以本地随机初始化小模型完成两轮真实生成、训练、验证、保存和重载；另用有正负优势的已知回答验证三个优化器确实更新参数。这证明基础流程可执行，不代表 GSM8K 正确率提升。

后续可增加 off-policy 多次更新、固定旧策略 log_probs、零优势样本跳过、严格复用生成 token ID 以及完整断点恢复。实际模型上的奖励提升仍需单独实验验证。
