from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCSYS_CheckFontSmooth();
def HD系统_是否开启字体平滑() -> int:
    """
    检查字体是否开启字体平滑
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_CheckFontSmooth = hd.HCSYS_CheckFontSmooth
    HCSYS_CheckFontSmooth.restype = ctypes.c_int64
    HCSYS_CheckFontSmooth.argtypes = []
    
    ret = HCSYS_CheckFontSmooth()
    return ret

# INT64 __stdcall HCSYS_CloseFontSmooth();
def HD系统_关闭字体平滑() -> int:
    """
    关闭字体平滑
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_CloseFontSmooth = hd.HCSYS_CloseFontSmooth
    HCSYS_CloseFontSmooth.restype = ctypes.c_int64
    HCSYS_CloseFontSmooth.argtypes = []
    
    ret = HCSYS_CloseFontSmooth()
    return ret

# INT64 __stdcall HCSYS_OpenFontSmooth();
def HD系统_打开字体平滑() -> int:
    """
    打开字体平滑
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_OpenFontSmooth = hd.HCSYS_OpenFontSmooth
    HCSYS_OpenFontSmooth.restype = ctypes.c_int64
    HCSYS_OpenFontSmooth.argtypes = []
    
    ret = HCSYS_OpenFontSmooth()
    return ret

# INT64 __stdcall HCSYS_CheckUAC();
def HD系统_是否开启UAC() -> int:
    """
    检查当前系统是否开启了UAC（用户控制）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_CheckUAC = hd.HCSYS_CheckUAC
    HCSYS_CheckUAC.restype = ctypes.c_int64
    HCSYS_CheckUAC.argtypes = []
    
    ret = HCSYS_CheckUAC()
    return ret

# INT64 __stdcall HCSYS_SetUAC(int bEnable);
def HD系统_设置UAC(是否开启: int) -> int:
    """
    设置当前系统的UAC（用户控制）开关
    
    Args:
        是否开启: 是否开启UAC（0: 关闭, 1: 开启）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_SetUAC = hd.HCSYS_SetUAC
    HCSYS_SetUAC.restype = ctypes.c_int64
    HCSYS_SetUAC.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_SetUAC(ctypes.c_int32(是否开启))
    return ret

# INT64 __stdcall HCSYS_Delay(int 毫秒);
def HD系统_延迟(毫秒: int) -> int:
    """
    延迟，不会堵塞主线程
    
    Args:
        毫秒: 毫秒数
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_Delay = hd.HCSYS_Delay
    HCSYS_Delay.restype = ctypes.c_int64
    HCSYS_Delay.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_Delay(ctypes.c_int32(毫秒))
    return ret

# INT64 __stdcall HCSYS_DelayEx(int 最小毫秒, int 最大毫秒);
def HD系统_随机延迟(最小毫秒: int, 最大毫秒: int) -> int:
    """
    在随机范围内延迟，不会堵塞主线程
    
    Args:
        最小毫秒: 最小延迟时间
        最大毫秒: 最大延迟时间
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_DelayEx = hd.HCSYS_DelayEx
    HCSYS_DelayEx.restype = ctypes.c_int64
    HCSYS_DelayEx.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCSYS_DelayEx(ctypes.c_int32(最小毫秒), ctypes.c_int32(最大毫秒))
    return ret

# INT64 __stdcall HCSYS_ExitSys(int type);
def HD系统_关闭系统(类型: int) -> int:
    """
    关闭系统
    
    Args:
        类型: 注销(0), 关机(1), 重启(2)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_ExitSys = hd.HCSYS_ExitSys
    HCSYS_ExitSys.restype = ctypes.c_int64
    HCSYS_ExitSys.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_ExitSys(ctypes.c_int32(类型))
    return ret

