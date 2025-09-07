#软件找HD作者拿(魔改版)
from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCIP_YMSetRootPath(char* path);
def HDIP_有米设置路径(路径: str) -> int:
    """
    设置有米软件路径（EXE路径）
    软件找HD作者拿（魔改版）
    
    Args:
        路径: 有米软件EXE路径
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMSetRootPath = hd.HCIP_YMSetRootPath
    HCIP_YMSetRootPath.restype = ctypes.c_int64
    HCIP_YMSetRootPath.argtypes = [ctypes.c_char_p]
    
    ret = HCIP_YMSetRootPath(auto_encode(路径))
    return ret

# INT64 __stdcall HCIP_YMAddIP(char* ip, int port, char* account, char* password, int type, int kfp, char* proName);
def HDIP_有米添加IP(IP地址: str, 端口: int, 账号: str, 密码: str, 类型: int, 是否可分配: int = 1, 进程名: str = None) -> int:
    """
    添加有米IP代理设置
    软件找HD作者拿（魔改版）
    
    Args:
        IP地址: IP地址，如："127.0.0.1"
        端口: 端口号
        账号: 账号
        密码: 密码
        类型: 1表示socket，2表示ss
        是否可分配: 是否可分配（一般默认1）
        进程名: 进程名（一般为空即可）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMAddIP = hd.HCIP_YMAddIP
    HCIP_YMAddIP.restype = ctypes.c_int64
    HCIP_YMAddIP.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
    
    if 进程名:
        pro_name = auto_encode(进程名)
    else:
        pro_name = None
    
    ret = HCIP_YMAddIP(
        auto_encode(IP地址),
        ctypes.c_int32(端口),
        auto_encode(账号),
        auto_encode(密码),
        ctypes.c_int32(类型),
        ctypes.c_int32(是否可分配),
        pro_name
    )
    return ret

# INT64 __stdcall HCIP_YMAddProcess(char* proName);
def HDIP_有米添加进程(进程名: str) -> int:
    """
    添加代理的进程名
    软件找HD作者拿（魔改版）
    
    Args:
        进程名: 进程名，如："Game.exe"
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMAddProcess = hd.HCIP_YMAddProcess
    HCIP_YMAddProcess.restype = ctypes.c_int64
    HCIP_YMAddProcess.argtypes = [ctypes.c_char_p]
    
    ret = HCIP_YMAddProcess(auto_encode(进程名))
    return ret

# INT64 __stdcall HCIP_YMOpen(int type);
def HDIP_有米打开(类型: int) -> int:
    """
    打开有米软件
    软件找HD作者拿（魔改版）
    
    Args:
        类型: 类型（0国内IP，1国外IP）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMOpen = hd.HCIP_YMOpen
    HCIP_YMOpen.restype = ctypes.c_int64
    HCIP_YMOpen.argtypes = [ctypes.c_int32]
    
    ret = HCIP_YMOpen(ctypes.c_int32(类型))
    return ret

# INT64 __stdcall HCIP_YMIsOpen(int type);
def HDIP_有米是否打开(类型: int) -> int:
    """
    检查有米软件是否已经打开
    软件找HD作者拿（魔改版）
    
    Args:
        类型: 类型（0国内IP，1国外IP）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMIsOpen = hd.HCIP_YMIsOpen
    HCIP_YMIsOpen.restype = ctypes.c_int64
    HCIP_YMIsOpen.argtypes = [ctypes.c_int32]
    
    ret = HCIP_YMIsOpen(ctypes.c_int32(类型))
    return ret

# INT64 __stdcall HCIP_YMClose(int type);
def HDIP_有米关闭(类型: int) -> int:
    """
    关闭有米软件
    软件找HD作者拿（魔改版）
    
    Args:
        类型: 类型（0国内IP，1国外IP）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCIP_YMClose = hd.HCIP_YMClose
    HCIP_YMClose.restype = ctypes.c_int64
    HCIP_YMClose.argtypes = [ctypes.c_int32]
    
    ret = HCIP_YMClose(ctypes.c_int32(类型))
    return ret