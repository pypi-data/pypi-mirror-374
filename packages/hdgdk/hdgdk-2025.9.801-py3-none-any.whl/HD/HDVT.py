from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCHDVT_AllocateMemory(int pid, int size);
def HDVT_申请内存(进程PID: int, 内存大小: int) -> int:
    """
    VT驱动申请内存
    
    Args:
        进程PID: 目标进程PID
        内存大小: 申请内存大小（字节）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_AllocateMemory = hd.HCHDVT_AllocateMemory
    HCHDVT_AllocateMemory.restype = ctypes.c_int64
    HCHDVT_AllocateMemory.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCHDVT_AllocateMemory(ctypes.c_int32(进程PID), ctypes.c_int32(内存大小))
    return ret

# INT64 __stdcall HCHDVT_FreeMemory(int pid, INT64 addr, int size);
def HDVT_释放内存(进程PID: int, 内存地址: int, 内存大小: int) -> int:
    """
    VT驱动释放内存
    
    Args:
        进程PID: 目标进程PID
        内存地址: 释放地址（由HCHDVT_AllocateMemory申请的内存地址）
        内存大小: 申请内存大小（字节）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_FreeMemory = hd.HCHDVT_FreeMemory
    HCHDVT_FreeMemory.restype = ctypes.c_int64
    HCHDVT_FreeMemory.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32]
    
    ret = HCHDVT_FreeMemory(ctypes.c_int32(进程PID), ctypes.c_int64(内存地址), ctypes.c_int32(内存大小))
    return ret

# INT64 __stdcall HCHDVT_Read(int pid, INT64 addr, void* buffer, int size);
def HDVT_读内存(进程PID: int, 内存地址: int, 数据缓冲区, 读取大小: int) -> int:
    """
    VT驱动读内存
    
    Args:
        进程PID: 目标进程PID
        内存地址: 读取的内存地址
        数据缓冲区: 读数据缓冲区（ctypes数组对象，可用create_string_buffer创建）
        读取大小: 读取的大小（字节）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_Read = hd.HCHDVT_Read
    HCHDVT_Read.restype = ctypes.c_int64
    HCHDVT_Read.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32]
    
    buffer_ptr = ctypes.cast(数据缓冲区, ctypes.c_void_p)
    
    ret = HCHDVT_Read(ctypes.c_int32(进程PID), ctypes.c_int64(内存地址), buffer_ptr, ctypes.c_int32(读取大小))
    return ret

# INT64 __stdcall HCHDVT_Write(int pid, INT64 addr, void* buffer, int size);
def HDVT_写内存(进程PID: int, 内存地址: int, 数据缓冲区, 写入大小: int) -> int:
    """
    VT驱动写内存
    
    Args:
        进程PID: 目标进程PID
        内存地址: 内存写入地址
        数据缓冲区: 写入数据缓冲区（ctypes数组对象，可用create_string_buffer创建）
        写入大小: 写入数据的大小（字节）
    
    Returns:
        int: 驱动返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_Write = hd.HCHDVT_Write
    HCHDVT_Write.restype = ctypes.c_int64
    HCHDVT_Write.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32]
    
    ret = HCHDVT_Write(ctypes.c_int32(进程PID), ctypes.c_int64(内存地址), 数据缓冲区, ctypes.c_int32(写入大小))
    return ret

# INT64 __stdcall HCHDVT_GetModule(int pid, char* moduleName);
def HDVT_获取模块地址(进程PID: int, 模块名称: str) -> int:
    """
    VT驱动获取模块基地址
    
    Args:
        进程PID: 目标进程PID
        模块名称: 模块名称（例如："kernel32.dll"）
    
    Returns:
        int: 模块地址（若返回负值为错误码，参照HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_GetModule = hd.HCHDVT_GetModule
    HCHDVT_GetModule.restype = ctypes.c_int64
    HCHDVT_GetModule.argtypes = [ctypes.c_int32, ctypes.c_char_p]
    
    ret = HCHDVT_GetModule(ctypes.c_int32(进程PID), auto_encode(模块名称))
    return ret

# INT64 __stdcall HCHDVT_GetModuleFun(int pid, INT64 moduleAddr, char* functionName);
def HDVT_获取模块函数地址(进程PID: int, 模块地址: int, 函数名称: str) -> int:
    """
    VT驱动获取模块内函数地址
    
    Args:
        进程PID: 目标进程PID
        模块地址: 模块基地址
        函数名称: 函数名称（ASCII编码的字符串）
    
    Returns:
        int: 函数地址值
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_GetModuleFun = hd.HCHDVT_GetModuleFun
    HCHDVT_GetModuleFun.restype = ctypes.c_int64
    HCHDVT_GetModuleFun.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_char_p]
    
    ret = HCHDVT_GetModuleFun(ctypes.c_int32(进程PID), ctypes.c_int64(模块地址), auto_encode(函数名称))
    return ret

