import re
from collections import OrderedDict
class Tokenizer:
    def __init__(self,vocab,merges,special_token = None):
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
        self.special_token = special_token or []
        self.byte_to_id = OrderedDict
        self.merge_ranks = OrderedDict

    def encode(self,text:str):
        tokens = [bytes([b]) for b in text.encode("utf-8")]
        while True:
            if len(tokens) < 2:
                break
            pairs = [
                (tokens[i], tokens[i + 1])
                for i in range(len(tokens) - 1)
            ]
            candidates = [
                pair for pair in pairs
                if pair in self.merge_ranks
            ]
            if not candidates:
                break
            best_pair = min(candidates, key=lambda pair: self.merge_ranks[pair])
            new_tokens = []
            i = 0
            while i < len(tokens):
                if (
                    i < len(tokens) - 1
                    and tokens[i] == best_pair[0]
                    and tokens[i + 1] == best_pair[1]
                ):
                    new_tokens.append(tokens[i] + tokens[i + 1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        return [self.byte_to_id[token] for token in tokens]
    def _add_special_token(self):
        for token in self.special_token:
            if token not in self.byte_to_id:
                

        # pass
    def decode(self,token):
        pass 

    def _merge_token(self,tokens,new_token):
        merge_token = []
        i = 0

        while i < len(tokens):
            if i+1 < len(tokens) and tokens[i]+ tokens[i+1] == new_token:
                merge_token.append(tokens[i]+tokens[i+1])
            else:
                merge_token.append(tokens[i])

        return merge_token
    def _pair_stat(self,tokens,stat):
        for i in range(len(tokens)-1):
            new_token = tokens[i] + tokens[i+1]
            if new_token not in stat:
                stat[new_token] = 0
            stat[new_token] += 1

    
             
