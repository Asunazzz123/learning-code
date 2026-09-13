"""
Memory Profiling
"""
import torch
import time

from contextlib import contextmanager

class MemoryProfiler():
    def __init__(self,device:torch.device):
        self.device = device
        self.periodmem : dict = {}


    @contextmanager
    def phase(self, period: str):
        """
        绑定阶段的显存分配占用读取
        """
        torch.cuda.synchronize(self.device)
        start = torch.cuda.memory_allocated(self.device)
        torch.cuda.reset_peak_memory_stats(self.device)
        try:
            yield
        finally:
            torch.cuda.synchronize(self.device)
            self.periodmem[period] = {
                "start_allocated" : start,
                "end_allocated" : torch.cuda.memory_allocated(self.device),
                "peak_allocated" : torch.cuda.max_memory_allocated(self.device)
            }

    def start_profiling(self,stat = "all"):
        """
        开启显存分配器的详细事件记录
        """
        torch.cuda.memory._record_memory_history(stat)

    def end_profiling(self):
        """
        关闭显存分配器
        """
        torch.cuda.memory._record_memory_history(enabled=None)

    def snap(self,path):
        torch.cuda.memory._dump_snapshot(path)


    def tensor_mem(self, tensor: torch.Tensor):
        # 输入三维张量的显存占用计算，
        # 计算方式为 tensor size * dtype 的占用，假设 tensor.shape为 m,n, d_model. 精度为 FP32. 则显存占用为 m*m*d_model*32bit
        return tensor.nbytes / (1024**2)


