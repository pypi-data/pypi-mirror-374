from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HC_OpenCPU(int winIndex, BOOL mainThread);
def HD优化_开启CPU(窗口序号: int, 是否主线程: bool = False) -> int:
    """
    开启CPU优化
    
    Args:
        窗口序号: 窗口序号（从1开始）
        是否主线程: 是否需要主线程来调用这个CALL
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HC_OpenCPU = hd.HC_OpenCPU
    HC_OpenCPU.restype = ctypes.c_int64
    HC_OpenCPU.argtypes = [ctypes.c_int32, ctypes.c_bool]
    
    ret = HC_OpenCPU(ctypes.c_int32(窗口序号), ctypes.c_bool(是否主线程))
    return ret

# INT64 __stdcall HC_SetFPS(int winIndex, int fps);
def HD优化_设置FPS(窗口序号: int, 帧数: int = 0) -> int:
    """
    设置帧数（绑定dx.public.down.cpu后台属性有效）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        帧数: 帧数（大于120表示关闭优化，可以用来在绑定后台的情况下关闭优化）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HC_SetFPS = hd.HC_SetFPS
    HC_SetFPS.restype = ctypes.c_int64
    HC_SetFPS.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HC_SetFPS(ctypes.c_int32(窗口序号), ctypes.c_int32(帧数))
    return ret


# __int64 __stdcall  HC_SetCpuDwonMs(__int32 窗口序号, __int32 downMs = 0);
def HD优化_设置延迟(窗口序号: int, downMs: int = 0) -> int:
    """
    设置延迟（绑定dx.public.down.cpu后台属性有效）

    Args:
        窗口序号: 窗口序号（从1开始）
        downMs:延迟毫秒数(自行根据实际情况而定一般在1ms到50ms之间)

    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HC_SetCpuDwonMs = hd.HC_SetCpuDwonMs
    HC_SetCpuDwonMs.restype = ctypes.c_int64
    HC_SetCpuDwonMs.argtypes = [ctypes.c_int32, ctypes.c_int32]

    ret = HC_SetCpuDwonMs(ctypes.c_int32(窗口序号), ctypes.c_int32(downMs))
    return ret


# INT64 __stdcall HC_CloseCPU(int winIndex, BOOL mainThread);
def HD优化_关闭CPU(窗口序号: int, 是否主线程: bool = False) -> int:
    """
    关闭CPU优化
    
    Args:
        窗口序号: 窗口序号（从1开始）
        是否主线程: 是否需要主线程来调用这个CALL
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HC_CloseCPU = hd.HC_CloseCPU
    HC_CloseCPU.restype = ctypes.c_int64
    HC_CloseCPU.argtypes = [ctypes.c_int32, ctypes.c_bool]
    
    ret = HC_CloseCPU(ctypes.c_int32(窗口序号), ctypes.c_bool(是否主线程))
    return ret