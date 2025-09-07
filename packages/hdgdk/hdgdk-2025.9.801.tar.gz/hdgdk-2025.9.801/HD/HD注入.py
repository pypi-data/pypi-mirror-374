from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCN_NormalInstallPlugX86(int pid);
def HD注入_普通安装插件X86(进程PID: int) -> int:
    """
    HD普通安装插件(X86),不需要安装驱动,这个不是无痕无模块注入,只支持32位的
    :param 进程PID: 进程PID
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCN_NormalInstallPlugX86 = hd.HCN_NormalInstallPlugX86
    HCN_NormalInstallPlugX86.restype = ctypes.c_int64
    HCN_NormalInstallPlugX86.argtypes = [ctypes.c_int32]

    ret = HCN_NormalInstallPlugX86(ctypes.c_int32(进程PID))

    return ret


# INT64 __stdcall HCN_NormalInstallPlugX86Ex(INT64 topHwnd);
def HD注入_普通安装插件X86Ex(窗口句柄: int) -> int:
    """
    HD普通安装插件(扩展版本X86),不需要安装驱动,这个不是无痕无模块注入,只支持32位的
    :param 窗口句柄: 窗口句柄
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCN_NormalInstallPlugX86Ex = hd.HCN_NormalInstallPlugX86Ex
    HCN_NormalInstallPlugX86Ex.restype = ctypes.c_int64
    HCN_NormalInstallPlugX86Ex.argtypes = [ctypes.c_int64]

    ret = HCN_NormalInstallPlugX86Ex(ctypes.c_int64(窗口句柄))

    return ret


# INT64 __stdcall HCN_NormalInstallPlugX64(int pid);
def HD注入_普通安装插件X64(进程PID: int) -> int:
    """
    HD普通安装插件(X64),不需要安装驱动,这个不是无痕无模块注入,只支持64位的
    :param 进程PID: 进程PID
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCN_NormalInstallPlugX64 = hd.HCN_NormalInstallPlugX64
    HCN_NormalInstallPlugX64.restype = ctypes.c_int64
    HCN_NormalInstallPlugX64.argtypes = [ctypes.c_int32]

    ret = HCN_NormalInstallPlugX64(ctypes.c_int32(进程PID))

    return ret


# INT64 __stdcall HCN_NormalInstallPlugX64Ex(INT64 topHwnd);
def HD注入_普通安装插件X64Ex(窗口句柄: int) -> int:
    """
    HD普通安装插件(扩展版本X64),不需要安装驱动,这个不是无痕无模块注入,只支持64位的
    :param 窗口句柄: 窗口句柄
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCN_NormalInstallPlugX64Ex = hd.HCN_NormalInstallPlugX64Ex
    HCN_NormalInstallPlugX64Ex.restype = ctypes.c_int64
    HCN_NormalInstallPlugX64Ex.argtypes = [ctypes.c_int64]

    ret = HCN_NormalInstallPlugX64Ex(ctypes.c_int64(窗口句柄))

    return ret


# INT64 __stdcall HCHD_NormalInstallPlugX86X64(int pid, int dllBits, BOOL bWait);
def HD注入_驱动安装插件(进程PID: int, DLL位数: int, 是否等待: bool = True) -> int:
    """
    把插件安装到指定进程中,不是无痕无模块注入(方式1)
    :param 进程PID: 进程PID
    :param DLL位数: DLL位数
    :param 是否等待: 是否等待 (已废弃无效) (默认True)
    :return: 返回值代码 (查看HD驱动返回值表)
    """
    hd = Config.get_hd()

    HCHD_NormalInstallPlugX86X64 = hd.HCHD_NormalInstallPlugX86X64
    HCHD_NormalInstallPlugX86X64.restype = ctypes.c_int64
    HCHD_NormalInstallPlugX86X64.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]

    ret = HCHD_NormalInstallPlugX86X64(
        ctypes.c_int32(进程PID),
        ctypes.c_int32(DLL位数),
        ctypes.c_bool(是否等待)
    )

    return ret


