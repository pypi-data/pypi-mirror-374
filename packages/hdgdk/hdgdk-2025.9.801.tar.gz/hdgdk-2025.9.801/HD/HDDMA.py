from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCVMDMA_GetVersion(int windowsIndex);
def HDDMA_获取版本号(窗口序号: int) -> int:
    """
    获取DMA服务器版本号
    :param 窗口序号: 窗口序号
    :return: 返回长整数版本号，如240401 格式:24年-04版本号-01小版本号
    """
    hd = Config.get_hd()

    HCVMDMA_GetVersion = hd.HCVMDMA_GetVersion
    HCVMDMA_GetVersion.restype = ctypes.c_int64
    HCVMDMA_GetVersion.argtypes = [ctypes.c_int32]

    return HCVMDMA_GetVersion(ctypes.c_int32(窗口序号))

# INT64 __stdcall HCVMDMA_IsVersion(int windowsIndex);
def HDDMA_版本是否一致(窗口序号: int) -> int:
    """
    判断HD插件的DMA接口和DMA服务器接口版本是否一致
    :param 窗口序号: 窗口序号
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCVMDMA_IsVersion = hd.HCVMDMA_IsVersion
    HCVMDMA_IsVersion.restype = ctypes.c_int64
    HCVMDMA_IsVersion.argtypes = [ctypes.c_int32]

    return HCVMDMA_IsVersion(ctypes.c_int32(窗口序号))

# INT64 __stdcall HCVMDMA_StartServer(char* ip = "0.0.0.0", int port = 6532, char* serverRootPath = "");
def HDDMA_开启服务器(ip: str = "127.0.0.1", port: int = 6532, 服务器exe根目录: str = "") -> int:
    """
    开启DMA服务器
    :param ip: IP地址 (默认127.0.0.1)
    :param port: 端口 (默认6532)
    :param 服务器exe根目录: 兼容指定自定义进程名(全路径\\XXXX.exe) 不指定路径使用内置进程名
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCVMDMA_StartServer = hd.HCVMDMA_StartServer
    HCVMDMA_StartServer.restype = ctypes.c_int64
    HCVMDMA_StartServer.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]

    ip_bytes = auto_encode(ip)
    path_bytes = auto_encode(服务器exe根目录)

    return HCVMDMA_StartServer(ip_bytes, ctypes.c_int32(port), path_bytes)

# INT64 __stdcall HCVMDMA_CloseServer();
def HDDMA_关闭服务器() -> int:
    """
    关闭服务器,同时结束进程
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCVMDMA_CloseServer = hd.HCVMDMA_CloseServer
    HCVMDMA_CloseServer.restype = ctypes.c_int64

    return HCVMDMA_CloseServer()

# INT64 __stdcall HCVMDMA_ServerIsStart();
def HDDMA_服务器是否开启(ip: str = "127.0.0.1", port: int = 6532) -> int:
    """
    接口说明:
        服务器是否已经开启

    函数原型：
        __int64  __stdcall  HCVMDMA_ServerIsStart(char* ip = "127.0.0.1", int port = 6532);

    参数说明:
        ip: 指定服务器IP,指定后可以用来判断服务器是否开启
        port: 指定服务器端口,指定后可以用来判断服务器是否开启

    返回值:
        int: 见HD返回值表

    备注:
        循环检查直到服务器开启成功
        如果使用HCVMDMA_StartServer开启服务器,不指定IP和端口,则使用的是HCVMDMA_ServerIsStart指定的IP和端口
    """
    hd = Config.get_hd()
    HCVMDMA_ServerIsStart = hd.HCVMDMA_ServerIsStart
    HCVMDMA_ServerIsStart.restype = ctypes.c_int64
    HCVMDMA_ServerIsStart.argtypes = [ctypes.c_char_p, ctypes.c_int32]
    ip_bytes = auto_encode(ip)
    ret = HCVMDMA_ServerIsStart(ip_bytes, ctypes.c_int32(port))
    return ret

# INT64 __stdcall HCVMDMA_Init(int windowsIndex, int vmPid, int timeOut = 10000);
def HDDMA_关联虚拟机(窗口序号: int, 虚拟机PID: int, 超时等待时间: int = 10000) -> int:
    """
    初始化并关联虚拟机
    :param 窗口序号: 窗口序号
    :param 虚拟机PID: 虚拟机进程ID (进程名: vmware-vmx.exe)
    :param 超时等待时间: 超时等待时间 (默认10000毫秒)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCVMDMA_Init = hd.HCVMDMA_Init
    HCVMDMA_Init.restype = ctypes.c_int64
    HCVMDMA_Init.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

    return HCVMDMA_Init(ctypes.c_int32(窗口序号), ctypes.c_int32(虚拟机PID), ctypes.c_int32(超时等待时间))

# INT64  __stdcall  HCVMDMA_GetPid(int windowsIndex, char* processName);
def HDDMA_获取PID(窗口序号: int, 进程名: str) -> int:
    """
    通过进程名获取PID
    :param 窗口序号: 窗口序号 (从1开始)
    :param 进程名: 进程名
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_GetPid = hd.HCVMDMA_GetPid
    HCVMDMA_GetPid.restype = ctypes.c_int64
    HCVMDMA_GetPid.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_char_p  # 进程名
    ]

    # 将进程名转换为字节串
    process_name_bytes = auto_encode(进程名)

    # 调用C函数
    ret = HCVMDMA_GetPid(
        ctypes.c_int32(窗口序号),
        process_name_bytes
    )

    return ret

# INT64  __stdcall  HCVMDMA_Read(int windowsIndex, int targetPid, INT64 addr, int addrSzie);
def HDDMA_读地址(窗口序号: int, 目标进程PID: int, 地址: int, 地址大小: int) -> int:
    """
    读地址,仅支持 1 2 4 8 地址大小
    :param 窗口序号: 窗口序号 (从1开始)
    :param 目标进程PID: 虚拟机中的目标进程PID
    :param 地址: 读的地址
    :param 地址大小: 读的大小,仅支持 1 2 4 8 地址大小
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_Read = hd.HCVMDMA_Read
    HCVMDMA_Read.restype = ctypes.c_int64
    HCVMDMA_Read.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 目标进程PID
        ctypes.c_int64,  # 地址
        ctypes.c_int32   # 地址大小
    ]

    # 调用C函数
    ret = HCVMDMA_Read(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(地址),
        ctypes.c_int32(地址大小)
    )

    return ret