# INT64 __stdcall HCHDVT_Hook(int pid, INT64 addr, void* hookData, int size, int hookType);
def HDVT_无痕HOOK(进程PID: int, HOOK地址: int, HOOK数据: bytes, 数据大小: int, HOOK类型: int) -> int:
    """
    VT驱动无痕HOOK
    
    Args:
        进程PID: 目标进程PID
        HOOK地址: HOOK的内存地址
        HOOK数据: HOOK数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: HOOK数据大小
        HOOK类型: HOOK类型
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_Hook = hd.HCHDVT_Hook
    HCHDVT_Hook.restype = ctypes.c_int64
    HCHDVT_Hook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCHDVT_Hook(ctypes.c_int32(进程PID), ctypes.c_int64(HOOK地址), HOOK数据, ctypes.c_int32(数据大小), ctypes.c_int32(HOOK类型))
    return ret

# INT64 __stdcall HCHDVT_RemoteCall(int pid, void* shellcodeData, int size);
def HDVT_远程执行(进程PID: int, 执行数据: bytes, 数据大小: int = None) -> int:
    """
    VT驱动远程执行
    
    Args:
        进程PID: 目标进程PID
        执行数据: 执行数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: 执行数据大小（可选）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_RemoteCall = hd.HCHDVT_RemoteCall
    HCHDVT_RemoteCall.restype = ctypes.c_int64
    HCHDVT_RemoteCall.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
    
    if 数据大小 is None:
        数据大小 = len(执行数据)
    
    ret = HCHDVT_RemoteCall(ctypes.c_int32(进程PID), 执行数据, ctypes.c_int32(数据大小))
    return ret

# INT64 __stdcall HCHDVT_InjectDllX64(int pid, void* dllData, int size);
def HDVT_DLL无痕注入X64(进程PID: int, DLL数据: bytes, 数据大小: int = None) -> int:
    """
    VT驱动DLL无痕注入X64
    
    Args:
        进程PID: 目标进程PID
        DLL数据: DLL数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: DLL数据大小（可选）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_InjectDllX64 = hd.HCHDVT_InjectDllX64
    HCHDVT_InjectDllX64.restype = ctypes.c_int64
    HCHDVT_InjectDllX64.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
    
    if 数据大小 is None:
        数据大小 = len(DLL数据)
    
    ret = HCHDVT_InjectDllX64(ctypes.c_int32(进程PID), DLL数据, ctypes.c_int32(数据大小))
    return ret

# INT64 __stdcall HCHDVT_InjectDllX86(int pid, void* dllData, int size);
def HDVT_DLL无痕注入X86(进程PID: int, DLL数据: bytes, 数据大小: int = None) -> int:
    """
    VT驱动DLL无痕注入X86
    
    Args:
        进程PID: 目标进程PID
        DLL数据: DLL数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: DLL数据大小（可选）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_InjectDllX86 = hd.HCHDVT_InjectDllX86
    HCHDVT_InjectDllX86.restype = ctypes.c_int64
    HCHDVT_InjectDllX86.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32]
    
    if 数据大小 is None:
        数据大小 = len(DLL数据)
    
    ret = HCHDVT_InjectDllX86(ctypes.c_int32(进程PID), DLL数据, ctypes.c_int32(数据大小))
    return ret

# INT64 __stdcall HCHDVT_InstallPlugX64(int pid);
def HDVT_安装插件X64(进程PID: int) -> int:
    """
    VT驱动安装插件X64
    
    Args:
        进程PID: 目标进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_InstallPlugX64 = hd.HCHDVT_InstallPlugX64
    HCHDVT_InstallPlugX64.restype = ctypes.c_int64
    HCHDVT_InstallPlugX64.argtypes = [ctypes.c_int32]
    
    ret = HCHDVT_InstallPlugX64(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCHDVT_InstallPlugX86(int pid);
def HDVT_安装插件X86(进程PID: int) -> int:
    """
    VT驱动安装插件X86
    
    Args:
        进程PID: 目标进程PID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        需要调用HCHD_LoadDrv2传递参数2来安装HDVT驱动
    """
    hd = Config.get_hd()
    
    HCHDVT_InstallPlugX86 = hd.HCHDVT_InstallPlugX86
    HCHDVT_InstallPlugX86.restype = ctypes.c_int64
    HCHDVT_InstallPlugX86.argtypes = [ctypes.c_int32]
    
    ret = HCHDVT_InstallPlugX86(ctypes.c_int32(进程PID))
    return ret



