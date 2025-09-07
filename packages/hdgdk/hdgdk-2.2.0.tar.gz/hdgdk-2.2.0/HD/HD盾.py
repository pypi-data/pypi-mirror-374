from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCHDPP_Protect(int pid);
def HD盾_保护(进程PID: int) -> int:
    """
    一键保护进程（隐藏等）
    
    Args:
        进程PID: 需要保护的进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数3来安装保护盾HDPP驱动
    """
    hd = Config.get_hd()
    
    HCHDPP_Protect = hd.HCHDPP_Protect
    HCHDPP_Protect.restype = ctypes.c_int64
    HCHDPP_Protect.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCHDPP_Protect(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCHDPW_OnProtect(INT64 hwnd);
def HD盾_开启窗口保护(窗口句柄: int) -> int:
    """
    打开窗口保护以及子窗口
    
    Args:
        窗口句柄: 目标窗口句柄，一般为父窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数5来安装保护盾HDPW驱动
        可以多次指定，内部会把指定的保护窗口句柄以及所属子窗口一起保护
    """
    hd = Config.get_hd()
    
    HCHDPW_OnProtect = hd.HCHDPW_OnProtect
    HCHDPW_OnProtect.restype = ctypes.c_int64
    HCHDPW_OnProtect.argtypes = [
        ctypes.c_int64
    ]
    
    ret = HCHDPW_OnProtect(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCHDPW_OffProtect();
def HD盾_关闭窗口保护() -> int:
    """
    取消所有窗口保护（指定保护过的）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数5来安装保护盾HDPW驱动
        可以取消调用过HCHDPW_OnProtect所有保护的窗口句柄
    """
    hd = Config.get_hd()
    
    HCHDPW_OffProtect = hd.HCHDPW_OffProtect
    HCHDPW_OffProtect.restype = ctypes.c_int64
    HCHDPW_OffProtect.argtypes = []
    
    ret = HCHDPW_OffProtect()
    return ret


# Int64  __stdcall HCHDVTPP_OnProtect(Int64 hwnd);
def HD盾_开启PPEx(窗口句柄: int) -> int:
    """
    保护窗口和进程(组件8)

    Args:
        窗口句柄: 目标窗口句柄，一般为父窗口句柄

    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2传递参数8来安装保护盾HDPPEx驱动
    可以取消调用过HCHDVTPP_OffProtect所有保护的窗口句柄
    """
    hd = Config.get_hd()

    HCHDVTPP_OnProtect = hd.HCHDVTPP_OnProtect
    HCHDVTPP_OnProtect.restype = ctypes.c_int64
    HCHDVTPP_OnProtect.argtypes = [
        ctypes.c_int64
    ]

    ret = HCHDVTPP_OnProtect(ctypes.c_int64(窗口句柄))
    return ret

# Int64  __stdcall HCHDVTPP_OffProtect();
def HD盾_关闭PPEx(窗口句柄: int) -> int:
    """
    取消所有保护窗口和进程(组件8)

    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2传递参数8来安装保护盾HDPPEx驱动
    可以取消调用过HCHDVTPP_OffProtect所有保护的窗口句柄
    """
    hd = Config.get_hd()

    HCHDVTPP_OffProtect = hd.HCHDVTPP_OffProtect
    HCHDVTPP_OffProtect.restype = ctypes.c_int64
    HCHDVTPP_OffProtect.argtypes = []

    ret = HCHDVTPP_OffProtect()
    return ret


# Int64  __stdcall HCHDVTPP_OnCapture(Int64 hwnd, int type);
def HD盾_反截图PPEx(窗口句柄: int,类型: int) -> int:
    """
    反截图(组件8)

    Args:
        窗口句柄: 目标窗口句柄，一般为父窗口句柄
        type:0关闭 1开启反截图模式1 2开启反截图模式2
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2传递参数8来安装保护盾HDPPEx驱动
    """
    hd = Config.get_hd()

    HCHDVTPP_OnCapture = hd.HCHDVTPP_OnCapture
    HCHDVTPP_OnCapture.restype = ctypes.c_int64
    HCHDVTPP_OnCapture.argtypes = [
        ctypes.c_int64,
        ctypes.c_int32
    ]

    ret = HCHDVTPP_OnCapture(ctypes.c_int64(窗口句柄),ctypes.c_int32(类型))
    return ret

# Int64  __stdcall HCHDVTPP_ReadBytes(Int64 pid, Int64 targetAddr, __int32 readSize, Int64 buffer, int type);
def HD盾_读字节集PPEx(pid: int,目标地址: int,读大小: int,缓冲区: int,类型) -> int:
    """
    读字节集(组件8)

    Args:
        pid:窗口PID
        targetAddr:目标地址
        readSize:读大小
        buffer:存读数据的缓冲区 注意:缓冲区大小一定要大于等于 读大小 最好相等
        type: 1.普通读写1 2.加强模式2  3.物理读写3
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2传递参数8来安装保护盾HDPPEx驱动
    """
    hd = Config.get_hd()

    HCHDVTPP_ReadBytes = hd.HCHDVTPP_ReadBytes
    HCHDVTPP_ReadBytes.restype = ctypes.c_int64
    HCHDVTPP_ReadBytes.argtypes = [
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int32
    ]

    ret = HCHDVTPP_ReadBytes(ctypes.c_int64(pid),ctypes.c_int64(目标地址),ctypes.c_int32(读大小),ctypes.c_int64(缓冲区),ctypes.c_int32(类型))
    return ret


# Int64  __stdcall HCHDVTPP_WriteBytes(__int64 pid, __int64 targetAddr, __int32 writeSize, __int64 buffer, int type);
def HD盾_写字节集PPEx(pid: int,目标地址: int,写大小: int,缓冲区: int,类型) -> int:
    """
    读字节集(组件8)

    Args:
        pid:窗口PID
        targetAddr:目标地址
        writeSize:写大小
        buffer:存写数据的缓冲区
        type: 1 普通读写1 2加强模式2 3物理读写3
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2传递参数8来安装保护盾HDPPEx驱动
    """
    hd = Config.get_hd()

    HCHDVTPP_WriteBytes = hd.HCHDVTPP_WriteBytes
    HCHDVTPP_WriteBytes.restype = ctypes.c_int64
    HCHDVTPP_WriteBytes.argtypes = [
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int32
    ]

    ret = HCHDVTPP_WriteBytes(ctypes.c_int64(pid),ctypes.c_int64(目标地址),ctypes.c_int32(写大小),ctypes.c_int64(缓冲区),ctypes.c_int32(类型))
    return ret