# INT64 __stdcall HCSYS_CloseScreenProtect();
def HD系统_关闭屏保() -> int:
    """
    关闭屏保
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_CloseScreenProtect = hd.HCSYS_CloseScreenProtect
    HCSYS_CloseScreenProtect.restype = ctypes.c_int64
    HCSYS_CloseScreenProtect.argtypes = []
    
    ret = HCSYS_CloseScreenProtect()
    return ret

# INT64 __stdcall HCSYS_ClosePowerManager();
def HD系统_关闭电源管理() -> int:
    """
    关闭电源管理，不进入睡眠
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_ClosePowerManager = hd.HCSYS_ClosePowerManager
    HCSYS_ClosePowerManager.restype = ctypes.c_int64
    HCSYS_ClosePowerManager.argtypes = []
    
    ret = HCSYS_ClosePowerManager()
    return ret

# INT64 __stdcall HCSYS_ResumeSystemModify();
def HD系统_恢复最近系统修改() -> int:
    """
    恢复系统上次的修改
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_ResumeSystemModify = hd.HCSYS_ResumeSystemModify
    HCSYS_ResumeSystemModify.restype = ctypes.c_int64
    HCSYS_ResumeSystemModify.argtypes = []
    
    ret = HCSYS_ResumeSystemModify()
    return ret

# INT64 __stdcall HCSYS_DisableCloseDisplayAndSleep();
def HD系统_禁止休眠() -> int:
    """
    设置当前的电源设置（禁止关闭显示器，禁止关闭硬盘，禁止睡眠和待机）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_DisableCloseDisplayAndSleep = hd.HCSYS_DisableCloseDisplayAndSleep
    HCSYS_DisableCloseDisplayAndSleep.restype = ctypes.c_int64
    HCSYS_DisableCloseDisplayAndSleep.argtypes = []
    
    ret = HCSYS_DisableCloseDisplayAndSleep()
    return ret

# INT64 __stdcall HCSYS_GetDir(int type);
def HD系统_获取路径(类型: int) -> int:
    """
    获取路径并返回json字符串
    
    Args:
        类型: 当前路径(0), system32路径(1), windows所在路径(2), 临时目录路径(3), 当前进程(exe)所在的路径(4)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetDir = hd.HCSYS_GetDir
    HCSYS_GetDir.restype = ctypes.c_int64
    HCSYS_GetDir.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_GetDir(ctypes.c_int32(类型))
    return ret

# INT64 __stdcall HCSYS_GetCpuType();
def HD系统_获取CPU类型() -> int:
    """
    获取CPU类型
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            1: Intel
            2: AMD
    """
    hd = Config.get_hd()
    
    HCSYS_GetCpuType = hd.HCSYS_GetCpuType
    HCSYS_GetCpuType.restype = ctypes.c_int64
    HCSYS_GetCpuType.argtypes = []
    
    ret = HCSYS_GetCpuType()
    return ret

# INT64 __stdcall HCSYS_GetCpuUsage();
def HD系统_获取当前CPU使用率() -> int:
    """
    获取CPU使用率
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            大于0表示: 使用率百分比
    """
    hd = Config.get_hd()
    
    HCSYS_GetCpuUsage = hd.HCSYS_GetCpuUsage
    HCSYS_GetCpuUsage.restype = ctypes.c_int64
    HCSYS_GetCpuUsage.argtypes = []
    
    ret = HCSYS_GetCpuUsage()
    return ret

# INT64 __stdcall HCSYS_GetCpuUsageByPid(int pid);
def HD系统_获取CPU使用率(进程PID: int) -> int:
    """
    获取指定进程的CPU使用率
    
    Args:
        进程PID: 进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            大于0表示: 使用率百分比
    """
    hd = Config.get_hd()
    
    HCSYS_GetCpuUsageByPid = hd.HCSYS_GetCpuUsageByPid
    HCSYS_GetCpuUsageByPid.restype = ctypes.c_int64
    HCSYS_GetCpuUsageByPid.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_GetCpuUsageByPid(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCSYS_GetMemoryUsageByPid(int pid);
def HD系统_获取内存使用率(进程PID: int) -> int:
    """
    获取指定进程的内存使用率
    
    Args:
        进程PID: 进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            大于0表示: 使用率百分比
    """
    hd = Config.get_hd()
    
    HCSYS_GetMemoryUsageByPid = hd.HCSYS_GetMemoryUsageByPid
    HCSYS_GetMemoryUsageByPid.restype = ctypes.c_int64
    HCSYS_GetMemoryUsageByPid.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_GetMemoryUsageByPid(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCSYS_GetDiskSerial(int index);
def HD系统_获取磁盘序列号(磁盘序号: int) -> int:
    """
    获取磁盘序列号
    
    Args:
        磁盘序号: 磁盘序号
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetDiskSerial = hd.HCSYS_GetDiskSerial
    HCSYS_GetDiskSerial.restype = ctypes.c_int64
    HCSYS_GetDiskSerial.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_GetDiskSerial(ctypes.c_int32(磁盘序号))
    return ret