# INT64  __stdcall  HCVMDMA_ReadFloat(int windowsIndex, int targetPid, INT64 addr);
def HDDMA_读单浮点(窗口序号: int, 目标进程PID: int, 地址: int) -> int:
    """
    读单浮点数
    :param 窗口序号: 窗口序号 (从1开始)
    :param 目标进程PID: 虚拟机中的目标进程PID
    :param 地址: 读的地址
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_ReadFloat = hd.HCVMDMA_ReadFloat
    HCVMDMA_ReadFloat.restype = ctypes.c_int64
    HCVMDMA_ReadFloat.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 目标进程PID
        ctypes.c_int64   # 地址
    ]

    # 调用C函数
    ret = HCVMDMA_ReadFloat(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(地址)
    )

    return ret

# INT64  __stdcall  HCVMDMA_ReadDouble(int windowsIndex, int targetPid, INT64 addr);
def HDDMA_读双浮点(窗口序号: int, 目标进程PID: int, 地址: int) -> int:
    """
    读双浮点数
    :param 窗口序号: 窗口序号 (从1开始)
    :param 目标进程PID: 虚拟机中的目标进程PID
    :param 地址: 读的地址
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_ReadDouble = hd.HCVMDMA_ReadDouble
    HCVMDMA_ReadDouble.restype = ctypes.c_int64
    HCVMDMA_ReadDouble.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 目标进程PID
        ctypes.c_int64   # 地址
    ]

    # 调用C函数
    ret = HCVMDMA_ReadDouble(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(地址)
    )

    return ret

# INT64  __stdcall  HCVMDMA_ReadBytes(int windowsIndex, int targetPid, INT64 addr, BYTE* buffAddr, int readSzie);
def HDDMA_读字节集(窗口序号: int, 目标进程PID: int, 地址: int, 缓冲区地址, 读字节大小: int) -> int:
    """
    读字节集
    :param 窗口序号: 窗口序号 (从1开始)
    :param 目标进程PID: 虚拟机中的目标进程PID
    :param 地址: 读的地址
    :param 缓冲区地址: 传递一个用于存字节集的缓冲区,一定要大于等于readSzie
    :param 读字节大小: 读的大小,内部限制最大1024字节,不能超过1024
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_ReadBytes = hd.HCVMDMA_ReadBytes
    HCVMDMA_ReadBytes.restype = ctypes.c_int64
    HCVMDMA_ReadBytes.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 目标进程PID
        ctypes.c_int64,  # 地址
        ctypes.POINTER(ctypes.c_ubyte),  # 缓冲区地址
        ctypes.c_int32   # 读字节大小
    ]

    # 调用C函数
    ret = HCVMDMA_ReadBytes(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(地址),
        缓冲区地址,
        ctypes.c_int32(读字节大小)
    )

    return ret

# INT64  __stdcall  HCVMDMA_Write(int windowsIndex, int targetPid, INT64 value, INT64 addr, int addrSzie);
def HDDMA_写地址(窗口序号: int, 目标进程PID: int, 值: int, 地址: int, 地址大小: int) -> int:
    """
    写地址,仅支持 1 2 4 8 地址大小
    :param 窗口序号: 窗口序号 (从1开始)
    :param 目标进程PID: 虚拟机中的目标进程PID
    :param 值: 待写入的值
    :param 地址: 读的地址
    :param 地址大小: 读的大小,仅支持 1 2 4 8 地址大小
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_Write = hd.HCVMDMA_Write
    HCVMDMA_Write.restype = ctypes.c_int64
    HCVMDMA_Write.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 目标进程PID
        ctypes.c_int64,  # 值
        ctypes.c_int64,  # 地址
        ctypes.c_int32   # 地址大小
    ]

    # 调用C函数
    ret = HCVMDMA_Write(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(值),
        ctypes.c_int64(地址),
        ctypes.c_int32(地址大小)
    )

    return ret

# INT64 __stdcall HCVMDMA_WriteFloat(int windowsIndex, int targetPid, float value, INT64 addr);
def HDDMA_写单浮点(窗口序号: int, 目标进程PID: int, 单浮点数值: float, 地址: int) -> int:
    """
    写单浮点数，需要先初始化关联虚拟机HCVMDMA_Init
    
    Args:
        窗口序号: 窗口序号
        目标进程PID: 虚拟机中的目标进程PID
        单浮点数值: 要写入的单浮点数值
        地址: 要写入的地址
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVMDMA_WriteFloat = hd.HCVMDMA_WriteFloat
    HCVMDMA_WriteFloat.restype = ctypes.c_int64
    HCVMDMA_WriteFloat.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_float, ctypes.c_int64]
    
    ret = HCVMDMA_WriteFloat(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_float(单浮点数值),
        ctypes.c_int64(地址)
    )
    return ret

# INT64 __stdcall HCVMDMA_WriteDouble(int windowsIndex, int targetPid, double value, INT64 addr);
def HDDMA_写双浮点(窗口序号: int, 目标进程PID: int, 双浮点数值: float, 地址: int) -> int:
    """
    写双浮点数，需要先初始化关联虚拟机HCVMDMA_Init
    
    Args:
        窗口序号: 窗口序号
        目标进程PID: 虚拟机中的目标进程PID
        双浮点数值: 要写入的双浮点数值
        地址: 要写入的地址
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVMDMA_WriteDouble = hd.HCVMDMA_WriteDouble
    HCVMDMA_WriteDouble.restype = ctypes.c_int64
    HCVMDMA_WriteDouble.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ctypes.c_int64]
    
    ret = HCVMDMA_WriteDouble(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_double(双浮点数值),
        ctypes.c_int64(地址)
    )
    return ret

