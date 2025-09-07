from .config import Config, ctypes
from .config import auto_encode

# 状态机回调类型定义
HCMTStatusFunType = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int64)

# INT64 __stdcall HCMT_DelayEx(int mis, BOOL bStatus);
def HD状态机_延迟Ex(毫秒: int, 是否状态机回调: bool = False) -> int:
    """
    延迟扩展版
    
    Args:
        毫秒: 毫秒延迟
        是否状态机回调: 是否状态机回调，默认为False，如果在状态机回调中调用，请置为True
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_DelayEx = hd.HCMT_DelayEx
    HCMT_DelayEx.restype = ctypes.c_int64
    HCMT_DelayEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_DelayEx(ctypes.c_int32(毫秒), ctypes.c_bool(是否状态机回调))
    return ret

# INT64 __stdcall HCMT_StartStatus();
def HD状态机_开启状态机() -> int:
    """
    开启状态机
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_StartStatus = hd.HCMT_StartStatus
    HCMT_StartStatus.restype = ctypes.c_int64
    HCMT_StartStatus.argtypes = []
    
    ret = HCMT_StartStatus()
    return ret

# INT64 __stdcall HCMT_AddStatus(INT64 funCallBack, INT64 lparam, BOOL bEnable, int statusType);
def HD状态机_添加状态机状态(状态回调: HCMTStatusFunType, 额外参数: int, 是否有效: bool, 状态值: int) -> int:
    """
    添加状态机状态
    
    Args:
        状态回调: 状态回调函数，例如：
            def callback_function(windowsIndex, lparam):
                print(f"Callback called with windowsIndex={windowsIndex}, lparam={lparam}")
                return 0  # 返回值类型为__int64
        额外参数: 额外参数，可以传递指针或者8字节数据，这个用户自定义参数会在触发回调的时候传递给回调的第二个形参
        是否有效: 状态是否有效，无效是不会触发状态回调的，即便是检索到这个状态的时候，也不会触发回调，只会不停判断
        状态值: 状态值，自定义值（内置：-1表示无状态，不要重复指定），大小决定优先级
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_AddStatus = hd.HCMT_AddStatus
    HCMT_AddStatus.restype = ctypes.c_int64
    HCMT_AddStatus.argtypes = [
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_bool,
        ctypes.c_int32
    ]
    
    heartFun = HCMTStatusFunType(状态回调)
    
    ret = HCMT_AddStatus(
        ctypes.cast(heartFun, ctypes.c_void_p).value,
        ctypes.c_int64(额外参数),
        ctypes.c_bool(是否有效),
        ctypes.c_int32(状态值)
    )
    return ret

# INT64 __stdcall HCMT_EnableStatus(int statusType, BOOL bEnable);
def HD状态机_操作状态(状态值: int, 是否有效: bool) -> int:
    """
    操作状态
    
    Args:
        状态值: 自定义的状态值
        是否有效: 是否有效
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_EnableStatus = hd.HCMT_EnableStatus
    HCMT_EnableStatus.restype = ctypes.c_int64
    HCMT_EnableStatus.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_EnableStatus(ctypes.c_int32(状态值), ctypes.c_bool(是否有效))
    return ret

# INT64 __stdcall HCMT_ChangeStatus(int statusType);
def HD状态机_改变当前状态(状态值: int) -> int:
    """
    改变当前状态
    
    Args:
        状态值: 自定义的状态值
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_ChangeStatus = hd.HCMT_ChangeStatus
    HCMT_ChangeStatus.restype = ctypes.c_int64
    HCMT_ChangeStatus.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_ChangeStatus(ctypes.c_int32(状态值))
    return ret

# INT64 __stdcall HCMT_RetraceStatus(BOOL bClear);
def HD状态机_回溯上个状态(是否清除: bool = False) -> int:
    """
    回溯上个状态
    
    Args:
        是否清除: True表示清除之前的栈缓存同时改变当前状态位-1（空），False表示清除当前栈顶的状态，相同的全部删除，同时改变当前状态为清除后的栈顶的那个状态
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_RetraceStatus = hd.HCMT_RetraceStatus
    HCMT_RetraceStatus.restype = ctypes.c_int64
    HCMT_RetraceStatus.argtypes = [
        ctypes.c_bool
    ]
    
    ret = HCMT_RetraceStatus(ctypes.c_bool(是否清除))
    return ret

# INT64 __stdcall HCMT_IsStatus();
def HD状态机_是否状态中() -> int:
    """
    当前状态机的状态在回调中是否有效
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_IsStatus = hd.HCMT_IsStatus
    HCMT_IsStatus.restype = ctypes.c_int64
    HCMT_IsStatus.argtypes = []
    
    ret = HCMT_IsStatus()
    return ret

# INT64 __stdcall HCMT_StatusSleep(int mis);
def HD状态机_状态延迟(毫秒: int) -> int:
    """
    状态延迟
    
    Args:
        毫秒: 毫秒延迟
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_StatusSleep = hd.HCMT_StatusSleep
    HCMT_StatusSleep.restype = ctypes.c_int64
    HCMT_StatusSleep.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_StatusSleep(ctypes.c_int32(毫秒))
    return ret

# INT64 __stdcall HCMT_GetStatus(int windowsIndex);
def HD状态机_获取当前状态(窗口索引: int) -> int:
    """
    获取当前状态
    
    Args:
        窗口索引: 窗口索引
    
    Returns:
        int: 当前状态值
    """
    hd = Config.get_hd()
    
    HCMT_GetStatus = hd.HCMT_GetStatus
    HCMT_GetStatus.restype = ctypes.c_int64
    HCMT_GetStatus.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_GetStatus(ctypes.c_int32(窗口索引))
    return ret