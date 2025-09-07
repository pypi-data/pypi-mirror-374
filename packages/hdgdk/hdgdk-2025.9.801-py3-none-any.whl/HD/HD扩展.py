from .config import Config, ctypes
from .config import auto_encode

# HD打开回调
# typedef __int64(__stdcall *UIFUNTYPE)(__int32 windowsIndex);
HD_OpenFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32)

# HD检查回调
# typedef __int64(__stdcall *CHECKINSTALLPLUGINTYPE)(int windowsIndex, int preWindowsIndex, int prePid, int error);
HD_CHFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)

# INT64 __stdcall HDEX_InstallPlugin1(int winIndex, char* app, int appType, int injectType, int memType, int gameType, BOOL bAccept, INT64 openFun, INT64 checkFun, int timeOut);
def HD扩展_安装插件1(窗口序号: int, 进程名: str, 进程类型: int, 注入类型: int, 内存模式: int, 游戏类型: int, 是否开启接受线程: bool, 打开回调, 检查回调, 超时时间: int = 30000) -> int:
    """
    第一种通讯安装插件方式（安装插件后再打开进程）
    
    Args:
        窗口序号: 窗口序号
        进程名: 进程名
        进程类型: 进程类型 32/64
        注入类型: 注入类型 0 1 2
        内存模式: 内存模式 0 1 2
        游戏类型: 游戏类型，一般为0就行
        是否开启接受线程: 是否开启接受线程
        打开回调: 回调类型查看INSTALLPLUGINTYPE
        检查回调: 检查回调类型查看，默认NULL
        超时时间: 超时时间
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HDEX_InstallPlugin1 = hd.HDEX_InstallPlugin1
    HDEX_InstallPlugin1.restype = ctypes.c_int64
    HDEX_InstallPlugin1.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32
    ]
    
    打开回调Fun = HD_OpenFunType_stdcall(打开回调) if 打开回调 else None
    检查回调Fun = HD_CHFunType_stdcall(检查回调) if 检查回调 else None
    
    open_fun_ptr = ctypes.c_int64(ctypes.cast(打开回调Fun, ctypes.c_void_p).value) if 打开回调Fun else ctypes.c_int64(0)
    check_fun_ptr = ctypes.c_int64(ctypes.cast(检查回调Fun, ctypes.c_void_p).value) if 检查回调Fun else ctypes.c_int64(0)
    
    ret = HDEX_InstallPlugin1(
        ctypes.c_int32(窗口序号),
        auto_encode(进程名),
        ctypes.c_int32(进程类型),
        ctypes.c_int32(注入类型),
        ctypes.c_int32(内存模式),
        ctypes.c_int32(游戏类型),
        ctypes.c_int32(是否开启接受线程),
        open_fun_ptr,
        check_fun_ptr,
        ctypes.c_int32(超时时间)
    )
    return ret

# INT64 __stdcall HDEX_InstallPlugin2(int winIndex, int funType, int pid, int appType, int gameType, BOOL bAccept, INT64 openFun, INT64 checkFun, int timeOut);
def HD扩展_安装插件2(窗口序号: int, 接口类型: int, 指定PID: int, 进程类型: int, 游戏类型: int, 是否开启接受线程: bool, 打开回调, 检查回调, 超时时间: int = 30000) -> int:
    """
    第二种通讯安装插件方式（打开进程后安装插件），通过pid
    
    Args:
        窗口序号: 窗口序号
        接口类型: 安装插件接口类型表 支持2 4 6
        指定PID: 指定PID，可以为0
        进程类型: 进程类型 32/64
        游戏类型: 游戏类型，一般为0就行
        是否开启接受线程: 是否开启接受线程
        打开回调: 回调类型查看，可选，默认NULL
        检查回调: 检查回调类型查看，可选，默认NULL
        超时时间: 超时时间
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HDEX_InstallPlugin2 = hd.HDEX_InstallPlugin2
    HDEX_InstallPlugin2.restype = ctypes.c_int64
    HDEX_InstallPlugin2.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32
    ]
    
    打开回调Fun = HD_OpenFunType_stdcall(打开回调) if 打开回调 else None
    检查回调Fun = HD_CHFunType_stdcall(检查回调) if 检查回调 else None
    
    open_fun_ptr = ctypes.c_int64(ctypes.cast(打开回调Fun, ctypes.c_void_p).value) if 打开回调Fun else ctypes.c_int64(0)
    check_fun_ptr = ctypes.c_int64(ctypes.cast(检查回调Fun, ctypes.c_void_p).value) if 检查回调Fun else ctypes.c_int64(0)
    
    ret = HDEX_InstallPlugin2(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(接口类型),
        ctypes.c_int32(指定PID),
        ctypes.c_int32(进程类型),
        ctypes.c_int32(游戏类型),
        ctypes.c_int32(是否开启接受线程),
        open_fun_ptr,
        check_fun_ptr,
        ctypes.c_int32(超时时间)
    )
    return ret