# INT64 __stdcall HCVMDMA_WriteBytes(int windowsIndex, int targetPid, INT64 addr, BYTE* buffAddr, int writeSize);
def HDDMA_写字节集(窗口序号: int, 目标进程PID: int, 地址: int, 缓冲区地址: int, 写字节大小: int) -> int:
    """
    写字节集，需要先初始化关联虚拟机HCVMDMA_Init
    
    Args:
        窗口序号: 窗口序号
        目标进程PID: 虚拟机中的目标进程PID
        地址: 目标进程中要写的地址
        缓冲区地址: 存储字节集的缓冲区地址
        写字节大小: 写入的字节大小，最大值为1024
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVMDMA_WriteBytes = hd.HCVMDMA_WriteBytes
    HCVMDMA_WriteBytes.restype = ctypes.c_int64
    HCVMDMA_WriteBytes.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int32]
    
    ret = HCVMDMA_WriteBytes(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int64(地址),
        ctypes.c_void_p(缓冲区地址),
        ctypes.c_int32(写字节大小)
    )
    return ret

# INT64 __stdcall HCVMDMA_GetProcAddr(int windowsIndex, int targetPid, char* moduleName, char* procName);
def HDDMA_获取函数(窗口序号: int, 目标进程PID: int, 模块名字: str, 函数名字: str) -> int:
    """
    获取函数地址 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 目标进程PID
    :param 模块名字: 模块名字
    :param 函数名字: 函数名字
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_GetProcAddr = hd.HCVMDMA_GetProcAddr
    HCVMDMA_GetProcAddr.restype = ctypes.c_int64
    HCVMDMA_GetProcAddr.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 目标进程PID
        ctypes.c_char_p,  # 模块名字
        ctypes.c_char_p   # 函数名字
    ]

    # 将模块名字和函数名字转换为字节串
    module_bytes = auto_encode(模块名字)
    proc_bytes = auto_encode(函数名字)

    # 调用C函数
    ret = HCVMDMA_GetProcAddr(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_char_p(module_bytes),
        ctypes.c_char_p(proc_bytes)
    )
    return ret

# INT64  __stdcall  HCVMDMA_GetBaseModule(int windowsIndex, int targetPid);
def HDDMA_获取主模块(窗口序号, 虚拟机中的目标进程PID):
    """
    获取主模块地址 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 目标进程PID
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_GetBaseModule = hd.HCVMDMA_GetBaseModule
    HCVMDMA_GetBaseModule.restype = ctypes.c_int64
    HCVMDMA_GetBaseModule.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32    # 目标进程PID
    ]

    # 调用C函数
    ret = HCVMDMA_GetBaseModule(ctypes.c_int32(窗口序号), ctypes.c_int32(虚拟机中的目标进程PID))
    return ret

# INT64  __stdcall  HCVMDMA_GetModule(int windowsIndex, int targetPid, char* moduleName);
def HDDMA_获取模块(窗口序号, 虚拟机中的目标进程PID, 模块名字):
    """
    获取模块地址 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 目标进程PID
    :param 模块名字: 模块名字，如ntdll.dll
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_GetModule = hd.HCVMDMA_GetModule
    HCVMDMA_GetModule.restype = ctypes.c_int64
    HCVMDMA_GetModule.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 目标进程PID
        ctypes.c_char_p   # 模块名字
    ]

    # 将模块名字转换为字节串
    module_bytes = auto_encode(模块名字)

    # 调用C函数
    ret = HCVMDMA_GetModule(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_char_p(module_bytes)
    )
    return ret

# INT64  __stdcall HCVMDMA_ShellCodeInitX64(int windowsIndex, int targetPid, INT64 hookAddr, int hookAddrSzie);
def HDDMA_获取执行环境X64(窗口序号, 虚拟机中的目标进程PID, HOOK地址, 破坏的汇编字节数):
    """
    初始化获取一个某个进程(x64)的执行环境句柄
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param HOOK地址: HOOK地址 (如:一些进程频繁用到的函数 sleep closehandle deletedc 等等)
    :param 破坏的汇编字节数: 破坏的汇编字节数, 必须是完整的汇编, 不能被打断
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_ShellCodeInitX64 = hd.HCVMDMA_ShellCodeInitX64
    HCVMDMA_ShellCodeInitX64.restype = ctypes.c_int64
    HCVMDMA_ShellCodeInitX64.argtypes = [
        ctypes.c_int32,    # 窗口序号
        ctypes.c_int32,    # 虚拟机中的目标进程PID
        ctypes.c_int64,    # HOOK地址
        ctypes.c_int32     # 破坏的汇编字节数
    ]

    # 调用C函数
    ret = HCVMDMA_ShellCodeInitX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(HOOK地址),
        ctypes.c_int32(破坏的汇编字节数)
    )
    return ret

# INT64  __stdcall HCVMDMA_RunShellCodeX64(int windowsIndex, int targetPid, INT64 excuteEnvAddr, char* shellCodeStr);
def HDDMA_CALLX64(窗口序号, 虚拟机中的目标进程PID, 执行环境句柄, shellCode机器码):
    """
    通过指定一个初进程(x64)的执行环境句柄来执行CALL
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param 执行环境句柄: 执行环境句柄, 通过HCVMDMA_ShellCodeInitX64 获取
    :param shellCode机器码: 自己写的汇编shellcode机器码, 最大限制不超过1024字节
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RunShellCodeX64 = hd.HCVMDMA_RunShellCodeX64
    HCVMDMA_RunShellCodeX64.restype = ctypes.c_int64
    HCVMDMA_RunShellCodeX64.argtypes = [
        ctypes.c_int32,    # 窗口序号
        ctypes.c_int32,    # 虚拟机中的目标进程PID
        ctypes.c_int64,    # 执行环境句柄
        ctypes.c_char_p   # shellCode机器码
    ]

    # 将shellCode机器码转换为字节串
    shell_code_bytes = auto_encode(shellCode机器码)

    # 调用C函数
    ret = HCVMDMA_RunShellCodeX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(执行环境句柄),
        ctypes.c_char_p(shell_code_bytes)
    )
    return ret