# INT64 __stdcall HCSYS_GetDisplayInfo();
def HD系统_获取显卡信息() -> int:
    """
    获取显卡信息
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetDisplayInfo = hd.HCSYS_GetDisplayInfo
    HCSYS_GetDisplayInfo.restype = ctypes.c_int64
    HCSYS_GetDisplayInfo.argtypes = []
    
    ret = HCSYS_GetDisplayInfo()
    return ret

# INT64 __stdcall HCSYS_GetDPI();
def HD系统_获取DPI() -> int:
    """
    获取DPI
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            大于0表示: 具体的DPI
    """
    hd = Config.get_hd()
    
    HCSYS_GetDPI = hd.HCSYS_GetDPI
    HCSYS_GetDPI.restype = ctypes.c_int64
    HCSYS_GetDPI.argtypes = []
    
    ret = HCSYS_GetDPI()
    return ret

# INT64 __stdcall HCSYS_RunApp(char* path, long type);
def HD系统_启动EXE(exe路径: str, 返回值类型: int) -> int:
    """
    运行指定路径下的exe
    
    Args:
        exe路径: exe路径
        返回值类型: 返回值类型（进程ID(0), 线程ID(1), 进程句柄(2), 线程句柄(3)）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_RunApp = hd.HCSYS_RunApp
    HCSYS_RunApp.restype = ctypes.c_int64
    HCSYS_RunApp.argtypes = [ctypes.c_char_p, ctypes.c_long]
    
    ret = HCSYS_RunApp(auto_encode(exe路径), ctypes.c_long(返回值类型))
    return ret

