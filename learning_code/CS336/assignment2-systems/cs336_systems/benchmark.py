from cs336_basics.model import BasicsTransformerLM
from cs336_basics.nn_utils import cross_entropy
from cs336_basics.optimizer import AdamW
import timeit
import torch
import numpy as np
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
        if self.size == "small":
                    self.d_model = 768
                    self.d_ff = 3072
                    self.num_layers = 12
                    self.num_heads = 12
        elif self.size == "medium":
                    self.d_model = 1024
                    self.d_ff = 4096
                    self.num_layers = 24
                    self.num_heads = 16
        elif self.size == "large":
                    self.d_model = 1280
                    self.d_ff = 5120
                    self.num_layers = 36
                    self.num_heads = 20
        elif self.size == "xl":
                    self.d_model = 2560
                    self.d_ff = 10240
                    self.num_layers = 32
                    self.num_heads = 32
        elif self.size == "10B":
                    self.d_model = 4608
                    self.d_ff = 12288
                    self.num_layers = 50
                    self.num_heads = 36
        



class Benchmarking(ModelSize):
    def __init__(self,size,device,batch_size = 4):
        super().__init__(size)
        self.device = device
        self.batch_size = batch_size
    def __model__(self):
        Transformer = BasicsTransformerLM(
            self.vocab_size,
            self.context_length,
            self.d_model,
            self.num_layers,
            self.num_heads,
            self.d_ff
        )
        Transformer.to(device=self.device)
        return Transformer
    

    def data_generate(self):
        gen = torch.randint(
               low = 0,
               high = self.vocab_size,
               size = (self.batch_size,self.context_length+1),
               dtype = torch.int64,
               device = self.device
            )

        x = gen[:,0:-1]
        y = gen[:,1:]
        return x,y

    def warmup_test(self,mode,wstep=5,nstep=10):
        model = self.__model__()
        x,y = self.data_generate()
        time = []
        if mode == "forward-only":
            for i in range(wstep):
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                logits = model(x)
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
            for i in range(nstep):
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                start = timeit.default_timer()
                logits = model(x)
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device) 
                end = timeit.default_timer()
                time.append(end - start)

        elif mode == "forward and backward":
    
            for i in range(wstep):
                model.zero_grad()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                logits = model(x)
                loss = cross_entropy(logits,y)
                loss.backward()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
            for i in range(nstep):
                model.zero_grad()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                start = timeit.default_timer()
                logits = model(x)
                loss = cross_entropy(logits,y)
                loss.backward()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device) 
                end = timeit.default_timer()
                time.append(end - start)

        elif mode == "forward and backward with optimizer":
            optimizer = AdamW(model.parameters())
            for i in range(wstep):
                optimizer.zero_grad()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                logits = model(x)
                loss = cross_entropy(logits,y)
                loss.backward()
                optimizer.step()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
            for i in range(nstep):
                optimizer.zero_grad()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device)
                start = timeit.default_timer()
                logits = model(x)
                loss = cross_entropy(logits,y)
                loss.backward()
                optimizer.step()
                if self.device.type == "cuda":
                    torch.cuda.synchronize(device=self.device) 
                end = timeit.default_timer()
                time.append(end - start)
        else:
               raise(IndexError("Mode Error"))
        time = np.array(time,dtype=np.float64)
        mean = time.mean()
        std = time.std()
        return mean,std
        
        




    

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    b = Benchmarking(size="small",device=device)
    x,y = b.data_generate()
    print(x.dtype)
    print(x.shape)
    print(y.shape)
    