# INT64 __stdcall HCHD_NormalInjectX86X64ByFile(int pid, char *DLL绝对路径A, BOOL bWait);
def HD注入_驱动注入DLL(进程PID: int, DLL绝对路径: str, 是否等待: bool = True) -> int:
    """
    把DLL注入到指定进程中,不是无痕无模块注入(方式1)
    :param 进程PID: 进程PID
    :param DLL绝对路径: DLL全路径
    :param 是否等待: 是否等待 (已废弃无效) (默认True)
    :return: 返回值代码 (查看HD驱动返回值表)
    """
    hd = Config.get_hd()

    HCHD_NormalInjectX86X64ByFile = hd.HCHD_NormalInjectX86X64ByFile
    HCHD_NormalInjectX86X64ByFile.restype = ctypes.c_int64
    HCHD_NormalInjectX86X64ByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    dll_path_bytes = auto_encode(DLL绝对路径)

    ret = HCHD_NormalInjectX86X64ByFile(
        ctypes.c_int32(进程PID),
        dll_path_bytes,
        ctypes.c_bool(是否等待)
    )

    return ret


# INT64 __stdcall HCHD_NormalInstallPlugX86X64Ex(int pid, int dllBits, BOOL bWait);
def HD注入_驱动安装插件Ex(进程PID: int, DLL位数: int, 是否等待: bool = True) -> int:
    """
    把插件安装到指定进程中,不是无痕无模块注入(方式2,方式1的加强版本)
    :param 进程PID: 进程PID
    :param DLL位数: DLL位数
    :param 是否等待: 是否等待 (已废弃无效) (默认True)
    :return: 返回值代码 (查看HD驱动返回值表)
    """
    hd = Config.get_hd()

    HCHD_NormalInstallPlugX86X64Ex = hd.HCHD_NormalInstallPlugX86X64Ex
    HCHD_NormalInstallPlugX86X64Ex.restype = ctypes.c_int64
    HCHD_NormalInstallPlugX86X64Ex.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]

    ret = HCHD_NormalInstallPlugX86X64Ex(
        ctypes.c_int32(进程PID),
        ctypes.c_int32(DLL位数),
        ctypes.c_bool(是否等待)
    )

    return ret


# INT64 __stdcall HCHD_NormalInjectX86X64ByFileEx(int pid, char *DLL绝对路径A, BOOL bWait);
def HD注入_驱动注入DLLEx(进程PID: int, DLL绝对路径: str, 是否等待: bool = True) -> int:
    """
    把DLL注入到指定进程中,不是无痕无模块注入(方式2,方式1的加强版本)
    :param 进程PID: 进程PID
    :param DLL绝对路径: DLL全路径
    :param 是否等待: 是否等待 (已废弃无效) (默认True)
    :return: 返回值代码 (查看HD驱动返回值表)
    """
    hd = Config.get_hd()

    HCHD_NormalInjectX86X64ByFileEx = hd.HCHD_NormalInjectX86X64ByFileEx
    HCHD_NormalInjectX86X64ByFileEx.restype = ctypes.c_int64
    HCHD_NormalInjectX86X64ByFileEx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    dll_path_bytes = auto_encode(DLL绝对路径)

    ret = HCHD_NormalInjectX86X64ByFileEx(
        ctypes.c_int32(进程PID),
        dll_path_bytes,
        ctypes.c_bool(是否等待)
    )

    return ret


# INT64 __stdcall HCInject_SetPlugin(char* 发布版本DLL名, char* 调试版本DLL名);
def HD注入_设置插件信息(发布版本DLL名: str = None, 调试版本DLL名: str = None) -> int:
    """
    设置插件信息
    :param 发布版本DLL名: 发布版本DLL名 (为空则根据不同版本内置了DLL名字) (默认None)
    :param 调试版本DLL名: 调试版本DLL名 (为空则根据不同版本内置了DLL名字) (默认None)
    :return: 返回值代码 (查看HD驱动返回值表)
    """
    hd = Config.get_hd()

    HCInject_SetPlugin = hd.HCInject_SetPlugin
    HCInject_SetPlugin.restype = ctypes.c_int64
    HCInject_SetPlugin.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    # 使用auto_encode自动转换编码（如果为None则传递NULL）
    release_dll_bytes = auto_encode(发布版本DLL名) if 发布版本DLL名 else None
    debug_dll_bytes = auto_encode(调试版本DLL名) if 调试版本DLL名 else None

    ret = HCInject_SetPlugin(release_dll_bytes, debug_dll_bytes)

    return ret