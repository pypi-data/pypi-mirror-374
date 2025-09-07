from .config import Config, ctypes
from .config import auto_encode

# ━━━━━━━━━━━━━━━━━━ 截图管理接口 ━━━━━━━━━━━━━━━━━━


class MYA8R8G8B8(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('m_a', ctypes.c_ubyte),
        ('m_r', ctypes.c_ubyte),
        ('m_g', ctypes.c_ubyte),
        ('m_b', ctypes.c_ubyte)
    ]

# INT64 __stdcall HCCS_SetType(int 模式);
def HD截图_设置识别模式(模式: int) -> int:
    """
    设置识别模式
    :param 窗口序号: 窗口序号 (从1开始)
    :return: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HCCS_SetType = hd.HCCS_SetType
    HCCS_SetType.restype = ctypes.c_int64
    HCCS_SetType.argtypes = [ctypes.c_int32]

    ret = HCCS_SetType(ctypes.c_int32(模式))

    return ret

# INT64 __stdcall HCCS_OpenCS(int 窗口序号);
def HD截图_打开(窗口序号: int) -> int:
    """
    打开截图
    :param 窗口序号: 窗口序号 (从1开始)
    :return: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HCCS_OpenCS = hd.HCCS_OpenCS
    HCCS_OpenCS.restype = ctypes.c_int64
    HCCS_OpenCS.argtypes = [ctypes.c_int32]

    ret = HCCS_OpenCS(ctypes.c_int32(窗口序号))

    return ret


# INT64 __stdcall HCCS_OpenCSEx(int 窗口序号, BOOL bNormal, int capType, INT64 hwnd);
def HD截图_打开Ex(窗口序号: int, 是否是通常模式: bool, 截图模式: int = 0, 窗口句柄: int = 0) -> int:
    """
    打开截图（扩展版本）
    :param 窗口序号: 窗口序号 (从1开始)
    :param 是否是通常模式: 是否是通常模式（一般为TRUE）
    :param 截图模式: 截图模式（查看HD截图模式） (默认0)
    :param 窗口句柄: 窗口句柄 (默认0)
    :return: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HCCS_OpenCSEx = hd.HCCS_OpenCSEx
    HCCS_OpenCSEx.restype = ctypes.c_int64
    HCCS_OpenCSEx.argtypes = [ctypes.c_int32, ctypes.c_bool, ctypes.c_int32, ctypes.c_int64]

    ret = HCCS_OpenCSEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否是通常模式),
        ctypes.c_int32(截图模式),
        ctypes.c_int64(窗口句柄)
    )

    return ret


# INT64 __stdcall HCCS_CloseCS(int 窗口序号);
def HD截图_关闭(窗口序号: int) -> int:
    """
    关闭截图
    :param 窗口序号: 窗口序号 (从1开始)
    :return: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    HCCS_CloseCS = hd.HCCS_CloseCS
    HCCS_CloseCS.restype = ctypes.c_int64
    HCCS_CloseCS.argtypes = [ctypes.c_int32]

    ret = HCCS_CloseCS(ctypes.c_int32(窗口序号))

    return ret


def HD截图_关闭Ex(窗口序号: int) -> int:
    # INT64 __stdcall HCCS_CloseCSEx(INT32 窗口序号);
    """
    关闭截图（扩展版本）
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    func = hd.HCCS_CloseCSEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32]
    
    return func(窗口序号)


def HD截图_获取截图数据(窗口序号: int) -> int:
    # INT64 __stdcall HCCS_GetCSData(INT32 窗口序号);
    """
    获取截图数据
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        
    Returns:
        int: 返回值代码（查看HD返回值表），数据以JSON格式返回
    """
    hd = Config.get_hd()
    func = hd.HCCS_GetCSData
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32]
    
    return func(窗口序号)


def HD截图_打开查看器(窗口序号: int, X: int, Y: int, 宽度: int, 高度: int) -> int:
    # INT64 __stdcall HCCS_OpenCSFinder(INT32 窗口序号, INT32 X, INT32 Y, INT32 宽度, INT32 高度);
    """
    打开截图查看器
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        X: 查看器X坐标
        Y: 查看器Y坐标
        宽度: 查看器宽度
        高度: 查看器高度
        
    Returns:
        int: 返回值代码（查看HD返回值表），或者返回查看器的PID
    """
    hd = Config.get_hd()
    func = hd.HCCS_OpenCSFinder
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, X, Y, 宽度, 高度)


def HD截图_关闭查看器(窗口序号: int, pid: int) -> int:
    # INT64 __stdcall HCCS_CloseCSFinder(INT32 窗口序号, INT32 pid);
    """
    关闭截图查看器
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        pid: 查看器的进程PID
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    func = hd.HCCS_CloseCSFinder
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    return func(窗口序号, pid)