# INT64  __stdcall HCVMDMA_ShellCodeInitx86(int windowsIndex, int targetPid, INT64 hookAddr, int hookAddrSize);
def HDDMA_获取执行环境x86(窗口序号, 虚拟机中的目标进程PID, HOOK地址, HOOK字节数):
    """
    初始化获取一个某个进程(x86)的执行环境句柄
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param HOOK地址: HOOK地址，例如一些进程频繁用到的函数，如sleep, closehandle, deletedc等
    :param HOOK字节数: 破坏的汇编字节数，必须是完整的汇编，不能被打断
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_ShellCodeInitx86 = hd.HCVMDMA_ShellCodeInitx86
    HCVMDMA_ShellCodeInitx86.restype = ctypes.c_int64
    HCVMDMA_ShellCodeInitx86.argtypes = [
        ctypes.c_int32,    # 窗口序号
        ctypes.c_int32,    # 虚拟机中的目标进程PID
        ctypes.c_int64,    # HOOK地址
        ctypes.c_int32     # HOOK字节数
    ]

    # 调用C函数
    ret = HCVMDMA_ShellCodeInitx86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(HOOK地址),
        ctypes.c_int32(HOOK字节数)
    )
    return ret

# INT64  __stdcall HCVMDMA_RunShellCodex86(int windowsIndex, int targetPid, INT64 excuteEnvAddr, char* shellCodeStr);
def HDDMA_CALLx86(窗口序号, 虚拟机中的目标进程PID, 执行环境句柄, shellCode机器码):
    """
    通过指定一个初进程(x86)的执行环境句柄来执行CALL
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param 执行环境句柄: 执行环境句柄, 通过HCVMDMA_ShellCodeInitx86 获取
    :param shellCode机器码: 自己写的汇编shellcode机器码, 最大限制不超过1024字节
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RunShellCodex86 = hd.HCVMDMA_RunShellCodex86
    HCVMDMA_RunShellCodex86.restype = ctypes.c_int64
    HCVMDMA_RunShellCodex86.argtypes = [
        ctypes.c_int32,    # 窗口序号
        ctypes.c_int32,    # 虚拟机中的目标进程PID
        ctypes.c_int64,    # 执行环境句柄
        ctypes.c_char_p   # shellCode机器码
    ]

    # 将shellCode机器码转换为字节串
    shell_code_bytes = auto_encode(shellCode机器码)

    # 调用C函数
    ret = HCVMDMA_RunShellCodex86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(执行环境句柄),
        ctypes.c_char_p(shell_code_bytes)
    )
    return ret

# INT64  __stdcall HCVMDMA_FindCodeX86(int windowsIndex, int targetPid, CHAR* code, int offset, int num, int type = 1, CHAR* moduleName = NULL);
def HDDMA_搜索特征码x86(窗口序号, 虚拟机中的目标进程PID, 特征码字符串地址, 偏移, 次数, 类型=1, 模块名字=None):
    """
    特征码搜索(X86)
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param 特征码字符串地址: 特征码字符串地址 (支持??)
    :param 偏移: 正负偏移
    :param 次数: 找到的第几次 从1开始
    :param 类型: 获取的是(基地址/CALL地址/直接地址/地址中的值) 1为地址 2为基地址 3为CALL 4为地址中的值
    :param 模块名字: 在指定的模块中搜索, 默认为主模块 NULL为默认
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_FindCodeX86 = hd.HCVMDMA_FindCodeX86
    HCVMDMA_FindCodeX86.restype = ctypes.c_int64
    HCVMDMA_FindCodeX86.argtypes = [
        ctypes.c_int32,    # 窗口序号
        ctypes.c_int32,    # 虚拟机中的目标进程PID
        ctypes.c_char_p,   # 特征码字符串地址
        ctypes.c_int32,    # 偏移
        ctypes.c_int32,    # 次数
        ctypes.c_int32,    # 类型
        ctypes.c_char_p    # 模块名字
    ]

    # 将特征码字符串地址和模块名字转换为字节串
    code_bytes = auto_encode(特征码字符串地址)
    module_name_bytes = auto_encode(模块名字 or '')

    # 调用C函数
    ret = HCVMDMA_FindCodeX86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_char_p(code_bytes),
        ctypes.c_int32(偏移),
        ctypes.c_int32(次数),
        ctypes.c_int32(类型),
        ctypes.c_char_p(module_name_bytes)
    )
    return ret

# INT64  __stdcall   HCVMDMA_FindCodeX86Ex(int windowsIndex, int targetPid, INT64 beginAddr, int addrSize, CHAR* code, int offset, int num, int type = 1);
def HDDMA_搜索特征码x86Ex(窗口序号, 虚拟机中的目标进程PID, 开始地址, 搜索范围大小, 特征码字符串地址, 正负偏移, 次数, 类型=1):
    """
    特征码搜索(X86)(扩展版本) 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 目标进程PID
    :param 开始地址: 搜索的开始地址
    :param 搜索范围大小: 搜索范围的大小，单位是字节
    :param 特征码字符串地址: 特征码字符串地址，支持??，可以是十六进制
    :param 正负偏移: 偏移量，支持正负数
    :param 次数: 找到的第几次，从1开始
    :param 类型: 需要获取的类型，1为地址，2为基地址，3为CALL地址，4为地址中的值（默认1）
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_FindCodeX86Ex = hd.HCVMDMA_FindCodeX86Ex
    HCVMDMA_FindCodeX86Ex.restype = ctypes.c_int64
    HCVMDMA_FindCodeX86Ex.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 目标进程PID
        ctypes.c_int64,   # 开始地址
        ctypes.c_int32,   # 搜索范围大小
        ctypes.c_char_p,  # 特征码字符串地址
        ctypes.c_int32,   # 偏移量
        ctypes.c_int32,   # 次数
        ctypes.c_int32    # 类型
    ]

    # 将特征码字符串转换为字节串
    code_bytes = auto_encode(特征码字符串地址)

    # 调用C函数
    ret = HCVMDMA_FindCodeX86Ex(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(开始地址),
        ctypes.c_int32(搜索范围大小),
        ctypes.c_char_p(code_bytes),
        ctypes.c_int32(正负偏移),
        ctypes.c_int32(次数),
        ctypes.c_int32(类型)
    )
    return ret