# INT64 __stdcall HDEX_InstallPlugin3(int winIndex, int funType, INT64 hwnd, int appType, int gameType, BOOL bAccept, INT64 openFun, INT64 checkFun, int timeOut);
def HD扩展_安装插件3(窗口序号: int, 接口类型: int, 指定窗口句柄: int, 进程类型: int, 游戏类型: int, 是否开启接受线程: bool, 打开回调, 检查回调, 超时时间: int = 30000) -> int:
    """
    第二种通讯安装插件方式（打开进程后安装插件），通过窗口句柄
    
    Args:
        窗口序号: 窗口序号
        接口类型: 安装插件接口类型表 支持3 5 7
        指定窗口句柄: 指定窗口句柄，可以为0
        进程类型: 进程类型 32/64
        游戏类型: 游戏类型，一般为0就行
        是否开启接受线程: 是否开启接受线程
        打开回调: 回调类型查看，可选，默认NULL
        检查回调: 检查回调类型查看，可选，默认NULL
        超时时间: 超时时间
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HDEX_InstallPlugin3 = hd.HDEX_InstallPlugin3
    HDEX_InstallPlugin3.restype = ctypes.c_int64
    HDEX_InstallPlugin3.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32
    ]
    
    打开回调Fun = HD_OpenFunType_stdcall(打开回调) if 打开回调 else None
    检查回调Fun = HD_CHFunType_stdcall(检查回调) if 检查回调 else None
    
    open_fun_ptr = ctypes.c_int64(ctypes.cast(打开回调Fun, ctypes.c_void_p).value) if 打开回调Fun else ctypes.c_int64(0)
    check_fun_ptr = ctypes.c_int64(ctypes.cast(检查回调Fun, ctypes.c_void_p).value) if 检查回调Fun else ctypes.c_int64(0)
    
    ret = HDEX_InstallPlugin3(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(接口类型),
        ctypes.c_int64(指定窗口句柄),
        ctypes.c_int32(进程类型),
        ctypes.c_int32(游戏类型),
        ctypes.c_int32(是否开启接受线程),
        open_fun_ptr,
        check_fun_ptr,
        ctypes.c_int32(超时时间)
    )
    return ret

# INT64 __stdcall HDEX_InstallPluginVM(int winIndex, int funType, int vmPid, int vncPort, int appType, INT64 openFun, INT64 checkFun, int timeOut);
def HD扩展_安装插件VM(窗口序号: int, 接口类型: int, 虚拟机PID: int, VNC端口: int, 进程类型: int, 打开回调=None, 检查回调=None, 超时时间: int = 30000) -> int:
    """
    安装插件VM版本，通过PID针对虚拟机内部自动关联虚拟机
    
    Args:
        窗口序号: 窗口序号
        接口类型: 内部安装插件接口类型，查看安装插件接口类型表 支持3 5 7
        虚拟机PID: 虚拟机PID，或者打开回调指定
        VNC端口: 虚拟机VNC端口，-1表示不连接VNC，大于0表示连接VNC（会断开后重新连接），0为使用之前的缓存VNC端口（会断开后重新连接）
        进程类型: 进程类型 32/64
        打开回调: 打开回调
        检查回调: 检查回调
        超时时间: 超时时间
    
    Returns:
        int: 返回值代码
    
    Note:
        1.调用之前记得打开服务器HCVMDMA_StartServer并确定正确打开HCVMDMA_ServerIsStart
        2.其他规则和前3种安装插件方式一致
        3.支持重连，重连的前提是不能被HCEnv_UnLoad卸载
        4.如果使用HD多线程模块 强烈建议在登录回调中使用
    """
    hd = Config.get_hd()
    
    HDEX_InstallPluginVM = hd.HDEX_InstallPluginVM
    HDEX_InstallPluginVM.restype = ctypes.c_int64
    HDEX_InstallPluginVM.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32
    ]
    
    openFun_ptr = ctypes.c_int64(ctypes.cast(HD_OpenFunType_stdcall(打开回调), ctypes.c_void_p).value) if 打开回调 else ctypes.c_int64(0)
    checkFun_ptr = ctypes.c_int64(ctypes.cast(HD_CHFunType_stdcall(检查回调), ctypes.c_void_p).value) if 检查回调 else ctypes.c_int64(0)
    
    ret = HDEX_InstallPluginVM(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(接口类型),
        ctypes.c_int32(虚拟机PID),
        ctypes.c_int32(VNC端口),
        ctypes.c_int32(进程类型),
        openFun_ptr,
        checkFun_ptr,
        ctypes.c_int32(超时时间)
    )
    return ret