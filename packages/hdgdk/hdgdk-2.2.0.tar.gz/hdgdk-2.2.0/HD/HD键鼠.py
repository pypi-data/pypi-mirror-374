from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCMKB_Bind(int windowsIndex, INT64 hwnd, char* bindConfig);
def HD键鼠_绑定(窗口序号: int, 窗口句柄: int, 绑定属性: str = None) -> int:
    """
    绑定窗口
    
    Args:
        窗口序号: 窗口序号（从1开始）
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为None表示全部选中
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_Bind = hd.HCMKB_Bind
    HCMKB_Bind.restype = ctypes.c_int64
    HCMKB_Bind.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
    
    绑定属性字节 = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_Bind(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性字节
    )
    return ret

# INT64 __stdcall HCMKB_BindEx(int windowsIndex, INT64 hwnd, char* bindConfig, int bRetMove);
def HD键鼠_绑定Ex(窗口序号: int, 窗口句柄: int, 绑定属性: str = None, 是否刷新: int = 1) -> int:
    """
    绑定窗口（扩展版本）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为None表示全部选中
        是否刷新: 是否刷新窗口，有些窗口需要刷新后台键鼠才正常，默认1
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_BindEx = hd.HCMKB_BindEx
    HCMKB_BindEx.restype = ctypes.c_int64
    HCMKB_BindEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32]
    
    绑定属性字节 = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_BindEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性字节,
        ctypes.c_int32(是否刷新)
    )
    return ret

# INT64 __stdcall HCMKB_BindModeEx(int windowsIndex, INT64 hwnd, char* bindConfig, int mode, int bRetMove);
def HD键鼠_模式绑定Ex(窗口序号: int, 窗口句柄: int, 绑定属性: str = None, 模式: int = 0, 是否刷新: int = 1) -> int:
    """
    绑定窗口（扩展接口）
    
    Args:
        窗口序号: 窗口序号
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为None表示全部选中
        模式: 0通用模式效果最好，1（0模式不行可以试一试这个1），2，3，后续会进一步测试更多的模式
        是否刷新: 是否刷新窗口，有些窗口需要刷新后台键鼠才正常
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_BindModeEx = hd.HCMKB_BindModeEx
    HCMKB_BindModeEx.restype = ctypes.c_int64
    HCMKB_BindModeEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    绑定属性字节 = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_BindModeEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性字节,
        ctypes.c_int32(模式),
        ctypes.c_int32(是否刷新)
    )
    return ret

# INT64 __stdcall HCMKB_SwitchBind(int windowsIndex, INT64 hwnd, char* bindString);
def HD键鼠_切换绑定(窗口序号: int, 窗口句柄: int, 绑定属性: str = None) -> int:
    """
    切换绑定到所属子窗口的句柄上
    
    Args:
        窗口序号: 窗口序号
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为NULL表示全部选中
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_SwitchBind = hd.HCMKB_SwitchBind
    HCMKB_SwitchBind.restype = ctypes.c_int64
    HCMKB_SwitchBind.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
    
    绑定属性_bytes = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_SwitchBind(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性_bytes
    )
    return ret

