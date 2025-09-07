from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCInject_Init(int 窗口序号, BOOL 是否重置);
def HD通讯_初始化(窗口序号: int, 是否重置: bool = False) -> int:
    """
    初始化插件环境
    
    Args:
        窗口序号: 窗口序号，从1开始
        是否重置: 是否重置，默认为False
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_Init = hd.HCInject_Init
    HCInject_Init.restype = ctypes.c_int64
    HCInject_Init.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCInject_Init(ctypes.c_int32(窗口序号), ctypes.c_bool(是否重置))
    return ret

# INT64 __stdcall HCInject_InitEx(int 窗口序号, char* 预加载LUA模块全路径, BOOL 是否重置);
def HD通讯_初始化Ex(窗口序号: int, 预加载LUA模块全路径: str, 是否重置: bool = False) -> int:
    """
    初始化插件环境扩展版本
    
    Args:
        窗口序号: 窗口序号，从1开始
        预加载LUA模块全路径: 指定一个LUA文件路径+文件名，当插件被加载的时候会自动执行这个LUA文件，通讯后执行
        是否重置: 是否重置
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_InitEx = hd.HCInject_InitEx
    HCInject_InitEx.restype = ctypes.c_int64
    HCInject_InitEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_bool
    ]
    
    ret = HCInject_InitEx(
        ctypes.c_int32(窗口序号), 
        auto_encode(预加载LUA模块全路径), 
        ctypes.c_bool(是否重置)
    )
    return ret

# INT64 __stdcall HCInject_InitExx(int 窗口序号, char* 预加载DLL模块全路径, char* 预加载LUA模块全路径, int addType, BOOL 是否重置);
def HD通讯_初始化Exx(窗口序号: int, 预加载DLL模块全路径: str = None, 预加载LUA模块全路径: str = None, 添加类型: int = -1, 是否重置: bool = False) -> int:
    """
    初始化插件环境扩展扩展版本
    
    Args:
        窗口序号: 窗口序号，从1开始
        预加载DLL模块全路径: 指定一个预加载的DLL，通讯前直接加载
        预加载LUA模块全路径: 指定一个LUA文件路径+文件名，当插件被加载的时候会自动执行这个LUA文件，通讯后执行
        添加类型: -1/0/1无痕无模块加载DLL，2普通加载DLL
        是否重置: 是否重置
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_InitExx = hd.HCInject_InitExx
    HCInject_InitExx.restype = ctypes.c_int64
    HCInject_InitExx.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    dll_path = auto_encode(预加载DLL模块全路径) if 预加载DLL模块全路径 else None
    lua_path = auto_encode(预加载LUA模块全路径) if 预加载LUA模块全路径 else None
    
    ret = HCInject_InitExx(
        ctypes.c_int32(窗口序号), 
        dll_path,
        lua_path,
        ctypes.c_int32(添加类型), 
        ctypes.c_bool(是否重置)
    )
    return ret

# INT64 __stdcall HCInject_GetPid(int 窗口序号);
def HD通讯_获取PID(窗口序号: int) -> int:
    """
    获取打开的进程PID
    
    Args:
        窗口序号: 窗口序号，从1开始
    
    Returns:
        int: 进程PID
    """
    hd = Config.get_hd()
    
    HCInject_GetPid = hd.HCInject_GetPid
    HCInject_GetPid.restype = ctypes.c_int64
    HCInject_GetPid.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCInject_GetPid(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCInject_GetPrePid(int 窗口序号);
def HD通讯_获取之前PID(窗口序号: int) -> int:
    """
    获取打开的进程之前的PID，可以用于重连
    
    Args:
        窗口序号: 窗口序号，从1开始
    
    Returns:
        int: 之前的进程PID
    """
    hd = Config.get_hd()
    
    HCInject_GetPrePid = hd.HCInject_GetPrePid
    HCInject_GetPrePid.restype = ctypes.c_int64
    HCInject_GetPrePid.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCInject_GetPrePid(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCInject_SetData(int 窗口序号, void* 用户数据缓冲区, int 数据大小);
def HD通讯_存数据(窗口序号: int, 用户数据缓冲区: bytes, 数据大小: int) -> int:
    """
    存自定义二进制数据
    
    Args:
        窗口序号: 窗口序号，从1开始
        用户数据缓冲区: 数据的来源缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: 数据的来源缓冲区中有效数据的大小，总大小1024字节
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_SetData = hd.HCInject_SetData
    HCInject_SetData.restype = ctypes.c_int64
    HCInject_SetData.argtypes = [
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.c_int32
    ]
    
    用户数据缓冲区_ptr = ctypes.cast(用户数据缓冲区, ctypes.c_void_p).value if 用户数据缓冲区 else ctypes.c_void_p(0)
    
    ret = HCInject_SetData(
        ctypes.c_int32(窗口序号), 
        用户数据缓冲区_ptr, 
        ctypes.c_int32(数据大小)
    )
    return ret

