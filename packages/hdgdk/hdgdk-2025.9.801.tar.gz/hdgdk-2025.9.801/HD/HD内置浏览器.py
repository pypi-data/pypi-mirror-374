from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCGB_Attach1(int winIndex);
def HD内置浏览器_附加谷歌1(窗口序号: int) -> int:
    """
    附加内置浏览器（附加监听模式1）
    
    Args:
        窗口序号: 窗口序号（从1开始）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCGB_Attach1 = hd.HCGB_Attach1
    HCGB_Attach1.restype = ctypes.c_int64
    HCGB_Attach1.argtypes = [ctypes.c_int32]
    
    ret = HCGB_Attach1(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCGB_Attach2(int winIndex);
def HD内置浏览器_附加谷歌2(窗口序号: int) -> int:
    """
    附加内置浏览器（附加监听模式2）
    
    Args:
        窗口序号: 窗口序号（从1开始）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCGB_Attach2 = hd.HCGB_Attach2
    HCGB_Attach2.restype = ctypes.c_int64
    HCGB_Attach2.argtypes = [ctypes.c_int32]
    
    ret = HCGB_Attach2(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCGB_Detach(int winIndex);
def HD内置浏览器_脱离谷歌(窗口序号: int) -> int:
    """
    脱离之前的内置浏览器
    
    Args:
        窗口序号: 窗口序号（从1开始）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCGB_Detach = hd.HCGB_Detach
    HCGB_Detach.restype = ctypes.c_int64
    HCGB_Detach.argtypes = [ctypes.c_int32]
    
    ret = HCGB_Detach(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCGB_InjectJSCode(int winIndex, char* codeBuffer, BOOL mainThread);
def HD内置浏览器_注入谷歌JS代码(窗口序号: int, JS代码: str, 是否主线程: bool = False) -> int:
    """
    给内置浏览器注入JS代码
    
    Args:
        窗口序号: 窗口序号（从1开始）
        JS代码: JS代码内容
        是否主线程: 是否在主线程执行，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCGB_InjectJSCode = hd.HCGB_InjectJSCode
    HCGB_InjectJSCode.restype = ctypes.c_int64
    HCGB_InjectJSCode.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCGB_InjectJSCode(
        ctypes.c_int32(窗口序号),
        auto_encode(JS代码),
        ctypes.c_bool(是否主线程)
    )
    return ret

# INT64 __stdcall HCGB_ExcuteJSFile(int winIndex, char* fileName, BOOL mainThread);
def HD内置浏览器_注入谷歌JS文件(窗口序号: int, JS文件路径: str, 是否主线程: bool = False) -> int:
    """
    给内置浏览器注入指定文件中的JS代码
    
    Args:
        窗口序号: 窗口序号（从1开始）
        JS文件路径: JS文件的完整路径
        是否主线程: 是否在主线程执行，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCGB_ExcuteJSFile = hd.HCGB_ExcuteJSFile
    HCGB_ExcuteJSFile.restype = ctypes.c_int64
    HCGB_ExcuteJSFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCGB_ExcuteJSFile(
        ctypes.c_int32(窗口序号),
        auto_encode(JS文件路径),
        ctypes.c_bool(是否主线程)
    )
    return ret