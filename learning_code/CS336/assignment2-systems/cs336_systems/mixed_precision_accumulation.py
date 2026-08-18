import torch

def tensor_gen(num:int,dtype1: torch.dtype,dtype2: torch.dtype) -> torch.tensor:
    s = torch.tensor(0,dtype=dtype1)
    for i in range(num):
        s += torch.tensor(0.01,dtype=dtype2)
    return s


if __name__ == "__main__":
    num = 1000
    print(tensor_gen(num,torch.float32,torch.float32))
    print(tensor_gen(num,torch.float32,torch.float16))
    print(tensor_gen(num,torch.float16,torch.float32))
    print(tensor_gen(num,torch.float16,torch.float16))
    # Result :
    ## num = 100
    # tensor(1.0000)
    # tensor(1.0002)
    # tensor(0.9883, dtype=torch.float16)
    # tensor(0.9883, dtype=torch.float16)
    ## num = 1000
    # tensor(10.0001)
    # tensor(10.0021)
    # tensor(9.9531, dtype=torch.float16)
    # tensor(9.9531, dtype=torch.float16)