# INT64 __stdcall HCVMDMA_FindCodeX64(int windowsIndex, int targetPid, CHAR* code, int offset, int num, int type = 1, CHAR* moduleName = NULL)
def HDDMA_搜索特征码x64(窗口序号, 虚拟机中的目标进程PID, 特征码字符串, 偏移, 次数, 类型=1, 模块名字=None):
    """
    特征码搜索 (X64)

    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param 特征码字符串: 特征码字符串地址(支持??)
    :param 偏移: 正负偏移
    :param 次数: 找到的第几次，从1开始
    :param 类型: 获取的是(基地址/CALL地址/直接地址/地址中的值) 1为地址，2为基地址，3为CALL，4为地址中的值
    :param 模块名字: 在指定的模块中搜索, 默认为主模块。NULL为默认
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_FindCodeX64 = hd.HCVMDMA_FindCodeX64
    HCVMDMA_FindCodeX64.restype = ctypes.c_int64
    HCVMDMA_FindCodeX64.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 虚拟机中的目标进程PID
        ctypes.c_char_p,  # 特征码字符串
        ctypes.c_int32,  # 偏移
        ctypes.c_int32,  # 次数
        ctypes.c_int32,  # 类型
        ctypes.c_char_p  # 模块名字 (可选，默认 NULL)
    ]

    # 将特征码字符串和模块名字转换为字节串
    code_bytes = auto_encode(特征码字符串)
    module_name_bytes = auto_encode(模块名字) if 模块名字 else None

    # 调用C函数
    ret = HCVMDMA_FindCodeX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        code_bytes,
        ctypes.c_int32(偏移),
        ctypes.c_int32(次数),
        ctypes.c_int32(类型),
        ctypes.c_char_p(module_name_bytes) if module_name_bytes else None
    )

    return ret

# INT64 __stdcall HCVMDMA_FindCodeX64Ex(int windowsIndex, int targetPid, INT64 beginAddr, int addrSize, CHAR* code, int offset, int num, int type = 1)
def HDDMA_搜索特征码x64Ex(窗口序号, 虚拟机中的目标进程PID, 开始地址, 地址大小, 特征码字符串, 偏移, 次数, 类型=1):
    """
    特征码搜索 (X64) 扩展版本

    :param 窗口序号: 窗口序号
    :param 虚拟机中的目标进程PID: 虚拟机中的目标进程PID
    :param 开始地址: 搜索的开始地址
    :param 地址大小: 搜索范围大小（单位：字节）
    :param 特征码字符串: 特征码字符串地址(支持??)
    :param 偏移: 正负偏移
    :param 次数: 找到的第几次，从1开始
    :param 类型: 获取的是(基地址/CALL地址/直接地址/地址中的值) 1为地址，2为基地址，3为CALL，4为地址中的值
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_FindCodeX64Ex = hd.HCVMDMA_FindCodeX64Ex
    HCVMDMA_FindCodeX64Ex.restype = ctypes.c_int64
    HCVMDMA_FindCodeX64Ex.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 虚拟机中的目标进程PID
        ctypes.c_int64,  # 开始地址
        ctypes.c_int32,  # 地址大小
        ctypes.c_char_p,  # 特征码字符串
        ctypes.c_int32,  # 偏移
        ctypes.c_int32,  # 次数
        ctypes.c_int32  # 类型
    ]

    # 将特征码字符串转换为字节串
    code_bytes = auto_encode(特征码字符串)

    # 调用C函数
    ret = HCVMDMA_FindCodeX64Ex(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(虚拟机中的目标进程PID),
        ctypes.c_int64(开始地址),
        ctypes.c_int32(地址大小),
        code_bytes,
        ctypes.c_int32(偏移),
        ctypes.c_int32(次数),
        ctypes.c_int32(类型)
    )

    return ret

# INT64 __stdcall HCVMDMA_Close(int windowsIndex)
def HDDMA_断开虚拟机(窗口序号):
    """
    卸载并关闭连接虚拟机

    :param 窗口序号: 窗口序号
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_Close = hd.HCVMDMA_Close
    HCVMDMA_Close.restype = ctypes.c_int64
    HCVMDMA_Close.argtypes = [ctypes.c_int32]  # 窗口序号

    # 调用C函数
    ret = HCVMDMA_Close(ctypes.c_int32(窗口序号))

    return ret

# INT64 __stdcall HCVMDMA_InitCapture(int windowsIndex)
def HDDMA_获取截图环境(窗口序号):
    """
    初始化截图环境

    :param 窗口序号: 窗口序号
    :return: 截图环境句柄 (成功: 返回句柄，失败: 返回错误代码)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_InitCapture = hd.HCVMDMA_InitCapture
    HCVMDMA_InitCapture.restype = ctypes.c_int64
    HCVMDMA_InitCapture.argtypes = [ctypes.c_int32]  # 窗口序号

    # 调用C函数
    ret = HCVMDMA_InitCapture(ctypes.c_int32(窗口序号))

    return ret

