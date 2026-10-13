from __future__ import annotations


import re
import json
import os
import random
from pathlib import Path
from typing import Any, Callable, Literal

import torch
from torch import Tensor
from torch.utils.data import Dataset,DataLoader
from transformers import PreTrainedTokenizerBase


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from cs336_alignment.grpo import (
    run_tokenize_prompt_and_output,
    run_get_response_log_probs,
    run_compute_rollout_rewards,
    run_compute_group_normalized_rewards,
    run_compute_policy_gradient_loss,
    run_aggregate_loss_across_microbatch,
    run_grpo_train_step,
)


"""
The below adapters are used in the optional
RLHF / safety part of the Alignment assignment.
"""


class _PackedSFTDataset(Dataset):
    def __init__(self, token_ids: list[int], seq_length: int):
        tokens = torch.tensor(token_ids, dtype=torch.long)
        n_examples = max(0, (len(token_ids) - 1) // seq_length)
        usable_length = n_examples * seq_length
        self.input_ids = tokens[:usable_length].reshape(n_examples, seq_length)
        self.labels = tokens[1:usable_length + 1].reshape(n_examples, seq_length)

    def __len__(self):
        return self.input_ids.shape[0]

    def __getitem__(self, index):
        return {
            "input_ids": self.input_ids[index],
            "labels": self.labels[index],
        }


def get_packed_sft_dataset(
    tokenizer: PreTrainedTokenizerBase,
    dataset_path: str | os.PathLike,
    seq_length: int,
    shuffle: bool,
) -> Dataset:
    """
    Given a tokenizer and a path to a dataset with instruction-tuning examples,
    construct a PyTorch Dataset for language modeling. The examples should be
    packed, i.e., all sequences in the dataset are of a constant length (`seq_length`).

    Args:
        tokenizer: transformers.PreTrainedTokenizerBase
            Transformers tokenizer to use in tokenizing and encoding text.
        dataset_path: str
            Path to file with instruction-tuning examples.
        seq_length: int
            Number of tokens to include in each example.
        shuffle: bool
            If true, shuffle the documents before packing them into examples.

    Returns:
        PyTorch Dataset for language modeling. Each example in this dataset is a dictionary of
        with keys "input_ids" and "labels" (both tensors of shape (seq_length, )).
        "input_ids" contains the token IDs for the language modeling inputs, and "labels" contains
        the token IDs for the language modeling labels.
    """
    if seq_length <= 0:
        raise ValueError("seq_length must be positive")
    if tokenizer.eos_token_id is None:
        raise ValueError("tokenizer must define an EOS token")

    # 1. 逐行读取 JSONL，每条样本包含 prompt 和 response
    with open(dataset_path, encoding="utf-8") as f:
        documents = [json.loads(line) for line in f if line.strip()]

    # 2. 在 packing 前打乱文档顺序，保留每条文档内部的 token 顺序
    if shuffle:
        random.shuffle(documents)

    # 3. 使用 Alpaca SFT 模板组织输入，去掉模板首尾的空白
    template_path = (
        Path(__file__).resolve().parents[1]
        / "cs336_alignment/prompts_safety/alpaca_sft.prompt"
    )
    template = template_path.read_text(encoding="utf-8").strip()

    # 4. 分词并追加 EOS，将各文档拼接为一个连续 token 流
    token_ids = []
    for document in documents:
        text = template.format(
            instruction=document["prompt"],
            response=document["response"],
        )
        token_ids.extend(tokenizer.encode(text, add_special_tokens=True))
        token_ids.append(tokenizer.eos_token_id)

    # 5. 按固定长度切块，labels 向后偏移一位，丢弃不足一块的尾部
    return _PackedSFTDataset(token_ids, seq_length)


def run_iterate_batches(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool,
):
    """
    Given a PyTorch Dataset, return an iterable over batches of size `batch_size`.
    Iterating through the returned iterable should constitute one epoch over the Dataset.

    Args:
        dataset: Dataset
            Dataset to emit batches from.
        batch_size: int
            Number of examples to include per batch.
        shuffle: bool
            If true, shuffle examples before batching them.

    Returns:
        Iterable over batches, where each batch has size `batch_size`.
    """
    return DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=False
    )
    # raise NotImplementedError