def HD截图_截图(窗口序号: int, BMP文件路径: str, 是否打开: bool = False) -> int:
    # INT64 __stdcall HCCS_CaptureBmp(INT32 窗口序号, LPCSTR BMP文件路径, BOOL 是否打开);
    """
    截图并保存为BMP图片文件
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        BMP文件路径: BMP文件路径+文件名
        是否打开: 是否打开查看图片
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    func = hd.HCCS_CaptureBmp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(BMP文件路径), 是否打开)


def HD截图_获取BMP截图数据(窗口序号: int) -> int:
    # INT64 __stdcall HCCS_GetCaptureBmpData(INT32 窗口序号);
    """
    获取BMP截图数据
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
             数据在json字符串中
             json: {"error":0,"ret":[{"bRet":1,"addr":XXX,"eleSize":YYY,"allLen":ZZZ,"w":1222,"h":699}]}
             XXX是图片二进制数据首地址
             YYY是MYA8R8G8B8结构体数量
             ZZZ:总字节大小等于(54+YYY*sizeof(MYA8R8G8B8))
             w:宽度
             h:高度
             注意:拿到图片地址数据XXX使用后 记得释放(HCCS_FreeArray)
    """
    hd = Config.get_hd()
    func = hd.HCCS_GetCaptureBmpData
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32]
    
    return func(窗口序号)


def HD截图_释放数据(需要释放的地址: int) -> int:
    # INT64 __stdcall HCCS_FreeArray(INT64 addr);
    """
    释放内存
    
    Args:
        需要释放的地址: 需要释放的地址
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
             释放内存 该内存是使用 new[] 申请的内存
    """
    hd = Config.get_hd()
    func = hd.HCCS_FreeArray
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64]
    
    return func(需要释放的地址)


def HD截图_释放内存池数据(窗口序号: int, 需要释放的地址: int) -> int:
    # INT64 __stdcall HCCS_FreeMemPool(INT32 窗口序号, INT64 addr);
    """
    释放内存,内存池操作释放内存
    我们获取了截图数据不需要了都需要调用这个接口来释放掉,防止内存泄露
    那个窗口序号返回申请的地址 就用那个窗口序号释放
    注意:该接口是释放【使用内存池申请的内存地址】的地址,与HCCS_FreeArray不一样
    
    Args:
        窗口序号: 窗口序号
        需要释放的地址: 需要释放的地址
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
             释放内存 该内存是使用 new[] 申请的内存
    """
    hd = Config.get_hd()
    func = hd.HCCS_FreeMemPool
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int64]
    
    return func(窗口序号, 需要释放的地址)


def HD截图_是否后台缓存失败(传递的返回值: int) -> int:
    # INT64 __stdcall HCCS_IsCaptureValid(INT64 ret);
    """
    后台截图缓存获取失败判断接口
    可以自行加一个容错次数,再这个次数内多次识别,直到找到
    
    Args:
        传递的返回值: 传递的返回值 必须是识别截图相关的接口返回的
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
             释放内存 该内存是使用 new[] 申请的内存
    """
    hd = Config.get_hd()
    func = hd.HCCS_IsCaptureValid
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64]
    
    return func(传递的返回值)


