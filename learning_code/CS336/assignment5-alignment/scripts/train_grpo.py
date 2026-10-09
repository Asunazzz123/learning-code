"""基础 on-policy GRPO 脚手架"""

from __future__ import annotations

import json
import argparse
import random
import numpy as np
from cs336_alignment import vllm_utils
from transformers import AutoModelForCausalLM, AutoTokenizer
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch


PROJECT_DIR = Path(__file__).resolve().parents[1]


@dataclass
class TrainConfig:
    model_id: str
    train_path: Path
    eval_path: Path
    prompt_path: Path
    output_dir: Path
    device: str
    generation_backend: str
    seed: int
    num_steps: int
    prompts_per_batch: int
    group_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    max_grad_norm: float
    temperature: float
    max_new_tokens: int
    eval_every: int
    eval_examples: int
    save_every: int
    optimizer: str


@dataclass
class Question:
    question: str
    ground_truth: str


@dataclass
class RolloutBatch:
    # 三个列表长度均为 prompts_per_batch * group_size，同题回答连续排列
    repeated_prompts: list[str]
    responses: list[str]
    repeated_ground_truths: list[str]


@dataclass
class Runtime:
    model: Any
    tokenizer: Any
    optimizer: Any
    # transformers 路线可以复用 model；vLLM 路线可以存放服务和同步状态
    generator: Any

def optimizer_switcher(model, config):
    params = [p for p in model.parameters() if p.requires_grad]
    match config.optimizer_name:
        case "adam":
            return torch.optim.Adam(
                params,
                lr=config.learning_rate,
            )
        case "adamw":
            return torch.optim.AdamW(
                params,
                lr=config.learning_rate,
            )
        case "muon":
            raise NotImplementedError
        case _:
            raise ValueError(f"未知优化器：{config.optimizer_name}")



