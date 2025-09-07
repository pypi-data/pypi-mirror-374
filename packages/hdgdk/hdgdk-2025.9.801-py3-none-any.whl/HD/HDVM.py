from .config import Config, ctypes
from .config import auto_encode

def HDVM_运行(
    windowsIndex: int,
    vmPath: str,
    vmxSysPath: str,
    bGui: bool = False,
    lparam: str = None,
    vmType: int = 0,
    type_: int = 0
) -> int:
    """
    接口说明:
        运行虚拟机(管理员运行)

    函数原型：
        __int64  __stdcall  HCVM_Run(__int32 windowsIndex, char* vmPath, char* vmxSysPath, BOOL bGui = FALSE, char* lparam = NULL, long vmType = 0, long type = 0);

    参数说明:
        windowsIndex: 窗口序号 表示只是打开虚拟机 注意:大于0表示重置对应窗口序号下的DMA环境
        vmPath: VM安装路径 如:"D:\vm16\"
        vmxSysPath: 虚拟机vmx路径 如:"D:/vmwin10/Windows10x64.vmx"
        bGui: 是否界面GUI显示启动虚拟机
        lparam: 额外命令参数
        vmType: 0 VMware Workstation -T ws(默认) 1 VMware Player -T player
        type_: 默认0 保留

    返回值:
        int: 0 1（查看HD返回值表）

    备注:
        指令:
        D:\vmwin10>D:\vm16\vmrun -T ws start "D:/vmwin10/Windows10x64.vmx" gui lparam
        D:\vmwin10>D:\vm16\vmrun -T ws start "D:/vmwin10/Windows10x64.vmx" nogui lparam
        C++案例:
        auto ret = HCVM_Run(0, "D:\\vm16\\", "D:\\vmwin10\\Windows 10 x64.vmx", TRUE, 0, 0, 0);
    """
    hd = Config.get_hd()
    HCVM_Run = hd.HCVM_Run
    HCVM_Run.restype = ctypes.c_int64
    HCVM_Run.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_char_p, ctypes.c_long, ctypes.c_long]
    vmPath_bytes = auto_encode(vmPath)
    vmxSysPath_bytes = auto_encode(vmxSysPath)
    lparam_bytes = auto_encode(lparam) if lparam else None
    ret = HCVM_Run(
        ctypes.c_int32(windowsIndex),
        vmPath_bytes,
        vmxSysPath_bytes,
        ctypes.c_bool(bGui),
        lparam_bytes,
        ctypes.c_long(vmType),
        ctypes.c_long(type_)
    )
    return ret

def HDVM_重启(
    windowsIndex: int,
    vmPath: str,
    vmxSysPath: str,
    bForceRoot: bool = True,
    bGui: bool = False,
    lparam: str = None,
    vmType: int = 0,
    type_: int = 0
) -> int:
    """
    接口说明:
        重启运行虚拟机(管理员运行)

    函数原型：
        __int64  __stdcall   HCVM_Rerun(__int32 windowsIndex, char* vmPath, char* vmxSysPath, BOOL bForceRoot = TRUE, BOOL bGui = FALSE, char* lparam = NULL, long vmType = 0, long type = 0);

    参数说明:
        windowsIndex: 窗口序号
        vmPath: VM安装路径
        vmxSysPath: 虚拟机vmx路径
        bForceRoot: 是否强制重启（类似断电）反之表示正常重启（需 VMware Tools 支持）
        bGui: 是否界面GUI显示启动虚拟机
        lparam: 额外命令参数
        vmType: 0 VMware Workstation -T ws(默认) 1 VMware Player -T player
        type_: 默认0 保留

    返回值:
        int: 0 1（查看HD返回值表）

    备注:
        指令:
        D:\vmwin10>D:\vm16\vmrun -T ws restart "D:/vmwin10/Windows10x64.vmx" gui lparam
        D:\vmwin10>D:\vm16\vmrun -T ws restart "D:/vmwin10/Windows10x64.vmx" nogui lparam
        C++案例:
        auto ret = HCVM_Rerun(0, "D:\\vm16\\", "D:\\vmwin10\\Windows 10 x64.vmx", m_强制关闭CheckBox.GetCheck(), TRUE, 0, 0, 0);
    """
    hd = Config.get_hd()
    HCVM_Rerun = hd.HCVM_Rerun
    HCVM_Rerun.restype = ctypes.c_int64
    HCVM_Rerun.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_char_p, ctypes.c_long, ctypes.c_long]
    vmPath_bytes = auto_encode(vmPath)
    vmxSysPath_bytes = auto_encode(vmxSysPath)
    lparam_bytes = auto_encode(lparam) if lparam else None
    ret = HCVM_Rerun(
        ctypes.c_int32(windowsIndex),
        vmPath_bytes,
        vmxSysPath_bytes,
        ctypes.c_bool(bForceRoot),
        ctypes.c_bool(bGui),
        lparam_bytes,
        ctypes.c_long(vmType),
        ctypes.c_long(type_)
    )
    return ret

