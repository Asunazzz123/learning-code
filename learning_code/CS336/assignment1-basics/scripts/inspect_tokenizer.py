import json
import sys
sys.path.insert(0, "learning_code/CS336/assignment1-basics")

from cs336_basics.tokenizer import Tokenizer
from tests.common import FIXTURES_PATH, gpt2_bytes_to_unicode


gpt2_byte_decoder = {v: k for k, v in gpt2_bytes_to_unicode().items()}

with open(FIXTURES_PATH / "gpt2_vocab.json") as f:
    gpt2_vocab = json.load(f)

vocab = {
    idx: bytes([gpt2_byte_decoder[t] for t in token])
    for token, idx in gpt2_vocab.items()
}

merges = []
with open(FIXTURES_PATH / "gpt2_merges.txt") as f:
    for line in f:
        parts = line.rstrip().split(" ")
        if len(parts) == 2:
            merges.append((
                bytes([gpt2_byte_decoder[t] for t in parts[0]]),
                bytes([gpt2_byte_decoder[t] for t in parts[1]]),
            ))

tokenizer = Tokenizer(vocab, merges, special_tokens=["<|endoftext|>"])


while True:
    try:
        text = input("\n输入文本 (Ctrl+C 退出): ")
    except (EOFError, KeyboardInterrupt):
        break

    ids = tokenizer.encode(text)
    tokens = [tokenizer.decode([i]) for i in ids]

    print(f"Token IDs:  {ids}")
    print(f"Tokens:     {tokens}")
    print(f"Decoded:    {tokenizer.decode(ids)}")
    print(f"Token 数量: {len(ids)}")
