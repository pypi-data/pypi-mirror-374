from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCSC_SetPath(char* rootPath);
def HD主板机_设置路径(根目录: str) -> int:
    """
    设置HD主板机根目录路径
    
    Args:
        根目录: 根目录（hdscrcpy.exe和adb.exe所在目录）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSC_SetPath = hd.HCSC_SetPath
    HCSC_SetPath.restype = ctypes.c_int64
    HCSC_SetPath.argtypes = [ctypes.c_char_p]
    
    ret = HCSC_SetPath(auto_encode(根目录))
    return ret

# INT64 __stdcall HCSC_ResetAdb(char* ipInfo);
def HD主板机_重置ADB服务(IP端口信息: str = None) -> int:
    """
    重置ADB服务并可以添加连接IP
    
    Args:
        IP端口信息: IP端口信息（多个IP信息用"|"隔开，IP和端口用":"隔开，如："127.0.0.1:123|127.0.0.2:789|"，可以为None）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSC_ResetAdb = hd.HCSC_ResetAdb
    HCSC_ResetAdb.restype = ctypes.c_int64
    HCSC_ResetAdb.argtypes = [ctypes.c_char_p]
    
    if IP端口信息:
        ret = HCSC_ResetAdb(auto_encode(IP端口信息))
    else:
        ret = HCSC_ResetAdb(None)
    return ret

# INT64 __stdcall HCSC_QueryDevices();
def HD主板机_查询设备() -> int:
    """
    查询当前所有可用的设备
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            成功返回JSON字符串信息：设备1名字|设备2名字|设备3名字|（以"|"分割）
            失败返回JSON字符串信息：连接失败信息
    """
    hd = Config.get_hd()
    
    HCSC_QueryDevices = hd.HCSC_QueryDevices
    HCSC_QueryDevices.restype = ctypes.c_int64
    HCSC_QueryDevices.argtypes = []
    
    ret = HCSC_QueryDevices()
    return ret

# INT64 __stdcall HCSC_ConnectDevices(int winIndex, char* devicesName, char* cmdLparam, int type, int w, int h, int timeOut);
def HD主板机_连接设备(窗口序号: int, 设备号: str, 命令额外参数: str = None, 设备号类型: int = 1, 宽度: int = 1280, 高度: int = 720, 超时连接毫秒: int = 10000) -> int:
    """
    连接设备并通讯窗口序号（需要先初始化中控和登录！HCHD_Login HCEnv_Init/HCEnv_InitEx）
    
    Args:
        窗口序号: 窗口序号
        设备号: 设备号
        命令额外参数: 命令额外参数（参考投屏器命令行指令hdscrcpy命令行解析）
        设备号类型: 设备号类型（1: -s 模拟器描述, 2: -d USB设备号, 3: -e Ip:port）
        宽度: 宽度
        高度: 高度
        超时连接毫秒: 超时连接毫秒（一般10秒也就是10000毫秒）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            成功返回打开的窗口PID
    """
    hd = Config.get_hd()
    
    HCSC_ConnectDevices = hd.HCSC_ConnectDevices
    HCSC_ConnectDevices.restype = ctypes.c_int64
    HCSC_ConnectDevices.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    if 命令额外参数:
        cmd_param = auto_encode(命令额外参数)
    else:
        cmd_param = None
    
    ret = HCSC_ConnectDevices(
        ctypes.c_int32(窗口序号),
        auto_encode(设备号),
        cmd_param,
        ctypes.c_int32(设备号类型),
        ctypes.c_int32(宽度),
        ctypes.c_int32(高度),
        ctypes.c_int32(超时连接毫秒)
    )
    return ret