# INT64 __stdcall HCMKB_SwitchBindEx(int windowsIndex, INT64 hwnd, char* bindString, int bRetMove);
def HD键鼠_切换绑定Ex(窗口序号: int, 窗口句柄: int, 绑定属性: str = None, 是否刷新: int = 1) -> int:
    """
    切换绑定到所属子窗口的句柄上
    
    Args:
        窗口序号: 窗口序号
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为NULL表示全部选中
        是否刷新: 是否刷新窗口，有些窗口需要刷新后台键鼠才正常
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_SwitchBindEx = hd.HCMKB_SwitchBindEx
    HCMKB_SwitchBindEx.restype = ctypes.c_int64
    HCMKB_SwitchBindEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32]
    
    绑定属性_bytes = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_SwitchBindEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性_bytes,
        ctypes.c_int32(是否刷新)
    )
    return ret

# INT64 __stdcall HCMKB_SwitchBindModeEx(int windowsIndex, INT64 hwnd, char* bindString, int mode, int bRetMove);
def HD键鼠_切换模式绑定Ex(窗口序号: int, 窗口句柄: int, 绑定属性: str = None, 模式: int = 0, 是否刷新: int = 1) -> int:
    """
    切换绑定窗口（扩展接口）
    
    Args:
        窗口序号: 窗口序号
        窗口句柄: 窗口句柄
        绑定属性: 20个值，1是选中，0未选中，为NULL表示全部选中
        模式: 0通用模式效果最好，1（0模式不行可以试一试这个1），2，后续会进一步测试更多的模式
        是否刷新: 是否刷新窗口，有些窗口需要刷新后台键鼠才正常
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_SwitchBindModeEx = hd.HCMKB_SwitchBindModeEx
    HCMKB_SwitchBindModeEx.restype = ctypes.c_int64
    HCMKB_SwitchBindModeEx.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    绑定属性_bytes = auto_encode(绑定属性) if 绑定属性 else None
    
    ret = HCMKB_SwitchBindModeEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(窗口句柄),
        绑定属性_bytes,
        ctypes.c_int32(模式),
        ctypes.c_int32(是否刷新)
    )
    return ret