# INT64 __stdcall HCInject_GetData(int 窗口序号, void* 用户数据缓冲区, int 缓冲区大小);
def HD通讯_取数据(窗口序号: int, 用户数据缓冲区, 缓冲区大小: int) -> int:
    """
    取自定义二进制数据
    
    Args:
        窗口序号: 窗口序号，从1开始
        用户数据缓冲区: 数据的存储缓冲区，取的数据就是用HCInject_SetData接口存的数据
        缓冲区大小: 数据的存储缓冲区数据的大小，不能小于等于0，从内部取的数据最大为1024
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_GetData = hd.HCInject_GetData
    HCInject_GetData.restype = ctypes.c_int64
    HCInject_GetData.argtypes = [
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.c_int32
    ]
    
    用户数据缓冲区_ptr = ctypes.cast(用户数据缓冲区, ctypes.c_void_p).value if 用户数据缓冲区 else ctypes.c_void_p(0)
    
    ret = HCInject_GetData(
        ctypes.c_int32(窗口序号), 
        用户数据缓冲区_ptr, 
        ctypes.c_int32(缓冲区大小)
    )
    return ret

# INT64 __stdcall HCInject_GetPreWinIndex(int pid);
def HD通讯_获取绑定窗口序号(进程PID: int) -> int:
    """
    通过进程PID尝试拿到绑定的窗口序号
    
    Args:
        进程PID: 指定一个进程PID
    
    Returns:
        int: 绑定的窗口序号
    """
    hd = Config.get_hd()
    
    HCInject_GetPreWinIndex = hd.HCInject_GetPreWinIndex
    HCInject_GetPreWinIndex.restype = ctypes.c_int64
    HCInject_GetPreWinIndex.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCInject_GetPreWinIndex(ctypes.c_int32(进程PID))
    return ret

# INT64 __stdcall HCInject_GetHwnd(int 窗口序号, char* className, char* title, int filter, BOOL bType, int mis);
def HD通讯_获取窗口句柄(窗口序号: int, 窗口类名: str, 窗口标题: str, 过滤器: int, 是否模糊匹配: bool, 循环毫秒: int) -> int:
    """
    获取窗口句柄，内部是通过PID获取窗口句柄，需要先安装好插件到目标进程
    
    Args:
        窗口序号: 窗口序号，从1开始
        窗口类名: 窗口类名，不指定为NULL/0
        窗口标题: 窗口标题，不指定为NULL/0
        过滤器: 1标题 2类名 8检测是否无父窗口 16检查窗口句柄是否有效，多个标识可以用|累加
        是否模糊匹配: True为模糊匹配，False为完全匹配
        循环毫秒: 循环检查毫秒数，<=0表示不需要循环获取，>0表示内部循环获取句柄直到有值
    
    Returns:
        int: 窗口句柄
    """
    hd = Config.get_hd()
    
    HCInject_GetHwnd = hd.HCInject_GetHwnd
    HCInject_GetHwnd.restype = ctypes.c_int64
    HCInject_GetHwnd.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int32,
        ctypes.c_bool,
        ctypes.c_int32
    ]
    
    ret = HCInject_GetHwnd(
        ctypes.c_int32(窗口序号), 
        auto_encode(窗口类名), 
        auto_encode(窗口标题), 
        ctypes.c_int32(过滤器), 
        ctypes.c_bool(是否模糊匹配), 
        ctypes.c_int32(循环毫秒)
    )
    return ret

# INT64 __stdcall HCInject_GetHwndEx(int 窗口序号);
def HD通讯_获取窗口句柄Ex(窗口序号: int) -> int:
    """
    获取窗口句柄扩展版本，需要内置，一般不需要调用这个获取句柄
    
    Args:
        窗口序号: 窗口序号，从1开始
    
    Returns:
        int: 窗口句柄
    """
    hd = Config.get_hd()
    
    HCInject_GetHwndEx = hd.HCInject_GetHwndEx
    HCInject_GetHwndEx.restype = ctypes.c_int64
    HCInject_GetHwndEx.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCInject_GetHwndEx(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCInject_Continue(int 窗口序号);
def HD通讯_继续(窗口序号: int) -> int:
    """
    继续环境加载操作
    
    Args:
        窗口序号: 窗口序号，从1开始
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCInject_Continue = hd.HCInject_Continue
    HCInject_Continue.restype = ctypes.c_int64
    HCInject_Continue.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCInject_Continue(ctypes.c_int32(窗口序号))
    return ret