def seed_everything(seed: int) -> None:
    """设置 Python、PyTorch 和生成器的随机种子。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # raise NotImplementedError("TODO: seed_everything")


def load_questions(path: Path) -> list[Question]:
    """读取 GSM8K JSONL，从 answer 的 #### 后提取标准答案。"""
    with open(path,encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            record = json.loads(line)
    questions = []
    # 在 Assignment5 中的 jsonl 通过 #### 划分QA
    ground_truth = record["answer"].rsplit("####", 1)[1].strip()

    questions.append(
        Question(
            question=record["question"],
            ground_truth=ground_truth,
        )
    )
    return questions




def load_prompt_template(path: Path) -> str:
    """读取模板；保留与奖励函数匹配的标签、空格和结尾。"""
    with open(path, encoding="utf-8") as f:
        return f.read()



def build_runtime(config: TrainConfig) -> Runtime:
    """加载模型、tokenizer、优化器，并准备生成后端。

    检查 pad token、设备和精度；第一次跑通可只实现 transformers 后端。
    若初始化到一半失败，此函数负责释放已经创建的服务或资源。
    """
    model = AutoModelForCausalLM.from_pretrained(config.model_id)
    tokenizer = AutoTokenizer.from_pretrained(config.model_id)
    match config.generation_backend:
        case "tranformers":
            generator = model;
        case "vllm":
            pass # TODO: 实现vllm前向
        case _:
            raise ValueError("No Generation Name")
    Runtime(
        model=model,
        tokenizer=tokenizer,
        optimizer=optimizer_switcher(config.optimizer),
        generator=generator
    )




def sample_questions(
    questions: list[Question], count: int, step: int
) -> list[Question]:
    """TODO：每轮选择 count 道题，明确是否有放回采样或按 epoch 遍历。"""
    raise NotImplementedError("TODO: sample_questions")


def sync_generator(runtime: Runtime, config: TrainConfig) -> None:
    """TODO：保证生成器使用当前策略权重。

    若生成器直接复用训练模型，则无需复制；vLLM 后端需同步权重。
    可查看 cs336_alignment/vllm_utils.py 中已有的同步接口。
    """
    raise NotImplementedError("TODO: sync_generator")


def generate_rollouts(
    runtime: Runtime,
    questions: list[Question],
    template: str,
    config: TrainConfig,
) -> RolloutBatch:
    """TODO：套模板，每题采样 group_size 条回答，构造三个对齐列表。

    生成关闭梯度；responses 仅包含新生成的回答。
    明确 EOS、停止标签与截断的处理，确保奖励函数能识别回答格式。
    保留同一道题的分组顺序，并恢复训练所需的模型状态。
    """
    raise NotImplementedError("TODO: generate_rollouts")


def train_on_rollouts(
    runtime: Runtime, rollouts: RolloutBatch, config: TrainConfig
) -> tuple[torch.Tensor, dict[str, Any]]:
    """TODO：对接已实现的 run_grpo_train_step，执行一次 on-policy 更新。

    现有实现位于 tests/adapters.py；可整理到 cs336_alignment 后由两处复用。
    第一版使用 importance_reweighting_method='none'，一批 rollout 只更新一次。
    reward_fn 应与 prompt 模板对应；奖励和优势计算不要在外层重复执行。
    返回日志 loss 和 metadata，补齐 entropy 等讲义要求的统计。
    """
    raise NotImplementedError("TODO: train_on_rollouts")


def evaluate(
    runtime: Runtime,
    questions: list[Question],
    template: str,
    config: TrainConfig,
) -> dict[str, Any]:
    """TODO：在固定验证题目上生成并评分，返回奖励、正确率、长度及样例。

    不更新参数，不与训练数据混用；明确评测采样参数和正确率的定义。
    """
    raise NotImplementedError("TODO: evaluate")


def log_metrics(
    output_dir: Path, step: int, split: str, metrics: dict[str, Any]
) -> None:
    """TODO：将标量 Tensor 转为日志值，输出到终端及本地 JSONL。

    第一次跑通无需外部日志服务；区分 train/eval，并记录配置和生成样例。
    """
    raise NotImplementedError("TODO: log_metrics")


def save_checkpoint(runtime: Runtime, config: TrainConfig, step: int) -> None:
    """TODO：保存模型、tokenizer、优化器、配置和步数，避免覆盖已有结果。"""
    raise NotImplementedError("TODO: save_checkpoint")


def close_runtime(runtime: Runtime) -> None:
    """TODO：释放由本脚本创建的生成服务或资源；不要停止外部共享服务。"""
    raise NotImplementedError("TODO: close_runtime")


def train(config: TrainConfig) -> None:
    # 1. 固定随机种子，读取训练题目、验证题目和 prompt 模板
    seed_everything(config.seed)
    train_questions = load_questions(config.train_path)
    eval_questions = load_questions(config.eval_path)[:config.eval_examples]
    template = load_prompt_template(config.prompt_path)

    # 2. 初始化训练模型、优化器和生成后端
    runtime = build_runtime(config)
    try:
        # 3. 更新前进行基线评测，便于和训练后的结果比较
        sync_generator(runtime, config)
        metrics = evaluate(runtime, eval_questions, template, config)
        log_metrics(config.output_dir, 0, "eval", metrics)

        for step in range(1, config.num_steps + 1):
            # 4. 选择一批题目，用当前策略生成分组回答
            questions = sample_questions(train_questions, config.prompts_per_batch, step)
            sync_generator(runtime, config)
            rollouts = generate_rollouts(runtime, questions, template, config)

            # 5. 对本批回答执行一次更新，记录训练 loss 和统计信息
            loss, metadata = train_on_rollouts(runtime, rollouts, config)
            log_metrics(config.output_dir, step, "train", {**metadata, "loss": loss})

            # 6. 定期同步最新权重并验证，同时保留最终一步的评测
            if step % config.eval_every == 0 or step == config.num_steps:
                sync_generator(runtime, config)
                metrics = evaluate(runtime, eval_questions, template, config)
                log_metrics(config.output_dir, step, "eval", metrics)

            # 7. 定期保存 checkpoint，同时保留最终一步的模型
            if step % config.save_every == 0 or step == config.num_steps:
                save_checkpoint(runtime, config, step)
    finally:
        # 8. 正常完成或出错退出时释放运行资源
        close_runtime(runtime)


def parse_args() -> TrainConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--train-path", type=Path, default=PROJECT_DIR / "data/gsm8k/train.jsonl")
    parser.add_argument("--eval-path", type=Path, default=PROJECT_DIR / "data/gsm8k/test.jsonl")
    parser.add_argument("--prompt-path", type=Path, default=PROJECT_DIR / "cs336_alignment/prompts/r1_zero.prompt")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "outputs/grpo")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--generation-backend", choices=["transformers", "vllm"], default="transformers")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-steps", type=int, default=2)
    parser.add_argument("--prompts-per-batch", type=int, default=2)
    parser.add_argument("--group-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--max-grad-norm", type=float, default=1.0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--eval-every", type=int, default=1)
    parser.add_argument("--eval-examples", type=int, default=4)
    parser.add_argument("--save-every", type=int, default=1)
    args = parser.parse_args()
    for name in (
        "num_steps", "prompts_per_batch", "group_size", "gradient_accumulation_steps",
        "max_new_tokens", "eval_every", "eval_examples", "save_every",
    ):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.group_size < 2:
        parser.error("--group-size must be at least 2 for group normalization")
    if (args.prompts_per_batch * args.group_size) % args.gradient_accumulation_steps:
        parser.error("rollout batch size must be divisible by gradient accumulation steps")
    return TrainConfig(**vars(args))


if __name__ == "__main__":
    train(parse_args())
