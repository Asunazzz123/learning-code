import re
from collections import OrderedDict
class Tokenizer:
    def __init__(self,vocab,merges,special_tokens = None):
        """Args:
        vocab (dict[int, bytes]): The tokenizer vocabulary, a mapping from int (token ID in the vocabulary)
            to bytes (token bytes)
        merges (list[tuple[bytes, bytes]]): BPE merges. Each list item is a tuple of bytes (<token1>, <token2>),
            representing that <token1> was merged with <token2>.
            Merges are ordered by order of creation.
        special_tokens (list[str] | None): A list of string special tokens for the tokenizer. These strings will never
            be split into multiple tokens, and will always be kept as a single token."""
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens or []
        self.byte_to_id = {v: k for k, v in vocab.items()}
        self.merge_ranks = {pair: rank for rank, pair in enumerate(merges)}
        
    def _token_split_special_token(self,text: str) -> list[tuple[bytes,bytes]]:
        if not self.special_tokens:
            return [(text, False)]
        special_tokens = sorted(self.special_tokens, key = len , reverse= True)
        pattern = "(" + "|".join(re.escape(token) for token in self.special_tokens) + ")"
        parts = re.split(pattern, text)
        special_set = set(self.special_tokens)
        return [
            (part, part in special_set)
            for part in parts
            if part != ""
        ]

    def _bpe_encoder(self,raw_byte: bytes):
        tokens = [bytes([b]) for b in raw_byte]

        while True:
            if len(tokens) < 2:
                break
            pairs = [tokens[i] + tokens[i+1] for i in range(len(tokens) - 1)]
            candidate = [pair for pair in pairs if pair in self.merge_ranks]

            if not candidate:
                break
            
            best_pair = min(candidate, key = lambda pair: self.merge_ranks[pair])

            new_tokens = []
            i = 0
            while i < len(tokens):
                if ( i < len(tokens) - 1 and tokens[i] + tokens[i+1] == best_pair):
                    new_tokens.append(tokens[i] + tokens[i+1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        return tokens
                
            

    def encode(self,text: str) -> list[int]:
        token_ids = []
        for piece, is_special in self._token_split_special_token(text):
            if piece == "":
                continue
            
            if is_special:
                token_bytes = piece.encode("utf-8")
                token_ids.append(self.byte_to_id[token_bytes])
            
            else:
                token_bytes = piece.encode("utf-8")
                tokens = self._bpe_encoder(token_bytes)
                token_ids.extend(self.byte_to_id[token] for token in tokens)
        return token_ids
    

        # pass

    def decode(self,ids: list[int]) -> str:
        raw_bytes = b"".join(self.vocab[token_id] for token_id in ids)
        return raw_bytes.decode("utf-8", errors="replace")
        # pass