# INT64 __stdcall HCSYS_RunAppGetRet(char* cmdApp, BOOL bShowCrol, BOOL bWait);
def HD系统_执行DOS指令取返回(命令应用: str, 是否显示控制台: bool, 是否等待进程结束返回: bool) -> int:
    """
    获取CMD命令形式的打开进程并获取返回输出
    
    Args:
        命令应用: 带exe+启动参数
        是否显示控制台: 是否显示进程窗口
        是否等待进程结束返回: 是否等待进程结束返回（True: 等待，False: 不等待）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_RunAppGetRet = hd.HCSYS_RunAppGetRet
    HCSYS_RunAppGetRet.restype = ctypes.c_int64
    HCSYS_RunAppGetRet.argtypes = [ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCSYS_RunAppGetRet(
        auto_encode(命令应用),
        ctypes.c_bool(是否显示控制台),
        ctypes.c_bool(是否等待进程结束返回)
    )
    return ret

# INT64 __stdcall HCSYS_RunAppGetRetEx(char* cmdApp, char* lparam, BOOL bAs);
def HD系统_管理员打开进程(命令应用: str, 启动参数: str, 是否管理员: bool = True) -> int:
    """
    获取CMD命令形式的打开进程（支持管理员打开）（扩展版本）
    
    Args:
        命令应用: APP路径+APP，如: J:\\HMADG\\HMad\\x64\\Release\\GoogleAuthy.exe
        启动参数: 启动参数，如: DN7BNCWGVYBJHC677AYLLC3EFZEU2VIP
        是否管理员: 是否管理员
    
    Returns:
        int: 成功返回PID和返回json，失败返回查看返回值表HD返回值表
    
    Note:
        内部是调用ShellExecuteExA
    """
    hd = Config.get_hd()
    
    HCSYS_RunAppGetRetEx = hd.HCSYS_RunAppGetRetEx
    HCSYS_RunAppGetRetEx.restype = ctypes.c_int64
    HCSYS_RunAppGetRetEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCSYS_RunAppGetRetEx(
        auto_encode(命令应用),
        auto_encode(启动参数),
        ctypes.c_bool(是否管理员)
    )
    return ret

# INT64 __stdcall HCSYS_RunAppEx(char* path, char* appName, char* lparam, int flag, long type);
def HD系统_启动EXE带参数(路径: str, 应用名: str, 启动参数: str, 标志: int, 返回值类型: int) -> int:
    """
    运行指定路径下的exe，支持启动参数
    
    Args:
        路径: exe路径
        应用名: exe名字
        启动参数: 启动参数
        标志: 启动标志（挂起状态打开(4), 直接打开运行(0)）
        返回值类型: 返回值类型（进程ID(0), 线程ID(1), 进程句柄(2), 线程句柄(3)）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_RunAppEx = hd.HCSYS_RunAppEx
    HCSYS_RunAppEx.restype = ctypes.c_int64
    HCSYS_RunAppEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_long]
    
    ret = HCSYS_RunAppEx(
        auto_encode(路径),
        auto_encode(应用名),
        auto_encode(启动参数),
        ctypes.c_int32(标志),
        ctypes.c_long(返回值类型)
    )
    return ret

# INT64 __stdcall HCSYS_RunAppExxxx(char* path, char* appName, char* lparam, int flag, long type);
def HD系统_启动EXE带参数Ex(路径: str, 应用名: str, 启动参数: str, 标志: int, 返回值类型: int) -> int:
    """
    运行指定路径下的exe，支持启动参数，并指定了当前进程的路径
    
    Args:
        路径: exe路径
        应用名: exe名字
        启动参数: 启动参数
        标志: 启动标志（挂起状态打开(4), 直接打开运行(0)）
        返回值类型: 返回值类型（进程ID(0), 线程ID(1), 进程句柄(2), 线程句柄(3)）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_RunAppExxxx = hd.HCSYS_RunAppExxxx
    HCSYS_RunAppExxxx.restype = ctypes.c_int64
    HCSYS_RunAppExxxx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_long]
    
    ret = HCSYS_RunAppExxxx(
        auto_encode(路径),
        auto_encode(应用名),
        auto_encode(启动参数),
        ctypes.c_int32(标志),
        ctypes.c_long(返回值类型)
    )
    return ret

# INT64 __stdcall HCSYS_GetHDiskCode();
def HD系统_获取磁盘特征码() -> int:
    """
    获取磁盘特征码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetHDiskCode = hd.HCSYS_GetHDiskCode
    HCSYS_GetHDiskCode.restype = ctypes.c_int64
    HCSYS_GetHDiskCode.argtypes = []
    
    ret = HCSYS_GetHDiskCode()
    return ret

# INT64 __stdcall HCSYS_GetCpuCode();
def HD系统_获取CPU特征码() -> int:
    """
    获取CPU特征码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetCpuCode = hd.HCSYS_GetCpuCode
    HCSYS_GetCpuCode.restype = ctypes.c_int64
    HCSYS_GetCpuCode.argtypes = []
    
    ret = HCSYS_GetCpuCode()
    return ret

# INT64 __stdcall HCSYS_GetBIOSInfo();
def HD系统_获取BOIS制造日期() -> int:
    """
    获取BIOS制造日期
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetBIOSInfo = hd.HCSYS_GetBIOSInfo
    HCSYS_GetBIOSInfo.restype = ctypes.c_int64
    HCSYS_GetBIOSInfo.argtypes = []
    
    ret = HCSYS_GetBIOSInfo()
    return ret

