from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCModule_AddComponent(int winIndex, char* account, char* password, char* componentPath, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, INT64 addType, BOOL autoInit, BOOL mainThread);
def HD插件_加载插件(窗口序号: int, 账号: str, 密码: str, 组件路径: str, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, l5: int = 0, l6: int = 0, 添加方式: int = -1, 是否自动初始化: bool = True, 是否主线程: bool = False) -> int:
    """
    添加自定义组件
    
    Args:
        窗口序号: 窗口序号
        账号: 开发者账号
        密码: 开发者密码
        组件路径: 组件绝对路径（请勿使用中文）
        rcx: CALL参数1
        rdx: CALL参数2
        r8: CALL参数3
        r9: CALL参数4
        l5: CALL参数5
        l6: CALL参数6
        添加方式: -1默认/1无痕不可卸载/2普通可卸载
        是否自动初始化: 自动调用初始化接口
        是否主线程: 需挂接主线程
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCModule_AddComponent = hd.HCModule_AddComponent
    HCModule_AddComponent.restype = ctypes.c_int64
    HCModule_AddComponent.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCModule_AddComponent(
        ctypes.c_int32(窗口序号),
        auto_encode(账号),
        auto_encode(密码),
        auto_encode(组件路径),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        ctypes.c_int64(添加方式),
        ctypes.c_bool(是否自动初始化),
        ctypes.c_bool(是否主线程)
    )
    return ret

# INT64 __stdcall HCModule_DeleteComponent(int winIndex, char* componentName, BOOL mainThread);
def HD插件_卸载插件(窗口序号: int, 组件名: str, 是否主线程: bool = False) -> int:
    """
    无痕卸载DLL组件
    
    Args:
        窗口序号: 窗口序号
        组件名: 组件文件名（不含.dll）
        是否主线程: 需挂接主线程
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCModule_DeleteComponent = hd.HCModule_DeleteComponent
    HCModule_DeleteComponent.restype = ctypes.c_int64
    HCModule_DeleteComponent.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCModule_DeleteComponent(
        ctypes.c_int32(窗口序号),
        auto_encode(组件名),
        ctypes.c_bool(是否主线程)
    )
    return ret

# INT64 __stdcall HCModule_CALL(int winIndex, char* componentName, char* functionName, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, BOOL mainThread);
def HD插件_CALL(窗口序号: int, 组件名: str, 函数名: str, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, l5: int = 0, l6: int = 0, 是否主线程: bool = False) -> int:
    """
    调用自定义组件接口
    
    Args:
        窗口序号: 窗口序号
        组件名: 组件文件名（不含.dll）
        函数名: 目标函数名称
        rcx: CALL参数1
        rdx: CALL参数2
        r8: CALL参数3
        r9: CALL参数4
        l5: CALL参数5
        l6: CALL参数6
        是否主线程: 需挂接主线程
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCModule_CALL = hd.HCModule_CALL
    HCModule_CALL.restype = ctypes.c_int64
    HCModule_CALL.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
    
    ret = HCModule_CALL(
        ctypes.c_int32(窗口序号),
        auto_encode(组件名),
        auto_encode(函数名),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        ctypes.c_bool(是否主线程)
    )
    return ret

# INT64 __stdcall HCModule_CALLEx(int winIndex, char* componentName, char* functionName, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, char* buffer, int bufferSize, BOOL mainThread);
def HD插件_CALLEx(窗口序号: int, 组件名: str, 函数名: str, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, l5: int = 0, l6: int = 0, 缓冲区数据: bytes = None, 缓冲区大小: int = 0, 是否主线程: bool = False) -> int:
    """
    调用自定义组件接口（扩展版本）
    
    Args:
        窗口序号: 窗口序号
        组件名: 组件文件名（不含.dll）
        函数名: 目标函数名称
        rcx: CALL参数1
        rdx: CALL参数2
        r8: CALL参数3
        r9: CALL参数4
        l5: CALL参数5
        l6: CALL参数6
        缓冲区数据: 二进制缓冲区数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        缓冲区大小: 缓冲区大小（最大支持1024*100字节）
        是否主线程: 需挂接主线程
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCModule_CALLEx = hd.HCModule_CALLEx
    HCModule_CALLEx.restype = ctypes.c_int64
    HCModule_CALLEx.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool]
    
    # 处理缓冲区数据
    if 缓冲区数据 is not None:
        buffer_ptr = ctypes.c_char_p(缓冲区数据)
    else:
        buffer_ptr = None
    
    ret = HCModule_CALLEx(
        ctypes.c_int32(窗口序号),
        auto_encode(组件名),
        auto_encode(函数名),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        buffer_ptr,
        ctypes.c_int32(缓冲区大小),
        ctypes.c_bool(是否主线程)
    )
    return ret


