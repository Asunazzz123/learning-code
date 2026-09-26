import torch
import math
import timeit
from jaxtyping import Bool, Float, Int
from torch import Tensor
from contextlib import contextmanager
from einops import einsum, rearrange
from cs336_basics.model import scaled_dot_product_attention
from cs336_basics.nn_utils import softmax

SEQUENCE_LENGTH = [256,1024,4096,8192,16384]
DIM = [16,32,64,128]
mask = None

time_recorder = {}

@contextmanager
def timer(period: str, config: str = "overall"):
    start = timeit.default_timer()
    try:
        yield
    finally:
        elapsed = timeit.default_timer() - start
        time_recorder.setdefault(period, {}).setdefault(config, []).append(elapsed)


def naive_attention(
    Q: Float[Tensor,"... queries d_k"],
    K: Float[Tensor,"... keys    d_k"],
    V: Float[Tensor,"... keys    d_k"],
    mask: Bool[Tensor,"... queries keys"] | None
) -> Float[Tensor, "... queries d_v"]:

    d_k = K.shape[-1]

    attention_scores = einsum(Q, K, "... query d_k, ... key d_k -> ... query key")

    attention_scores = attention_scores / math.sqrt(d_k)
    if mask is not None:
            attention_scores = torch.where(mask, attention_scores, float("-inf"))

    attention_weights = softmax(attention_scores, dim=-1)  # Softmax over the key dimension
    prod = einsum(attention_weights, V, "... query key, ... key d_v ->  ... query d_v")
    return prod


def naive_attention_nvtx(
    Q: Float[Tensor,"... queries d_k"],
    K: Float[Tensor,"... keys    d_k"],
    V: Float[Tensor,"... keys    d_k"],
    mask: Bool[Tensor,"... queries keys"] | None
) -> Float[Tensor, "... queries d_v"]:

    d_k = K.shape[-1]
    with torch.cuda.nvtx.range("Attention_score_matmul"):
        with timer("attn_score_matmul"):
            attention_scores = einsum(Q, K, "... query d_k, ... key d_k -> ... query key")

    with torch.cuda.nvtx.range("Attention_score_scaling"):
        with timer("attn_score_scaling"):
            attention_scores = attention_scores / math.sqrt(d_k)
    if mask is not None:
        with timer("mask_covering"):
            attention_scores = torch.where(mask, attention_scores, float("-inf"))

    with torch.cuda.nvtx.range("Scaled_dot_softmax"):
        with timer("dot_softmax"):
            attention_weights = softmax(attention_scores, dim=-1)  # Softmax over the key dimension

    with torch.cuda.nvtx.range("value_matrix_product"):
        with timer("value_matrix_product"):
            prod = einsum(attention_weights, V, "... query key, ... key d_v ->  ... query d_v")
    return prod


def run():
    attn_compiled = torch.compile(naive_attention)
    for seq_len in SEQUENCE_LENGTH:
        for d in DIM:
            Q,K,V = torch.rand([8,seq_len,d])
            with timer("compiled_attention", f"seq={seq_len},d={d}"):
                attn_compiled(Q,K,V,mask)


