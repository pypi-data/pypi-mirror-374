from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCSD_SetColor(int lineColor, int textColor, int backColor);
def HD调试_设置颜色(线颜色: int = 0x0000FF00, 文本颜色: int = 0x00FFFF00, 背景颜色: int = 0x00000000) -> int:
    """
    设置全局可视化标注颜色值（用于调试）
    
    Args:
        线颜色: 线条颜色，默认0x0000FF00
        文本颜色: 文本颜色，默认0x00FFFF00
        背景颜色: 背景颜色，默认0x00000000
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCSD_SetColor = hd.HCSD_SetColor
    HCSD_SetColor.restype = ctypes.c_int64
    HCSD_SetColor.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCSD_SetColor(
        ctypes.c_int32(线颜色),
        ctypes.c_int32(文本颜色),
        ctypes.c_int32(背景颜色)
    )
    return ret

# INT64 __stdcall HCSD_SetFollowClassTitleName(int pid, int hwnd, char* className, char* titleName);
def HD调试_设置调试窗口跟随(进程PID: int = None, 窗口句柄: int = None, 类名: str = None, 标题名: str = None) -> int:
    """
    设置当前调试窗口跟随的进程信息（用于调试）
    
    Args:
        进程PID: 指定pid，内部会配合类名或标题名找绑定的窗口句柄
        窗口句柄: 指定了窗口句柄，其他3个参数无效
        类名: 窗口类名，可以为None
        标题名: 窗口标题名，可以为None
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCSD_SetFollowClassTitleName = hd.HCSD_SetFollowClassTitleName
    HCSD_SetFollowClassTitleName.restype = ctypes.c_int64
    HCSD_SetFollowClassTitleName.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_char_p
    ]
    
    className_bytes = auto_encode(类名) if 类名 else None
    titleName_bytes = auto_encode(标题名) if 标题名 else None
    
    ret = HCSD_SetFollowClassTitleName(
        ctypes.c_int32(进程PID) if 进程PID else 0,
        ctypes.c_int32(窗口句柄) if 窗口句柄 else 0,
        className_bytes,
        titleName_bytes
    )
    return ret

# INT64 __stdcall HCSD_DrawWinodws(INT64 hwnd, int LineRgbColor, int lineSize, int type, int fillRgbColor);
def HD调试_标记窗口(窗口句柄: int, 线条RGB颜色: int, 线条大小: int, 类型: int = 0, 填充RGB颜色: int = 0) -> int:
    """
    给指定窗口画边框或者填充矩形
    
    Args:
        窗口句柄: 窗口句柄
        线条RGB颜色: 线条颜色
        线条大小: 线条大小
        类型: 0边框，1填充
        填充RGB颜色: 填充色RGB，type=1才有效
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCSD_DrawWinodws = hd.HCSD_DrawWinodws
    HCSD_DrawWinodws.restype = ctypes.c_int64
    HCSD_DrawWinodws.argtypes = [
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCSD_DrawWinodws(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(线条RGB颜色),
        ctypes.c_int32(线条大小),
        ctypes.c_int32(类型),
        ctypes.c_int32(填充RGB颜色)
    )
    return ret

# INT64 __stdcall HCHD_CatchException(BOOL bOpen);
def HD调试_捕捉异常调用堆栈(是否开启: bool = True) -> int:
    """
    开启/关闭捕捉异常调用堆栈
    
    Args:
        是否开启: 是否打开异常捕捉
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCHD_CatchException = hd.HCHD_CatchException
    HCHD_CatchException.restype = ctypes.c_int64
    HCHD_CatchException.argtypes = [
        ctypes.c_bool
    ]
    
    ret = HCHD_CatchException(ctypes.c_bool(是否开启))
    return ret

# INT64 __stdcall HCSD_SetAttachConsole(BOOL bOpen);
def HD调试_附加控制台(是否开启: bool = True) -> int:
    """
    开启/关闭附加控制台
    
    Args:
        是否开启: 是否打开控制台附加
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCSD_SetAttachConsole = hd.HCSD_SetAttachConsole
    HCSD_SetAttachConsole.restype = ctypes.c_int64
    HCSD_SetAttachConsole.argtypes = [
        ctypes.c_bool
    ]
    
    ret = HCSD_SetAttachConsole(ctypes.c_bool(是否开启))
    return ret