# INT64 __stdcall HCVMDMA_InitMouseKey(int windowsIndex)
def HDDMA_获取键鼠环境(窗口序号):
    """
    初始化键鼠环境

    :param 窗口序号: 窗口序号
    :return: 键鼠环境句柄 (成功: 返回句柄，失败: 返回错误代码)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_InitMouseKey = hd.HCVMDMA_InitMouseKey
    HCVMDMA_InitMouseKey.restype = ctypes.c_int64
    HCVMDMA_InitMouseKey.argtypes = [ctypes.c_int32]  # 窗口序号

    # 调用C函数
    ret = HCVMDMA_InitMouseKey(ctypes.c_int32(窗口序号))

    return ret

# INT64 __stdcall HCVMDMA_Capture(int windowsIndex, INT64 captureEnvAddr)
def HDDMA_截图一次(窗口序号, 截图环境句柄):
    """
    截图一次

    :param 窗口序号: 窗口序号
    :param 截图环境句柄: 截图环境句柄，由 `HCVMDMA_InitCapture` 获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_Capture = hd.HCVMDMA_Capture
    HCVMDMA_Capture.restype = ctypes.c_int64
    HCVMDMA_Capture.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 截图环境句柄

    # 调用C函数
    ret = HCVMDMA_Capture(ctypes.c_int32(窗口序号), ctypes.c_int64(截图环境句柄))

    return ret

# INT64 __stdcall HCVMDMA_OpenCapture(int windowsIndex, INT64 captureEnvAddr)
def HDDMA_开启截图(窗口序号, 截图环境句柄):
    """
    开启截图(内部会开启一条线程循环调用HCVMDMA_Capture)
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :param captureEnvAddr: 截图环境句柄，由HCVMDMA_InitCapture获取返回
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_OpenCapture = hd.HCVMDMA_OpenCapture
    HCVMDMA_OpenCapture.restype = ctypes.c_int64
    HCVMDMA_OpenCapture.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 截图环境句柄

    # 调用C函数
    ret = HCVMDMA_OpenCapture(ctypes.c_int32(窗口序号), ctypes.c_int64(截图环境句柄))

    return ret

# INT64 __stdcall HCVMDMA_CloseCapture(int windowsIndex)
def HDDMA_关闭截图(窗口序号):
    """
    关闭截图(内部会关闭之前开启的线程)
    和HCVMDMA_OpenCapture是一对接口
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_CloseCapture = hd.HCVMDMA_CloseCapture
    HCVMDMA_CloseCapture.restype = ctypes.c_int64
    HCVMDMA_CloseCapture.argtypes = [ctypes.c_int32]  # 窗口序号

    # 调用C函数
    ret = HCVMDMA_CloseCapture(ctypes.c_int32(窗口序号))

    return ret

# INT64 __stdcall HCVMDMA_MoveTo(int windowsIndex, int x, int y, INT64 mkbEnvAddr)
def HDDMA_鼠标移动(窗口序号, x, y, 键鼠环境):
    """
    鼠标移动 (不包含轨迹)
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :param x: 虚拟机屏幕坐标X
    :param y: 虚拟机屏幕坐标Y
    :param mkbEnvAddr: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_MoveTo = hd.HCVMDMA_MoveTo
    HCVMDMA_MoveTo.restype = ctypes.c_int64
    HCVMDMA_MoveTo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]  # 窗口序号, x, y, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_MoveTo(ctypes.c_int32(窗口序号), ctypes.c_int32(x), ctypes.c_int32(y), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_LeftDown(int windowsIndex, INT64 mkbEnvAddr)
def HDDMA_左键按下(窗口序号, 键鼠环境):
    """
    鼠标左键按下
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :param mkbEnvAddr: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_LeftDown = hd.HCVMDMA_LeftDown
    HCVMDMA_LeftDown.restype = ctypes.c_int64
    HCVMDMA_LeftDown.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_LeftDown(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_LeftUp(int windowsIndex, INT64 mkbEnvAddr)
def HDDMA_左键弹起(窗口序号, 键鼠环境):
    """
    鼠标左键弹起
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :param mkbEnvAddr: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_LeftUp = hd.HCVMDMA_LeftUp
    HCVMDMA_LeftUp.restype = ctypes.c_int64
    HCVMDMA_LeftUp.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_LeftUp(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_LeftClick(int windowsIndex, int mis, INT64 mkbEnvAddr)
def HDDMA_左键点击(窗口序号, mis, 键鼠环境):
    """
    鼠标左键点击
    需要先初始化关联虚拟机HCVMDMA_Init

    :param windowsIndex: 窗口序号
    :param mis: 按下和弹起之前的间隔时间(毫秒)
    :param mkbEnvAddr: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_LeftClick = hd.HCVMDMA_LeftClick
    HCVMDMA_LeftClick.restype = ctypes.c_int64
    HCVMDMA_LeftClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]  # 窗口序号, mis, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_LeftClick(ctypes.c_int32(窗口序号), ctypes.c_int32(mis), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_LeftDoubleClick(int windowsIndex, int mis, INT64 mkbEnvAddr)
