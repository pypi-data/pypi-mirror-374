from .config import Config, ctypes
from .config import auto_encode

# char* __stdcall HCEnv_GetRetJson(__int32 窗口序号);
def HD通用_获取最近返回Json(窗口序号: int) -> bytes:
    """
    获取最近一次调用接口返回的json字符串
    
    Args:
        窗口序号: 窗口序号 可以包含0 表示中控
        
    Returns:
        bytes: JSON字符串 (字节格式)
    """
    hd = Config.get_hd()

    func = hd.HCEnv_GetRetJson
    func.restype = ctypes.c_char_p
    func.argtypes = [ctypes.c_int]

    return func(窗口序号)

# INT64 __stdcall HCEnv_GetRetValue(__int32 窗口序号);
def HD通用_获取最近返回值(窗口序号: int) -> int:
    """
    获取最近一次调用接口返回的值(用于检测是否有错)
    
    Args:
        窗口序号: 窗口序号 可以包含0 表示中控
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HCEnv_GetRetValue
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]

    return func(窗口序号)

# char* __stdcall HCEnv_GetErrorStr(__int32 ret);
def HD通用_获取返回值说明(ret: int) -> bytes:
    """
    根据返回值获取错误说明
    
    Args:
        ret: 返回值代码
        
    Returns:
        bytes: 错误说明字符串 (字节格式)
    """
    hd = Config.get_hd()

    func = hd.HCEnv_GetErrorStr
    func.restype = ctypes.c_char_p
    func.argtypes = [ctypes.c_int]

    return func(ret)

# INT64 __stdcall HCEnv_GetLastError();
def HD通用_获取最近API返回值() -> int:
    """
    获取最近API调用的返回值
    
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HCEnv_GetLastError
    func.restype = ctypes.c_int64
    func.argtypes = []

    return func()

# INT64 __stdcall HCInject_GetLastInfo(__int32 窗口序号);
def HD通用_获取当前插件状态值(窗口序号: int) -> int:
    """
    获取当前环境搭建流程中的操作信息
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HCInject_GetLastInfo
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]

    return func(窗口序号)

# __int64 __stdcall HC_CALL(__int32 窗口序号, __int64 CALL地址, __int64 rcx = 0, __int64 rdx = 0, __int64 r8 = 0, __int64 r9 = 0, __int64 lparam5 = 0, __int64 lparam6 = 0, __int64 lparam7 = 0, __int64 lparam8 = 0, BOOL 是否主线程调用 = FALSE);
def HD通用_CALLX64(窗口序号: int, CALL地址: int, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, lparam5: int = 0, lparam6: int = 0, lparam7: int = 0, lparam8: int = 0, 是否主线程调用: bool = False) -> int:
    """
    通用CALL(适合X64),支持0-8个参数
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        CALL地址: CALL地址
        rcx: CALL参数 (默认0)
        rdx: CALL参数 (默认0)
        r8: CALL参数 (默认0)
        r9: CALL参数 (默认0)
        lparam5: CALL参数 (默认0)
        lparam6: CALL参数 (默认0)
        lparam7: CALL参数 (默认0)
        lparam8: CALL参数 (默认0)
        是否主线程调用: 是否主线程调用这个CALL,需要挂接主线程 (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_CALL
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]

    return func(窗口序号, CALL地址, rcx, rdx, r8, r9, lparam5, lparam6, lparam7, lparam8, 是否主线程调用)

# __int64 __stdcall HC_CALLX86(__int32 窗口序号, __int32 CALL地址, __int32 ecx = 0,__int32 lparam1 = 0, __int32 lparam2 = 0, __int32 lparam3 = 0, __int32 lparam4 = 0, __int32 lparam5 = 0, __int32 lparam6 = 0, __int32 lparam7 = 0, __int32 lparam8 = 0, __int32 lparamNum = 0, __int32 addEsp = -1, BOOL 是否主线程调用 = FALSE);
def HD通用_CALLX86(窗口序号: int, CALL地址: int, ecx: int = 0, lparam1: int = 0, lparam2: int = 0, lparam3: int = 0, lparam4: int = 0, lparam5: int = 0, lparam6: int = 0, lparam7: int = 0, lparam8: int = 0, lparamNum: int = 0, addEsp: int = -1, 是否主线程调用: bool = False) -> int:
    """
    通用CALL(适合X86),支持0到8个参数
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        CALL地址: 4字节接口地址
        ecx: 对象参数 (默认0)
        lparam1: 第一个参数 (默认0)
        lparam2: 第二个参数 (默认0)
        lparam3: 第三个参数 (默认0)
        lparam4: 第四个参数 (默认0)
        lparam5: 第五个参数 (默认0)
        lparam6: 第六个参数 (默认0)
        lparam7: 第七个参数 (默认0)
        lparam8: 第八个参数 (默认0)
        lparamNum: 当前接口地址的传递的参数数量(支持0到8个参数) (默认0)
        addEsp: 如果调用的接口地址是内平栈就置为-1,如果是外平栈就设置为参数数量(lparamNum)*0x4 (默认-1)
        是否主线程调用: 是否主线程调用这个CALL,需要挂接主线程 (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_CALLX86
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]

    return func(窗口序号, CALL地址, ecx, lparam1, lparam2, lparam3, lparam4, lparam5, lparam6, lparam7, lparam8, lparamNum, addEsp, 是否主线程调用)

# __int64 __stdcall HC_HookMainThread(__int32 窗口序号, __int64 窗口句柄);
def HD通用_挂接主线程(窗口序号: int, 窗口句柄: int) -> int:
    """
    挂接主线程
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        窗口句柄: 窗口句柄
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    func = hd.HC_HookMainThread
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64]

    return func(窗口序号, 窗口句柄)