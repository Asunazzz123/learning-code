
import os
os.environ['TORCHINDUCTOR_CACHE_DIR'] = '/tmp/rmsnorm_inductor_fresh_2'
os.environ['TORCH_COMPILE_DEBUG'] = '1'
os.environ['TORCH_LOGS'] = '+inductor,output_code,kernel_code,fusion'
os.environ['_TORCHINDUCTOR_PYOBJECT_TENSOR_DATA_PTR'] = '4454548596'

import torch
from torch import tensor, device
import torch.fx as fx
from torch._dynamo.testing import rand_strided
from math import inf
import torch._inductor.inductor_prims



import torch._dynamo.config
import torch._inductor.config
import torch._functorch.config
import torch.fx.experimental._config

torch._inductor.config.inplace_buffers = True
torch._inductor.config.deterministic = False
torch._inductor.config.comprehensive_padding = True
torch._inductor.config.triton.store_cubin = False
torch._inductor.config.trace.enabled = False
torch._inductor.config.trace.save_real_tensors = False
torch._functorch.config.functionalize_rng_ops = False
torch._functorch.config.debug_partitioner = False
torch._functorch.config.fake_tensor_allow_unsafe_data_ptr_access = True
torch._functorch.config.unlift_effect_tokens = False
torch._functorch.config.selective_decompose = False



isolate_fails_code_str = None





if "__compile_source__" in globals():
    import inspect as __after_aot_inspect
    import linecache as __after_aot_linecache
    __after_aot_filename = __after_aot_inspect.currentframe().f_code.co_filename
    __after_aot_linecache.cache[__after_aot_filename] = (
        len(__compile_source__),
        None,
        __compile_source__.splitlines(True),
        __after_aot_filename,
    )
# torch version: 2.11.0
# torch cuda version: None
# torch git version: 70d99e998b4955e0049d13a98d77ae1b14db1f45


# torch.cuda.is_available()==False, no GPU info collected
torch._higher_order_ops.triton_kernel_wrap.kernel_side_table.reset_table()

from torch.nn import *
class Repro(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()



    def forward(self, primals_1, primals_2, rsqrt, tangents_1):
        mul_2 = torch.ops.aten.mul.Tensor(tangents_1, primals_2);  primals_2 = None
        mul = torch.ops.aten.mul.Tensor(primals_1, rsqrt)
        mul_3 = torch.ops.aten.mul.Tensor(tangents_1, mul);  tangents_1 = mul = None
        sum_1 = torch.ops.aten.sum.dim_IntList(mul_3, [0, 1], True);  mul_3 = None
        view = torch.ops.aten.view.default(sum_1, [2560]);  sum_1 = None
        mul_4 = torch.ops.aten.mul.Tensor(mul_2, primals_1)
        mul_5 = torch.ops.aten.mul.Tensor(mul_2, rsqrt);  mul_2 = None
        sum_2 = torch.ops.aten.sum.dim_IntList(mul_4, [2], True);  mul_4 = None
        mul_6 = torch.ops.aten.mul.Scalar(sum_2, -0.5);  sum_2 = None
        pow_2 = torch.ops.aten.pow.Tensor_Scalar(rsqrt, 3);  rsqrt = None
        mul_7 = torch.ops.aten.mul.Tensor(mul_6, pow_2);  mul_6 = pow_2 = None
        expand = torch.ops.aten.expand.default(mul_7, [4, 512, 2560]);  mul_7 = None
        div = torch.ops.aten.div.Scalar(expand, 2560);  expand = None
        pow_3 = torch.ops.aten.pow.Tensor_Scalar(primals_1, 1.0);  primals_1 = None
        mul_8 = torch.ops.aten.mul.Scalar(pow_3, 2.0);  pow_3 = None
        mul_9 = torch.ops.aten.mul.Tensor(div, mul_8);  div = mul_8 = None
        add_1 = torch.ops.aten.add.Tensor(mul_5, mul_9);  mul_5 = mul_9 = None
        return (add_1, view)

def load_args(reader):
    buf0 = reader.storage(None, 20971520)
    reader.tensor(buf0, (4, 512, 2560), is_leaf=True)  # primals_1
    buf1 = reader.storage(None, 10240)
    reader.tensor(buf1, (2560,), is_leaf=True)  # primals_2
    buf2 = reader.storage(None, 8192)
    reader.tensor(buf2, (4, 512, 1), is_leaf=True)  # rsqrt
    buf3 = reader.storage(None, 20971520)
    reader.tensor(buf3, (4, 512, 2560), is_leaf=True)  # tangents_1
load_args._version = 0
mod = Repro()
if __name__ == '__main__':
    from torch._dynamo.repro.after_aot import run_repro
    with torch.no_grad():
        run_repro(mod, load_args, accuracy=False, command='run', save_dir=None, tracing_mode='real', check_str=None)
        # To run it separately, do 
        # mod, args = run_repro(mod, load_args, accuracy=False, command='get_args', save_dir=None, tracing_mode='real', check_str=None)
        # mod(*args)