# INT64 __stdcall HCMKB_PauseBind(int windowsIndex, int bPause, int bRetMove);
def HD键鼠_暂停绑定(窗口序号: int, 是否暂停: bool = True, 是否刷新: int = 1) -> int:
    """
    暂停/恢复后台绑定
    
    Args:
        窗口序号: 窗口序号
        是否暂停: 是否暂停
        是否刷新: 是否刷新窗口，有些窗口需要刷新后台键鼠才正常
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_PauseBind = hd.HCMKB_PauseBind
    HCMKB_PauseBind.restype = ctypes.c_int64
    HCMKB_PauseBind.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_PauseBind(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(是否暂停),
        ctypes.c_int32(是否刷新)
    )
    return ret

# INT64 __stdcall HCMKB_UnBind(int windowsIndex);
def HD键鼠_解绑(窗口序号: int) -> int:
    """
    解绑窗口
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_UnBind = hd.HCMKB_UnBind
    HCMKB_UnBind.restype = ctypes.c_int64
    HCMKB_UnBind.argtypes = [ctypes.c_int32]
    
    ret = HCMKB_UnBind(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMKB_MoveTo(int windowsIndex, int x, int y, BOOL bTrace, int traceType, int windowState);
def HD键鼠_鼠标移动(窗口序号: int, X坐标: int, Y坐标: int, 是否模拟鼠标轨迹: bool = True, 轨迹类型: int = -1, 窗口状态: int = -1) -> int:
    """
    鼠标移动
    
    Args:
        窗口序号: 窗口序号
        X坐标: 窗口客户区坐标x
        Y坐标: 窗口客户区坐标y
        是否模拟鼠标轨迹: 是否模拟鼠标轨迹
        轨迹类型: 轨迹类型，默认-1或1表示随机轨迹，2表示直线轨迹
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_MoveTo = hd.HCMKB_MoveTo
    HCMKB_MoveTo.restype = ctypes.c_int64
    HCMKB_MoveTo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_MoveTo(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(X坐标),
        ctypes.c_int32(Y坐标),
        ctypes.c_bool(是否模拟鼠标轨迹),
        ctypes.c_int32(轨迹类型),
        ctypes.c_int32(窗口状态)
    )
    return ret


# INT64 __stdcall HCMKB_MoveR(int windowsIndex, int x, int y, BOOL bTrace, int traceType, int windowState);
def HD键鼠_鼠标相对移动(窗口序号: int, X坐标: int, Y坐标: int, 是否模拟鼠标轨迹: bool = True, 轨迹类型: int = -1, 窗口状态: int = -1) -> int:
    """
    鼠标移动

    Args:
        窗口序号: 窗口序号
        X坐标: 基于窗口客户区坐标x的当前坐标的水平偏移
        Y坐标: 基于窗口客户区坐标y的当前坐标的垂直偏移
        是否模拟鼠标轨迹: 是否模拟鼠标轨迹
        轨迹类型: 轨迹类型，默认-1或1表示随机轨迹，2表示直线轨迹
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置

    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HCMKB_MoveR = hd.HCMKB_MoveR
    HCMKB_MoveR.restype = ctypes.c_int64
    HCMKB_MoveR.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool, ctypes.c_int32,
                             ctypes.c_int32]

    ret = HCMKB_MoveR(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(X坐标),
        ctypes.c_int32(Y坐标),
        ctypes.c_bool(是否模拟鼠标轨迹),
        ctypes.c_int32(轨迹类型),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_KeyUp(int windowsIndex, int virtualKeyCode, int windowState);
def HD键鼠_按键弹起(窗口序号: int, 虚拟键码: int, 窗口状态: int = -1) -> int:
    """
    弹起某个键
    
    Args:
        窗口序号: 窗口序号
        虚拟键码: 虚拟键码
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_KeyUp = hd.HCMKB_KeyUp
    HCMKB_KeyUp.restype = ctypes.c_int64
    HCMKB_KeyUp.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_KeyUp(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟键码),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_KeyDown(int windowsIndex, int virtualKeyCode, int windowState);
def HD键鼠_按键按下(窗口序号: int, 虚拟键码: int, 窗口状态: int = -1) -> int:
    """
    按下某个键
    
    Args:
        窗口序号: 窗口序号
        虚拟键码: 虚拟键码
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_KeyDown = hd.HCMKB_KeyDown
    HCMKB_KeyDown.restype = ctypes.c_int64
    HCMKB_KeyDown.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_KeyDown(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟键码),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_LeftUp(int windowsIndex, int windowState);
def HD键鼠_左键弹起(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标左键弹起
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_LeftUp = hd.HCMKB_LeftUp
    HCMKB_LeftUp.restype = ctypes.c_int64
    HCMKB_LeftUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_LeftUp(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_LeftDown(int windowsIndex, int windowState);
def HD键鼠_左键按下(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标左键按下
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_LeftDown = hd.HCMKB_LeftDown
    HCMKB_LeftDown.restype = ctypes.c_int64
    HCMKB_LeftDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_LeftDown(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_LeftClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_左键点击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标左键点击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_LeftClick = hd.HCMKB_LeftClick
    HCMKB_LeftClick.restype = ctypes.c_int64
    HCMKB_LeftClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_LeftClick(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(延时毫秒),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_LeftDoubleClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_左键双击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标左键双击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCMKB_LeftDoubleClick = hd.HCMKB_LeftDoubleClick
    HCMKB_LeftDoubleClick.restype = ctypes.c_int64
    HCMKB_LeftDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCMKB_LeftDoubleClick(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(延时毫秒),
        ctypes.c_int32(窗口状态)
    )
    return ret

# INT64 __stdcall HCMKB_MiddleUp(int windowsIndex, int windowState);
def HD键鼠_中键弹起(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标中键弹起
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_MiddleUp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_MiddleDown(int windowsIndex, int windowState);
def HD键鼠_中键按下(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标中键按下
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_MiddleDown
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_MiddleClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_中键点击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标中键点击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_MiddleClick
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_MiddleDoubleClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_中键双击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标中键双击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_MiddleDoubleClick
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_RightUp(int windowsIndex, int windowState);
def HD键鼠_右键弹起(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标右键弹起
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_RightUp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_RightDown(int windowsIndex, int windowState);
def HD键鼠_右键按下(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标右键按下
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_RightDown
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_RightClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_右键点击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标右键点击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_RightClick
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_RightDoubleClick(int windowsIndex, int delayMs, int windowState);
def HD键鼠_右键双击(窗口序号: int, 延时毫秒: int = 50, 窗口状态: int = -1) -> int:
    """
    鼠标右键双击
    
    Args:
        窗口序号: 窗口序号
        延时毫秒: 延时毫秒（默认50毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_RightDoubleClick
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_WheelUp(int windowsIndex, int windowState);
def HD键鼠_滚轮向上(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标滚轮向上滚动
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_WheelUp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_WheelDown(int windowsIndex, int windowState);
def HD键鼠_滚轮向下(窗口序号: int, 窗口状态: int = -1) -> int:
    """
    鼠标滚轮向下滚动
    
    Args:
        窗口序号: 窗口序号
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_WheelDown
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 窗口状态)

# INT64 __stdcall HCMKB_KeyPress(int windowsIndex, int virtualKeyCode, int delayMs, int windowState);
def HD键鼠_按键(窗口序号: int, 虚拟键码: int, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    """
    按下某个键
    
    Args:
        窗口序号: 窗口序号
        虚拟键码: 虚拟键码
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_KeyPress
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 虚拟键码, 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_KeyPressA(int windowsIndex, char* text, int delayMs, int windowState);
def HD键鼠_连续按键A(窗口序号: int, 文本: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    """
    连续按键输入字符串（连续单个按键）
    
    Args:
        窗口序号: 窗口序号
        文本: 要输入的字符串（ASCII字符）
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_KeyPressA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, auto_encode(文本), 延时毫秒, 窗口状态)

# INT64 __stdcall HCMKB_KeyPressW(int windowsIndex, wchar_t* text, int delayMs, int windowState);
def HD键鼠_连续按键W(窗口序号: int, 文本: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    """
    连续按键输入字符串（连续单个按键）
    
    Args:
        窗口序号: 窗口序号
        文本: 要输入的字符串（Unicode字符）
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCMKB_KeyPressW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int]
    
    return func(窗口序号, 文本, 延时毫秒, 窗口状态)

def HD键鼠_发送文本A(窗口序号: int, 文本A: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendStringA(INT32 窗口序号, LPCSTR 文本A, INT32 延时毫秒, INT32 窗口状态);
    """
    发送Ascii字符串 (不同于连续单个按键)
    
    Args:
        窗口序号: 窗口序号
        文本A: 文本(Ascii)
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendStringA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, auto_encode(文本A), 延时毫秒, 窗口状态)

def HD键鼠_发送文本W(窗口序号: int, 文本W: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendStringW(INT32 窗口序号, LPCWSTR 文本W, INT32 延时毫秒, INT32 窗口状态);
    """
    发送Unicode字符串 (不同于连续单个按键)
    
    Args:
        窗口序号: 窗口序号
        文本W: 文本(Unicode)
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendStringW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, 文本W, 延时毫秒, 窗口状态)

def HD键鼠_发送文本1(窗口序号: int, 文本A: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendString(INT32 窗口序号, LPCSTR 文本A, INT32 延时毫秒, INT32 窗口状态);
    """
    发送Ascii字符串
    
    Args:
        窗口序号: 窗口序号
        文本A: 文本(Ascii)
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendString
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, auto_encode(文本A), 延时毫秒, 窗口状态)

def HD键鼠_发送文本2(窗口序号: int, 文本A: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendString2(INT32 窗口序号, LPCSTR 文本A, INT32 延时毫秒, INT32 窗口状态);
    """
    发送Ascii字符串
    
    Args:
        窗口序号: 窗口序号
        文本A: 文本(Ascii)
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendString2
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, auto_encode(文本A), 延时毫秒, 窗口状态)

def HD键鼠_剪切板发送文本(窗口序号: int, 发送字节缓冲区: bytes, 发送字节大小: int, 文本类型: int, mis: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendPaste(INT32 窗口序号, LPVOID 发送字节缓冲区, INT32 发送字节大小, INT32 文本类型, INT32 mis, INT32 窗口状态);
    """
    发送剪切板字符串内容到窗口
    
    Args:
        窗口序号: 窗口序号
        发送字节缓冲区: 发送字节缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        发送字节大小: 发送字节缓冲区的字节大小
        文本类型: Ascii(1)  Unicode(2)
        mis: 延时毫秒
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendPaste
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    buffer = ctypes.c_char_p(发送字节缓冲区)
    
    return func(窗口序号, buffer, 发送字节大小, 文本类型, mis, 窗口状态)

def HD键鼠_剪切板发送文本Ex(窗口序号: int, 发送字节缓冲区: bytes, 发送字节大小: int, 文本类型: int, bSend: int = 0, mis: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendPasteEx(INT32 窗口序号, LPVOID 发送字节缓冲区, INT32 发送字节大小, INT32 文本类型, INT32 bSend, INT32 mis, INT32 窗口状态);
    """
    发送剪切板字符串内容到窗口
    
    Args:
        窗口序号: 窗口序号
        发送字节缓冲区: 发送字节缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        发送字节大小: 发送字节缓冲区的字节大小
        文本类型: Ascii(1)  Unicode(2)
        bSend: 是否消息发送的方式传递文本,如果为假表示粘贴到文本框
        mis: 延时毫秒
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendPasteEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    buffer = ctypes.c_char_p(发送字节缓冲区)
    
    return func(窗口序号, buffer, 发送字节大小, 文本类型, bSend, mis, 窗口状态)

def HD键鼠_剪切板发送随机文本(窗口序号: int, bSend: int = 0, mis: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendRoundNamePaste(INT32 窗口序号, INT32 bSend, INT32 mis, INT32 窗口状态);
    """
    发送随机名字,从2个文本(hf.txt 和 he.txt )中各获取一个字
    
    Args:
        窗口序号: 窗口序号
        bSend: 是否消息发送的方式传递文本,如果为假表示粘贴到文本框
        mis: 延时毫秒
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendRoundNamePaste
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, bSend, mis, 窗口状态)

def HD键鼠_设置剪切板文本(发送字节缓冲区: bytes, 发送字节大小: int, 文本类型: int) -> int:
    # INT64 __stdcall HCMKB_SetClipboard(LPVOID 发送字节缓冲区, INT32 发送字节大小, INT32 文本类型);
    """
    设置剪切板字符串
    
    Args:
        发送字节缓冲区: 发送字节缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        发送字节大小: 发送字节缓冲区的字节大小
        文本类型: Ascii(1)  Unicode(2)  Utf-8(3)
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SetClipboard
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
    
    buffer = ctypes.c_char_p(发送字节缓冲区)
    
    return func(buffer, 发送字节大小, 文本类型)

def HD键鼠_获取剪切板字符串(文本类型: int) -> int:
    # INT64 __stdcall HCMKB_GetClipboard(INT32 文本类型);
    """
    获取剪切板字符串
    
    Args:
        文本类型: Ascii(1)  Unicode(2)
        
    Returns:
        int: 剪切板字符串
    """
    hd = Config.get_hd()
    func = hd.HCMKB_GetClipboard
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32]
    
    return func(文本类型)

def HD键鼠_句柄发送文本(hwnd: int, 文本A: str, 延时毫秒: int = 20, 窗口状态: int = -1) -> int:
    # INT64 __stdcall HCMKB_SendStringF(INT64 hwnd, LPCSTR 文本A, INT32 延时毫秒, INT32 窗口状态);
    """
    发送Ascii字符串,部分游戏需要激活窗口！（可以不用通讯调用）
    
    Args:
        hwnd: hwnd窗口句柄
        文本A: 文本(Ascii)
        延时毫秒: 延时毫秒（默认20毫秒）
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendStringF
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]
    
    return func(hwnd, auto_encode(文本A), 延时毫秒, 窗口状态)

def HD键鼠_句柄发送按键按下(窗口序号: int, hwnd: int, 虚拟键码: int, 窗口状态: int = 0) -> int:
    # INT64 __stdcall HCMKB_SendKeyDownF(INT32 窗口序号, INT32 hwnd, INT32 虚拟键码, INT32 窗口状态);
    """
    按下发送键码到指定窗口（可以不用通讯调用）
    
    Args:
        窗口序号: 窗口序号 (不需要通讯也可以调用,指定一个大于0的序号就行或者任意一个)
        hwnd: hwnd窗口句柄(指定子窗口的窗口句柄,可以指定非绑定窗口的子窗口)
        虚拟键码: 虚拟键码
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置(值)参考: HCWIN_SetWindowState的参数值
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendKeyDownF
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, hwnd, 虚拟键码, 窗口状态)

def HD键鼠_句柄发送按键弹起(窗口序号: int, hwnd: int, 虚拟键码: int, 窗口状态: int = 0) -> int:
    # INT64 __stdcall HCMKB_SendKeyUpF(INT32 窗口序号, INT32 hwnd, INT32 虚拟键码, INT32 窗口状态);
    """
    弹起发送键码到指定窗口（可以不用通讯调用）
    
    Args:
        窗口序号: 窗口序号 (不需要通讯也可以调用,指定一个大于0的序号就行或者任意一个)
        hwnd: hwnd窗口句柄(指定子窗口的窗口句柄,可以指定非绑定窗口的子窗口)
        虚拟键码: 虚拟键码
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置(值)参考: HCWIN_SetWindowState的参数值
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendKeyUpF
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, hwnd, 虚拟键码, 窗口状态)

def HD键鼠_句柄发送按键(窗口序号: int, hwnd: int, 虚拟键码: int, 延时毫秒: int = 20, 窗口状态: int = 0) -> int:
    # INT64 __stdcall HCMKB_SendKeyPressF(INT32 窗口序号, INT32 hwnd, INT32 虚拟键码, INT32 延时毫秒, INT32 窗口状态);
    """
    按下并弹起发送键码到指定窗口（可以不用通讯调用）
    
    Args:
        窗口序号: 窗口序号 (不需要通讯也可以调用,指定一个大于0的序号就行或者任意一个)
        hwnd: hwnd窗口句柄(指定子窗口的窗口句柄,可以指定非绑定窗口的子窗口)
        虚拟键码: 虚拟键码
        延时毫秒: 按下和弹起之间的间隔时间
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置(值)参考: HCWIN_SetWindowState的参数值
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendKeyPressF
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, hwnd, 虚拟键码, 延时毫秒, 窗口状态)

def HD键鼠_句柄发送清空文本(窗口序号: int, hwnd: int, 窗口状态: int = 0) -> int:
    # INT64 __stdcall HCMKB_SendDeleteTextF(INT32 窗口序号, INT32 hwnd, INT32 窗口状态);
    """
    可以清空子窗口的内容（可以不用通讯调用）
    
    Args:
        窗口序号: 窗口序号 (不需要通讯也可以调用,指定一个大于0的序号就行或者任意一个)
        hwnd: hwnd窗口句柄(指定子窗口的窗口句柄,可以指定非绑定窗口的子窗口) 比如:edit richedit
        窗口状态: 窗口状态，-1/0不设置，其他值为操作前窗口设置(值)参考: HCWIN_SetWindowState的参数值
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SendDeleteTextF
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, hwnd, 窗口状态)

def HD键鼠_设置鼠标轨迹参数(步长: int = 30, 步数: int = 100, 每步延迟: int = 20, 开启调试: bool = False) -> int:
    # INT64 __stdcall HCMKB_SetRealMouse(INT32 步长, INT32 步数, INT32 每步延迟, BOOL 开启调试);
    """
    设置鼠标轨迹参数(当移动鼠标开启轨迹生效)
    
    Args:
        步长: 针对直线轨迹有效
        步数: 针对曲线随机轨迹有效
        每步延迟: 中间点每个点发送的频率(毫秒)
        开启调试: 真为开启,只有在调试版本才会触发,会弹窗实时显示轨迹坐标点
        
    Returns:
        int: 操作结果
    """
    hd = Config.get_hd()
    func = hd.HCMKB_SetRealMouse
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
    
    return func(步长, 步数, 每步延迟, 开启调试)

def HD键鼠_获取鼠标位置(窗口序号: int) -> int:
    # INT64 __stdcall HCMKB_GetMousePos(INT32 窗口序号);
    """
    获取后台/前台鼠标位置
    
    Args:
        窗口序号: 窗口序号 特别说明:1.序号为-1表示全局前台 2.如果后台绑定normal,序号不为-1表示窗口前台
        
    Returns:
        int: 返回值大于等于0:表示XY组成的8字节 低4字节为X 高4字节为Y
    """
    hd = Config.get_hd()
    func = hd.HCMKB_GetMousePos
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32]
    
    return func(窗口序号)