def HDVM_关闭(
    windowsIndex: int,
    vmPath: str,
    vmxSysPath: str,
    bForceRoot: bool = True,
    vmType: int = 0,
    type_: int = 0
) -> int:
    """
    接口说明:
        关闭运行虚拟机(管理员运行)

    函数原型：
        __int64  __stdcall   HCVM_Close(__int32 windowsIndex, char* vmPath, char* vmxSysPath, BOOL bForceRoot = TRUE, long vmType = 0, long type = 0);

    参数说明:
        windowsIndex: 窗口序号
        vmPath: VM安装路径
        vmxSysPath: 虚拟机vmx路径
        bForceRoot: 是否强制重启（类似断电）反之表示正常重启（需 VMware Tools 支持）
        vmType: 0 VMware Workstation -T ws(默认) 1 VMware Player -T player
        type_: 默认0 保留

    返回值:
        int: 0 1（查看HD返回值表）

    备注:
        指令:
        D:\vmwin10>D:\vm16\vmrun -T ws stop "D:/vmwin10/Windows10x64.vmx"
        D:\vmwin10>D:\vm16\vmrun -T ws stop "D:/vmwin10/Windows10x64.vmx"
        C++案例:
        auto ret = HCVM_Close(0, "D:\\vm16\\", "D:\\vmwin10\\Windows 10 x64.vmx", m_强制关闭CheckBox.GetCheck(), 0, 0);
    """
    hd = Config.get_hd()
    HCVM_Close = hd.HCVM_Close
    HCVM_Close.restype = ctypes.c_int64
    HCVM_Close.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_long, ctypes.c_long]
    vmPath_bytes = auto_encode(vmPath)
    vmxSysPath_bytes = auto_encode(vmxSysPath)
    ret = HCVM_Close(
        ctypes.c_int32(windowsIndex),
        vmPath_bytes,
        vmxSysPath_bytes,
        ctypes.c_bool(bForceRoot),
        ctypes.c_long(vmType),
        ctypes.c_long(type_)
    )
    return ret

def HDVM_遍历(
    vmPath: str
) -> int:
    """
    接口说明:
        获取当前正在运行的虚拟机路径 和 总数(管理员运行)

    函数原型：
        __int64  __stdcall   HCVM_List(char* vmPath);

    参数说明:
        vmPath: VM安装路径 如:"D:\vm16\"

    返回值:
        int: 数量
        返回的json: "|"隔开 如:"D:/vmwin10/Windows10x64_1.vmx|D:/vmwin10/Windows10x64_2.vmx|D:/vmwin10/Windows10x64_3.vmx"

    备注:
        无
        C++案例:
        auto ret = HCVM_List("D:\\vm16\\");
    """
    hd = Config.get_hd()
    HCVM_List = hd.HCVM_List
    HCVM_List.restype = ctypes.c_int64
    HCVM_List.argtypes = [ctypes.c_char_p]
    vmPath_bytes = auto_encode(vmPath)
    ret = HCVM_List(vmPath_bytes)
    return ret

def HDVM_是否开启(
    vmPath: str,
    vmxSysPath: str
) -> int:
    """
    接口说明:
        指定虚拟机是否已经开启(管理员运行)

    函数原型：
        __int64  __stdcall   HCVM_IsStart(char* vmPath, char* vmxSysPath);

    参数说明:
        vmPath: VM安装路径 如:"D:\vm16\"
        vmxSysPath: 虚拟机vmx路径 如:"D:/vmwin10/Windows10x64_1.vmx"

    返回值:
        int: 0 1（查看HD返回值表）

    备注:
        无
        C++案例:
        auto ret = HCVM_List("D:\\vm16\\","D:/vmwin10/Windows10x64_1.vmx");
    """
    hd = Config.get_hd()
    HCVM_IsStart = hd.HCVM_IsStart
    HCVM_IsStart.restype = ctypes.c_int64
    HCVM_IsStart.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    vmPath_bytes = auto_encode(vmPath)
    vmxSysPath_bytes = auto_encode(vmxSysPath)
    ret = HCVM_IsStart(vmPath_bytes, vmxSysPath_bytes)
    return ret