# INT64 __stdcall HCSYS_GetMachineCode();
def HD系统_获取机器码() -> int:
    """
    获取机器码（包含网卡）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetMachineCode = hd.HCSYS_GetMachineCode
    HCSYS_GetMachineCode.restype = ctypes.c_int64
    HCSYS_GetMachineCode.argtypes = []
    
    ret = HCSYS_GetMachineCode()
    return ret

# INT64 __stdcall HCSYS_GetMachineCodeNoMac();
def HD系统_获取机器码无网卡() -> int:
    """
    获取机器码（不包含网卡）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetMachineCodeNoMac = hd.HCSYS_GetMachineCodeNoMac
    HCSYS_GetMachineCodeNoMac.restype = ctypes.c_int64
    HCSYS_GetMachineCodeNoMac.argtypes = []
    
    ret = HCSYS_GetMachineCodeNoMac()
    return ret

# INT64 __stdcall HCSYS_GetNetTime();
def HD系统_获取网络时间() -> int:
    """
    获取网络时间
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetNetTime = hd.HCSYS_GetNetTime
    HCSYS_GetNetTime.restype = ctypes.c_int64
    HCSYS_GetNetTime.argtypes = []
    
    ret = HCSYS_GetNetTime()
    return ret

# INT64 __stdcall HCSYS_GetNetTimeByIp(char* ip);
def HD系统_获取网络时间Ex(IP地址: str) -> int:
    """
    获取指定服务器IP的网络时间
    
    Args:
        IP地址: 服务器IP字符串（如: 127.0.0.1）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetNetTimeByIp = hd.HCSYS_GetNetTimeByIp
    HCSYS_GetNetTimeByIp.restype = ctypes.c_int64
    HCSYS_GetNetTimeByIp.argtypes = [ctypes.c_char_p]
    
    ret = HCSYS_GetNetTimeByIp(auto_encode(IP地址))
    return ret

# INT64 __stdcall HCSYS_GetSystemBuildNumber();
def HD系统_获取系统版本() -> int:
    """
    获取系统版本
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            大于0表示具体版本号
    """
    hd = Config.get_hd()
    
    HCSYS_GetSystemBuildNumber = hd.HCSYS_GetSystemBuildNumber
    HCSYS_GetSystemBuildNumber.restype = ctypes.c_int64
    HCSYS_GetSystemBuildNumber.argtypes = []
    
    ret = HCSYS_GetSystemBuildNumber()
    return ret

# INT64 __stdcall HCSYS_GetSystemType();
def HD系统_获取系统类型() -> int:
    """
    获取系统类型
    
    Returns:
        int: 返回值代码（查看HD返回值表）
            1: win95/98/me/nt4.0
            2: xp/2000
            3: 2003/2003 R2/xp-64
            4: win7/2008 R2
            5: vista/2008
            6: win8/2012
            7: win8.1/2012 R2
            8: win10/2016 TP/win11
            9: win11
    """
    hd = Config.get_hd()
    
    HCSYS_GetSystemType = hd.HCSYS_GetSystemType
    HCSYS_GetSystemType.restype = ctypes.c_int64
    HCSYS_GetSystemType.argtypes = []
    
    ret = HCSYS_GetSystemType()
    return ret

