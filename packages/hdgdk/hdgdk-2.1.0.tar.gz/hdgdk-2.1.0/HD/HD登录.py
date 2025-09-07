from .config import Config, ctypes
from .config import auto_encode

def HD_Path(dll路径: str) -> None:
    """
    加载DLL文件
    
    Args:
        dll路径: DLL文件所在路径，例如 "./lib/HDDebug.dll"
    """
    Config.load_dll(dll路径)

# INT64 __stdcall HCHD_Login(char* account, char* password, char* appName, char* appLparam, BOOL bAutoUpdate, BOOL bShowMsgBox);
def HD登录_登录(账号: str, 密码: str, 应用名称: str, 应用参数: str, 是否自动更新: bool, 是否显示消息框: bool) -> int:
    """
    HD登录验证接口
    
    Args:
        账号: 登录账号
        密码: 登录密码
        应用名称: 中控进程名字，指定了方便自动更新
        应用参数: 打开中控的启动参数，指定了方便自动更新
        是否自动更新: 是否自动更新
        是否显示消息框: 如果需要更新是否弹出消息框提醒
    
    Returns:
        int: 版本号
    """
    hd = Config.get_hd()
    
    HCHD_Login = hd.HCHD_Login
    HCHD_Login.restype = ctypes.c_int64
    HCHD_Login.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_bool,
        ctypes.c_bool
    ]
    
    ret = HCHD_Login(
        auto_encode(账号),
        auto_encode(密码),
        auto_encode(应用名称),
        auto_encode(应用参数),
        ctypes.c_bool(是否自动更新),
        ctypes.c_bool(是否显示消息框)
    )
    return ret

# INT64 __stdcall HCHD_GetLastLoginFYI();
def HD登录_获取最近登录点数() -> int:
    """
    获取最近登录时候的点数
    
    Returns:
        int: 最近登录点数
    """
    hd = Config.get_hd()
    
    HCHD_GetLastLoginFYI = hd.HCHD_GetLastLoginFYI
    HCHD_GetLastLoginFYI.restype = ctypes.c_int64
    HCHD_GetLastLoginFYI.argtypes = []
    
    ret = HCHD_GetLastLoginFYI()
    return ret

# INT64 __stdcall HCHD_GetExpiredTimeStamp();
def HD登录_获取最近登录时间() -> int:
    """
    获取最近登录时间戳
    
    Returns:
        int: 最近登录时间戳
    """
    hd = Config.get_hd()
    
    HCHD_GetExpiredTimeStamp = hd.HCHD_GetExpiredTimeStamp
    HCHD_GetExpiredTimeStamp.restype = ctypes.c_int64
    HCHD_GetExpiredTimeStamp.argtypes = []
    
    ret = HCHD_GetExpiredTimeStamp()
    return ret

# INT64 __stdcall HCHD_GetFYI();
def HD登录_获取点数() -> int:
    """
    获取当前点数
    
    Returns:
        int: 当前点数
    """
    hd = Config.get_hd()
    
    HCHD_GetFYI = hd.HCHD_GetFYI
    HCHD_GetFYI.restype = ctypes.c_int64
    HCHD_GetFYI.argtypes = []
    
    ret = HCHD_GetFYI()
    return ret

# INT64 __stdcall HCHD_GetOpenMaxNum();
def HD登录_获取最大多开数() -> int:
    """
    获取当前最大打开窗口数
    
    Returns:
        int: 最大多开数
    """
    hd = Config.get_hd()
    
    HCHD_GetOpenMaxNum = hd.HCHD_GetOpenMaxNum
    HCHD_GetOpenMaxNum.restype = ctypes.c_int64
    HCHD_GetOpenMaxNum.argtypes = []
    
    ret = HCHD_GetOpenMaxNum()
    return ret

# INT64 __stdcall HCHD_GetVersion();
def HD登录_获取版本号() -> int:
    """
    获取当前插件版本号
    
    Returns:
        int: 版本号
    """
    hd = Config.get_hd()
    
    HCHD_GetVersion = hd.HCHD_GetVersion
    HCHD_GetVersion.restype = ctypes.c_int64
    HCHD_GetVersion.argtypes = []
    
    ret = HCHD_GetVersion()
    return ret