def HDDMA_左键双击(窗口序号: int, mis: int, 键鼠环境: int) -> int:
    """
    鼠标左键双击
    需要先初始化关联虚拟机HCVMDMA_Init

    :param 窗口序号: 窗口序号
    :param mis: 按下和弹起之前的间隔时间(毫秒)
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_LeftDoubleClick = hd.HCVMDMA_LeftDoubleClick
    HCVMDMA_LeftDoubleClick.restype = ctypes.c_int64
    HCVMDMA_LeftDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]  # 窗口序号, mis, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_LeftDoubleClick(ctypes.c_int32(窗口序号), ctypes.c_int32(mis), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_MiddleDown(int windowsIndex, INT64 mkbEnvAddr)
def HDDMA_中键按下(窗口序号: int, 键鼠环境: int) -> int:
    """
    鼠标中键按下
    需要先初始化关联虚拟机HCVMDMA_Init

    :param 窗口序号: 窗口序号
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_MiddleDown = hd.HCVMDMA_MiddleDown
    HCVMDMA_MiddleDown.restype = ctypes.c_int64
    HCVMDMA_MiddleDown.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_MiddleDown(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_MiddleUp(int windowsIndex, INT64 mkbEnvAddr)
def HDDMA_中键弹起(窗口序号: int, 键鼠环境: int) -> int:
    """
    鼠标中键弹起
    需要先初始化关联虚拟机HCVMDMA_Init

    :param 窗口序号: 窗口序号
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_MiddleUp = hd.HCVMDMA_MiddleUp
    HCVMDMA_MiddleUp.restype = ctypes.c_int64
    HCVMDMA_MiddleUp.argtypes = [ctypes.c_int32, ctypes.c_int64]  # 窗口序号, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_MiddleUp(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_MiddleClick(int windowsIndex, int mis, INT64 mkbEnvAddr)
def HDDMA_中键点击(窗口序号: int, mis: int, 键鼠环境: int) -> int:
    """
    鼠标中键点击
    需要先初始化关联虚拟机HCVMDMA_Init

    :param 窗口序号: 窗口序号
    :param mis: 按下和弹起之前的间隔时间(毫秒)
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_MiddleClick = hd.HCVMDMA_MiddleClick
    HCVMDMA_MiddleClick.restype = ctypes.c_int64
    HCVMDMA_MiddleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]  # 窗口序号, mis, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_MiddleClick(ctypes.c_int32(窗口序号), ctypes.c_int32(mis), ctypes.c_int64(键鼠环境))

    return ret

# INT64 __stdcall HCVMDMA_MiddleDoubleClick(int windowsIndex, int mis, INT64 mkbEnvAddr)
def HDDMA_中键双击(窗口序号: int, mis: int, 键鼠环境: int) -> int:
    """
    鼠标中键双击
    需要先初始化关联虚拟机HCVMDMA_Init

    :param 窗口序号: 窗口序号
    :param mis: 按下和弹起之前的间隔时间(毫秒)
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_MiddleDoubleClick = hd.HCVMDMA_MiddleDoubleClick
    HCVMDMA_MiddleDoubleClick.restype = ctypes.c_int64
    HCVMDMA_MiddleDoubleClick.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]  # 窗口序号, mis, 键鼠环境

    # 调用C函数
    ret = HCVMDMA_MiddleDoubleClick(ctypes.c_int32(窗口序号), ctypes.c_int32(mis), ctypes.c_int64(键鼠环境))

    return ret

# INT64  __stdcall  HCVMDMA_RightDown(int windowsIndex, INT64 mkbEnvAddr);
def HDDMA_右键按下(窗口序号, mkbEnvAddr):
    """
    鼠标右键按下 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param mkbEnvAddr: 键鼠环境，由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RightDown = hd.HCVMDMA_RightDown
    HCVMDMA_RightDown.restype = ctypes.c_int64
    HCVMDMA_RightDown.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_RightDown(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(mkbEnvAddr)
    )
    return ret

# INT64  __stdcall  HCVMDMA_RightUp(int windowsIndex, INT64 mkbEnvAddr);
def HDDMA_右键弹起(窗口序号, mkbEnvAddr):
    """
    鼠标右键弹起 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param mkbEnvAddr: 键鼠环境，由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RightUp = hd.HCVMDMA_RightUp
    HCVMDMA_RightUp.restype = ctypes.c_int64
    HCVMDMA_RightUp.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_RightUp(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(mkbEnvAddr)
    )
    return ret

# INT64  __stdcall  HCVMDMA_RightClick(int windowsIndex, int mis, INT64 mkbEnvAddr);
def HDDMA_右键点击(窗口序号, 间隔时间, mkbEnvAddr):
    """
    鼠标右键点击 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 间隔时间: 按下和弹起之前的间隔时间 (毫秒)
    :param mkbEnvAddr: 键鼠环境，由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RightClick = hd.HCVMDMA_RightClick
    HCVMDMA_RightClick.restype = ctypes.c_int64
    HCVMDMA_RightClick.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 间隔时间 (毫秒)
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_RightClick(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(间隔时间),
        ctypes.c_int64(mkbEnvAddr)
    )
    return ret