# INT64 __stdcall HCSYS_GetTime();
def HD系统_开机经过时间() -> int:
    """
    获取开机到现在过经过的时间（毫秒）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetTime = hd.HCSYS_GetTime
    HCSYS_GetTime.restype = ctypes.c_int64
    HCSYS_GetTime.argtypes = []
    
    ret = HCSYS_GetTime()
    return ret

# INT64 __stdcall HCSYS_Is64Bit();
def HD系统_当前进程是否X64() -> int:
    """
    当前进程是否是64位
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_Is64Bit = hd.HCSYS_Is64Bit
    HCSYS_Is64Bit.restype = ctypes.c_int64
    HCSYS_Is64Bit.argtypes = []
    
    ret = HCSYS_Is64Bit()
    return ret

# INT64 __stdcall HCSYS_IsSurrpotVt();
def HD系统_是否支持vt() -> int:
    """
    是否支持VT
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_IsSurrpotVt = hd.HCSYS_IsSurrpotVt
    HCSYS_IsSurrpotVt.restype = ctypes.c_int64
    HCSYS_IsSurrpotVt.argtypes = []
    
    ret = HCSYS_IsSurrpotVt()
    return ret

# INT64 __stdcall HCSYS_GetScreenPixelDepth();
def HD系统_获取屏幕的色深() -> int:
    """
    获取屏幕的色深
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetScreenPixelDepth = hd.HCSYS_GetScreenPixelDepth
    HCSYS_GetScreenPixelDepth.restype = ctypes.c_int64
    HCSYS_GetScreenPixelDepth.argtypes = []
    
    ret = HCSYS_GetScreenPixelDepth()
    return ret

# INT64 __stdcall HCSYS_SetScreenPixelDepth(int dmBitsPerPel);
def HD系统_设置屏幕的色深(像素深度: int) -> int:
    """
    设置屏幕的色深
    
    Args:
        像素深度: 像素深度值（24/32等）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_SetScreenPixelDepth = hd.HCSYS_SetScreenPixelDepth
    HCSYS_SetScreenPixelDepth.restype = ctypes.c_int64
    HCSYS_SetScreenPixelDepth.argtypes = [ctypes.c_int32]
    
    ret = HCSYS_SetScreenPixelDepth(ctypes.c_int32(像素深度))
    return ret

# INT64 __stdcall HCSYS_GetScreenHeight();
def HD系统_获取屏幕高度() -> int:
    """
    获取屏幕高度
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetScreenHeight = hd.HCSYS_GetScreenHeight
    HCSYS_GetScreenHeight.restype = ctypes.c_int64
    HCSYS_GetScreenHeight.argtypes = []
    
    ret = HCSYS_GetScreenHeight()
    return ret

# INT64 __stdcall HCSYS_GetScreenWidth();
def HD系统_获取屏幕宽度() -> int:
    """
    获取屏幕宽度
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetScreenWidth = hd.HCSYS_GetScreenWidth
    HCSYS_GetScreenWidth.restype = ctypes.c_int64
    HCSYS_GetScreenWidth.argtypes = []
    
    ret = HCSYS_GetScreenWidth()
    return ret

# INT64 __stdcall HCSYS_SetScreen(int width, int height);
def HD系统_设置屏幕分辨率(宽度: int, 高度: int) -> int:
    """
    设置屏幕分辨率
    
    Args:
        宽度: 屏幕宽度
        高度: 屏幕高度
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_SetScreen = hd.HCSYS_SetScreen
    HCSYS_SetScreen.restype = ctypes.c_int64
    HCSYS_SetScreen.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCSYS_SetScreen(ctypes.c_int32(宽度), ctypes.c_int32(高度))
    return ret

# INT64 __stdcall HCSYS_GetCmdRet(char* cmd);
def HD系统_获取CMD命令返回值(命令: str) -> int:
    """
    获取CMD命令返回值（字符串）
    
    Args:
        命令: CMD命令
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCSYS_GetCmdRet = hd.HCSYS_GetCmdRet
    HCSYS_GetCmdRet.restype = ctypes.c_int64
    HCSYS_GetCmdRet.argtypes = [ctypes.c_char_p]
    
    ret = HCSYS_GetCmdRet(auto_encode(命令))
    return ret
