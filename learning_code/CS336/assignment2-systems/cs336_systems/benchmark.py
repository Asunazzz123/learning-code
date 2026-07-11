from cs336_basics.cs336_basics.model import TransformerBlock


class ModelParams:
    d_model: int
    d_ff: int
    num_layers: int
    num_heads: int

class ModelSize(ModelParams):
    def __init__(self,size):
        self.size = size
        self.vocab_size = 50257
        self.context_length = 2048
    def params(self):
        if self.size == "small":
            self.d_model = 768
            self.d_ff = 3072
            self.num_layers = 12
            self.num_heads = 12
        elif self.size == "medium":
            self.d_model = 1024
            self.d_ff = 4096
            self.num_layers = 124
            self.num_heads = 26
        elif self.size == "large":
            self.d_model = 1280
            self.d_ff = 5120
            self.num_layers = 36
            self.num_heads = 20
        elif self.size == "xl":
            self.d_model = 2560
            self.d_ff = 10240
            self.num_layers = 50
            self.num_heads = 36
        elif self.size == "10B":
            self.d_model = 4608
            self.d_ff = 12288
            self.num_layers = 50
            self.num_heads = 50



class Benchmarking(ModelParams):
    def __init__(self,size):
        ModelSize(size).params()

    def __model__(self):
        Transformer = TransformerBlock(
            self.d_model,
            self.num_heads,
            self.d_ff,
            self.
        )
        return Transformer
    

