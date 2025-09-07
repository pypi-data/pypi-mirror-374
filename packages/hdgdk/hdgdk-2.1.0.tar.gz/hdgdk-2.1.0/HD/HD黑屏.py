from .config import Config, ctypes
from .config import auto_encode

# __int64 __stdcall HC_OpenBS(__int32 窗口序号, __int32 minIndex = 0, __int32 maxIndex = 0, BOOL 是否主线程调用 = FALSE);
def HD黑屏_打开(窗口序号: int, minIndex: int = 0, maxIndex: int = 0, 是否主线程调用: bool = False) -> int:
    """
    打开黑屏
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        minIndex: 最小模型序号 (默认0)
        maxIndex: 最大模型序号 (默认0)
        是否主线程调用: 是否需要主线程来调用这个CALL (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_OpenBS
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]

    return func(窗口序号, minIndex, maxIndex, 是否主线程调用)

# __int64 __stdcall HC_SetBs(__int32 窗口序号, __int32 minIndex = 0, __int32 maxIndex = 0);
def HD黑屏_设置模型范围(窗口序号: int, minIndex: int = 0, maxIndex: int = 0) -> int:
    """
    设置模型序号的过滤范围
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        minIndex: 最小模型序号 (默认0)
        maxIndex: 最大模型序号 (默认0)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_SetBs
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

    return func(窗口序号, minIndex, maxIndex)

# __int64 __stdcall HC_CloseBS(__int32 窗口序号, BOOL 是否主线程调用 = FALSE);
def HD黑屏_关闭(窗口序号: int, 是否主线程调用: bool = False) -> int:
    """
    关闭黑屏
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        是否主线程调用: 是否需要主线程来调用这个CALL (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_CloseBS
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_bool]

    return func(窗口序号, 是否主线程调用)