def run_parse_mmlu_response(
    mmlu_example: dict[str, Any],
    model_output: str,
) -> str | None:
    """
    Given an MMLU example and a model output, parse the model output into a
    predicted option letter (i.e., 'A', 'B', 'C', or 'D'). If the model output
    cannot be parsed into a prediction option letter, return None.

    mmlu_example: dict[str, Any]
        Dictionary with an MMLU example. Contains the following keys:
        - "subject": str with the subject of the question.
        - "question": str with the text of the question.
        - "options": list[str] with the four answer options (in order).
                     The first option refers to letter "A", the second to "B", etc.
        - "answer": str with the option of the correct answer (e.g., "A")
    model_output: str
        str with the model's output to the MMLU example.

    Returns:
        str (one of "A", "B", "C", or "D") if the model output can be parsed into a prediction,
        else None.
    """
    answer = mmlu_example["answer"]

    match = re.search(
        r"\b(?:the\s+correct\s+answer\s+is|answer\s*[:：])\s*([ABCD])\b",
        model_output,
        flags=re.IGNORECASE,
    )
    return match.group(1).upper() if match else None

def run_parse_gsm8k_response(
    model_output: str,
) -> str | None:
    """
    Given a GSM8K model output, parse the model output into a predicted numeric answer by
    taking the last number that occurs in the output.

    model_output: str
        str with the model's output to a GSM8K example.

    Returns:
        str with the predicted numeric answer if the model output can be parsed into a prediction,
        else None.
    """
    numbers = re.findall(r"-?\d+(?:\.\d+)?", model_output)
    return numbers[-1] if numbers else None


def run_compute_per_instance_dpo_loss(
    lm: torch.nn.Module,
    lm_ref: torch.nn.Module,
    tokenizer: PreTrainedTokenizerBase,
    beta: float,
    prompt: str,
    response_chosen: str,
    response_rejected: str,
) -> torch.Tensor:
    """
    Given two language models (`lm`, and the "reference model" `lm_ref`),
    their tokenizer, the DPO beta hyperparameter, a prompt and a pair
    of responses to the prompt, computes the value of the DPO loss for this example.

    lm: torch.nn.Module
        Language model being trained.
    lm_ref: torch.nn.Module
        Reference language model.
    tokenizer: PreTrainedTokenizerBase
        Tokenizer for both language models.
    beta: float
        DPO beta hyperparameter.
    prompt: str
        Prompt for this instance of preference pair.
    response_chosen: str
        Preferred response to the prompt.
    response_rejected: str
        Rejected response to the prompt.

    Returns:
        torch.Tensor with the DPO loss for this example.
    """
    formatted_prompt = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        f"### Instruction:\n{prompt}\n\n"
        "### Response:\n"
    )
    tokenized = run_tokenize_prompt_and_output(
        prompt_strs=[formatted_prompt, formatted_prompt],
        output_strs=[
            response_chosen + tokenizer.eos_token,
            response_rejected + tokenizer.eos_token,
        ],
        tokenizer=tokenizer
    )
    input = tokenized["input_ids"]
    label = tokenized["labels"]
    result = run_get_response_log_probs(
        model=lm,
        input_ids=input,
        labels=label,
        return_token_entropy=False
    )
    token_log_probs = result["log_probs"]

    sequence_log_probs = (
        token_log_probs * tokenized["response_mask"]
    ).sum(dim=1)

    log_prob_chosen = sequence_log_probs[0]
    log_prob_rejected = sequence_log_probs[1]

    with torch.no_grad():
        ref_result = run_get_response_log_probs(
            model=lm_ref,
            input_ids=tokenized["input_ids"],
            labels=tokenized["labels"],
            return_token_entropy=False,
        )

        ref_sequence_log_probs = (
            ref_result["log_probs"] * tokenized["response_mask"]
        ).sum(dim=1)

    log_prob_ref_chosen = ref_sequence_log_probs[0]
    log_prob_ref_rejected = ref_sequence_log_probs[1]

    policy_log_ratio = log_prob_chosen - log_prob_rejected
    reference_log_ratio = log_prob_ref_chosen - log_prob_ref_rejected

    loss = -torch.nn.functional.logsigmoid(
        beta * (policy_log_ratio - reference_log_ratio)
    )

    return loss
    # raise NotImplementedError
