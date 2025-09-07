from .config import Config, ctypes
from .config import auto_encode


#   Int64 __stdcall HDDW_Open(__int32 windIndex,__int64 attachHwnd);
def HD实时绘制_打开(windIndex: int,attachHwnd:int) -> int:
    """
    打开实时绘制

    Args:
        windIndex:窗口序号
        attachHwnd:附加窗口句柄
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
        无
    """
    hd = Config.get_hd()

    HDDW_Open = hd.HDDW_Open
    HDDW_Open.restype = ctypes.c_int64
    HDDW_Open.argtypes = [
        ctypes.c_int32,
        ctypes.c_int64
    ]

    ret = HDDW_Open(ctypes.c_int32(windIndex),ctypes.c_int64(attachHwnd))
    return ret


#   Int64 __stdcall HDDW_Close(__int32 windIndex);
def HD实时绘制_关闭(windIndex: int) -> int:
    """
    关闭实时绘制

    Args:
        windIndex:窗口序号
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
        无
    """
    hd = Config.get_hd()

    HDDW_Close = hd.HDDW_Close
    HDDW_Close.restype = ctypes.c_int64
    HDDW_Close.argtypes = [
        ctypes.c_int32
    ]

    ret = HDDW_Close(ctypes.c_int32(windIndex))
    return ret


#   Int64 __stdcall HDDW_SetSetting(BOOL bRDraw, BOOL bYoloDraw, BOOL bMKBDraw, __int32 updateTime, char* lparam = NULL);
def HD实时绘制_设置配置(bRDraw: bool= True,bYoloDraw: bool= True,bMKBDraw: bool = True,updateTime: int = 100,lparam: str = None) -> int:
    """
    设置配置实时绘制配置信息

    Args:
        bRDraw:是否绘制识别信息
        bYoloDraw:是否绘制yolov信息
        bMKBDraw:是否绘制键鼠信息
        updateTime:每次更新间隔时间(毫秒)
        param:额外json配置信息 一般NULL 使用的内置配置
        json配置:
        {"bgc":0xFFFFFFFF} 窗口背景色包含透明度 RGBA() 后续绘增加更多的配置属性
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
        无
    """
    hd = Config.get_hd()

    HDDW_SetSetting = hd.HDDW_SetSetting
    HDDW_SetSetting.restype = ctypes.c_int64
    HDDW_SetSetting.argtypes = [
        ctypes.c_bool,
        ctypes.c_bool,
        ctypes.c_bool,
        ctypes.c_int32,
        ctypes.c_char_p,
    ]

    ret = HDDW_SetSetting(
        ctypes.c_bool(bRDraw),
        ctypes.c_bool(bYoloDraw),
        ctypes.c_bool(bMKBDraw),
        ctypes.c_int32(updateTime),
        (auto_encode(lparam) if lparam else None)
    )
    return ret