# INT64  __stdcall  HCVMDMA_RightDoubleClick(int windowsIndex, int mis, INT64 mkbEnvAddr);
def HDDMA_右键双击(窗口序号, 间隔时间, mkbEnvAddr):
    """
    鼠标右键双击 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 间隔时间: 按下和弹起之前的间隔时间 (毫秒)
    :param mkbEnvAddr: 键鼠环境，由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_RightDoubleClick = hd.HCVMDMA_RightDoubleClick
    HCVMDMA_RightDoubleClick.restype = ctypes.c_int64
    HCVMDMA_RightDoubleClick.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 间隔时间 (毫秒)
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_RightDoubleClick(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(间隔时间),
        ctypes.c_int64(mkbEnvAddr)
    )
    return ret

# INT64  __stdcall  HCVMDMA_WheelUp(int windowsIndex, INT64 mkbEnvAddr);
def HDDMA_滚轮滚上(窗口序号: int, 键鼠环境: int) -> int:
    """
    鼠标滚轮滚上 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_WheelUp = hd.HCVMDMA_WheelUp
    HCVMDMA_WheelUp.restype = ctypes.c_int64
    HCVMDMA_WheelUp.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_WheelUp(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_WheelDown(int windowsIndex, INT64 mkbEnvAddr);
def HDDMA_滚轮滚下(窗口序号: int, 键鼠环境: int) -> int:
    """
    鼠标滚轮滚下 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_WheelDown = hd.HCVMDMA_WheelDown
    HCVMDMA_WheelDown.restype = ctypes.c_int64
    HCVMDMA_WheelDown.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_WheelDown(ctypes.c_int32(窗口序号), ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_KeyDown(int windowsIndex, int keyCode, INT64 mkbEnvAddr);
def HDDMA_键盘按下(窗口序号: int, 虚拟键码值: int, 键鼠环境: int) -> int:
    """
    键盘按下 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟键码值: 虚拟键码值
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_KeyDown = hd.HCVMDMA_KeyDown
    HCVMDMA_KeyDown.restype = ctypes.c_int64
    HCVMDMA_KeyDown.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 虚拟键码值
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_KeyDown(ctypes.c_int32(窗口序号), ctypes.c_int32(虚拟键码值), ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_KeyUp(int windowsIndex, int keyCode, INT64 mkbEnvAddr);
def HDDMA_键盘按上(窗口序号: int, 虚拟键码值: int, 键鼠环境: int) -> int:
    """
    键盘按上 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟键码值: 虚拟键码值
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_KeyUp = hd.HCVMDMA_KeyUp
    HCVMDMA_KeyUp.restype = ctypes.c_int64
    HCVMDMA_KeyUp.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 虚拟键码值
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_KeyUp(ctypes.c_int32(窗口序号), ctypes.c_int32(虚拟键码值), ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_KeyClick(int windowsIndex, int keyCode, int mis, INT64 mkbEnvAddr);
def HDDMA_键盘敲击(窗口序号: int, 虚拟键码值: int, mis: int, 键鼠环境: int) -> int:
    """
    键盘敲击 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param 虚拟键码值: 虚拟键码值
    :param mis: 按下和弹起之前的间隔时间(毫秒)
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_KeyClick = hd.HCVMDMA_KeyClick
    HCVMDMA_KeyClick.restype = ctypes.c_int64
    HCVMDMA_KeyClick.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_int32,   # 虚拟键码值
        ctypes.c_int32,   # 按下和弹起之前的间隔时间
        ctypes.c_int64    # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_KeyClick(ctypes.c_int32(窗口序号), ctypes.c_int32(虚拟键码值), ctypes.c_int32(mis), ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_SendUnicode(int windowsIndex, wchar_t* strUnicode, INT64 mkbEnvAddr);
def HDDMA_发送文本Unicode(窗口序号: int, strUnicode: str, 键鼠环境: int) -> int:
    """
    发送unicode字符串 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param strUnicode: unicode编码字符串 (最大100长度, 一个字2个字节)
    :param 键鼠环境: 键鼠环境, 由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_SendUnicode = hd.HCVMDMA_SendUnicode
    HCVMDMA_SendUnicode.restype = ctypes.c_int64
    HCVMDMA_SendUnicode.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_wchar_p,     # unicode编码字符串
        ctypes.c_int64        # 键鼠环境
    ]

    # 调用C函数
    ret = HCVMDMA_SendUnicode(ctypes.c_int32(窗口序号), strUnicode, ctypes.c_int64(键鼠环境))
    return ret

# INT64  __stdcall  HCVMDMA_SendAscii(int windowsIndex, char* strAscii, INT64 mkbEnvAddr);
def HDDMA_发送文本Ascii(窗口序号: int, strAscii: str, 键鼠环境: int) -> int:
    """
    发送ascii字符串 需要先初始化关联虚拟机HCVMDMA_Init
    :param 窗口序号: 窗口序号
    :param strAscii: ascii编码字符串 (最大200字符，每个字符1字节，共200字节)，例如数字、英文、符号等
    :param 键鼠环境: 键鼠环境，由HCVMDMA_InitMouseKey获取
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCVMDMA_SendAscii = hd.HCVMDMA_SendAscii
    HCVMDMA_SendAscii.restype = ctypes.c_int64
    HCVMDMA_SendAscii.argtypes = [
        ctypes.c_int32,   # 窗口序号
        ctypes.c_char_p,  # ascii字符串
        ctypes.c_int64    # 键鼠环境
    ]

    # 将字符串转换为字节串
    ascii_bytes = auto_encode(strAscii)

    # 调用C函数
    ret = HCVMDMA_SendAscii(
        ctypes.c_int32(窗口序号),
        ctypes.c_char_p(ascii_bytes),
        ctypes.c_int64(键鼠环境)
    )
    return ret

def HDDMA_获取PID列表(
    window_index: int
) -> int:
    """
    获取PID列表
    Args:
        window_index (int): 窗口序号
    Returns:
        int: PID数量（大于0为数量，小于等于0为错误），具体进程信息需用HCEnv_GetRetJson获取
        返回JSON:具体进程PID从最近json获取字符串 pid1,name1|pid2,name2|pid3,name3|  "|"分隔符 每个进程信息
    """
    hd = Config.get_hd()
    HCVMDMA_GetPidList = hd.HCVMDMA_GetPidList
    HCVMDMA_GetPidList.restype = ctypes.c_int64
    HCVMDMA_GetPidList.argtypes = [ctypes.c_int32]
    ret = HCVMDMA_GetPidList(ctypes.c_int32(window_index))
    return ret

def HDDMA_PID是否存在(
    window_index: int,
    pid: int
) -> int:
    """
    接口说明:
        对应虚拟机中的进程PID是否存在

    函数原型:
        __int64  __stdcall  HCVMDMA_IsExistPid(__int32 windowsIndex,__int32 pid);

    参数说明:
        window_index: 窗口序号
        pid: 进程PID

    返回值:
        int: 0 或 1（查看HD返回值表）

    备注:
        需要先初始化关联虚拟机HCVMDMA_Init
    """
    hd = Config.get_hd()
    HCVMDMA_IsExistPid = hd.HCVMDMA_IsExistPid
    HCVMDMA_IsExistPid.restype = ctypes.c_int64
    HCVMDMA_IsExistPid.argtypes = [ctypes.c_int32, ctypes.c_int32]
    ret = HCVMDMA_IsExistPid(ctypes.c_int32(window_index), ctypes.c_int32(pid))
    return ret