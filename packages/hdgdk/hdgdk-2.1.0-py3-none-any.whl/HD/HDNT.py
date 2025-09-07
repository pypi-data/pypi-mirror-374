from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCNT_GetWindowProcessId(INT64 hwnd);
def HDNT_窗口句柄取PID(窗口句柄: int) -> int:
    """
    获取目标窗口句柄的进程ID（R3层内核版本）
    
    Args:
        窗口句柄: 目标窗口的句柄值
    
    Returns:
        int: 进程ID（查看HD返回值表）
    
    Note:
        可以绕过一些检测，比如NP等
    """
    hd = Config.get_hd()
    
    HCNT_GetWindowProcessId = hd.HCNT_GetWindowProcessId
    HCNT_GetWindowProcessId.restype = ctypes.c_int64
    HCNT_GetWindowProcessId.argtypes = [ctypes.c_int64]
    
    ret = HCNT_GetWindowProcessId(ctypes.c_int64(窗口句柄))
    return ret