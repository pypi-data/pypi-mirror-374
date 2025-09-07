from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCLUA_ReadFile(int winIndex, char* filePath, int luaID, BOOL exec, BOOL needRet, BOOL mainThread);
def HDLUA_读文件(窗口序号: int, 文件路径: str, LUA标识符: int, 是否执行: bool = False, 是否需要返回值: bool = False, 是否主线程: bool = False) -> str:
    """
    执行或加载LUA文件
    
    Args:
        窗口序号: 窗口索引（1到最大多开数）
        文件路径: LUA脚本完整路径
        LUA标识符: 线程标识符（0-100），当needRet=True时必须唯一
        是否执行: True=立即执行脚本并注入接口，False=仅注入接口不执行
        是否需要返回值: True=阻塞模式直到执行完成，False=异步执行
        是否主线程: True=在主线程上下文执行，False=后台线程执行
    
    Returns:
        str: JSON字符串，格式：{"error": 错误码, "ret": 执行结果, "data": 附加数据}
    """
    hd = Config.get_hd()
    
    HCLUA_ReadFile = hd.HCLUA_ReadFile
    HCLUA_ReadFile.restype = ctypes.c_char_p
    HCLUA_ReadFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCLUA_ReadFile(
        ctypes.c_int32(窗口序号),
        auto_encode(文件路径),
        ctypes.c_int32(LUA标识符),
        ctypes.c_bool(是否执行),
        ctypes.c_bool(是否需要返回值),
        ctypes.c_bool(是否主线程)
    )
    return ret.decode('utf-8') if ret else ""

# INT64 __stdcall HCLUA_CloseLua(int winIndex, int luaID);
def HDLUA_结束LUA(窗口序号: int, LUA标识符: int = -1) -> int:
    """
    终止LUA线程运行
    
    Args:
        窗口序号: 绑定的窗口索引
        LUA标识符: -1=终止所有线程，其他数值=终止指定标识符的线程
    
    Returns:
        int: 操作结果代码（负数表示失败）
    """
    hd = Config.get_hd()
    
    HCLUA_CloseLua = hd.HCLUA_CloseLua
    HCLUA_CloseLua.restype = ctypes.c_int64
    HCLUA_CloseLua.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCLUA_CloseLua(ctypes.c_int32(窗口序号), ctypes.c_int32(LUA标识符))
    return ret

# INT64 __stdcall HCLUA_ExcuteCall(int winIndex, char* funcName, int argCount, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, BOOL mainThread);
def HDLUA_执行CALL(窗口序号: int, 函数名: str, 参数数量: int = 0, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, l5: int = 0, l6: int = 0, 是否主线程: bool = False) -> str:
    """
    调用已注册的LUA函数
    
    Args:
        窗口序号: 绑定的窗口索引
        函数名: 已注册的LUA函数名（大小写敏感）
        参数数量: 实际传递的参数个数（0-8）
        rcx: 第1个参数
        rdx: 第2个参数
        r8: 第3个参数
        r9: 第4个参数
        l5: 第5个参数
        l6: 第6个参数
        是否主线程: True=在主线程上下文执行
    
    Returns:
        str: JSON字符串，格式：{"error": 错误码, "ret": 执行结果, "data": 扩展数据}
    """
    hd = Config.get_hd()
    
    HCLUA_ExcuteCall = hd.HCLUA_ExcuteCall
    HCLUA_ExcuteCall.restype = ctypes.c_char_p
    HCLUA_ExcuteCall.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]
    
    ret = HCLUA_ExcuteCall(
        ctypes.c_int32(窗口序号),
        auto_encode(函数名),
        ctypes.c_int32(参数数量),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        ctypes.c_bool(是否主线程)
    )
    return ret.decode('utf-8') if ret else ""
