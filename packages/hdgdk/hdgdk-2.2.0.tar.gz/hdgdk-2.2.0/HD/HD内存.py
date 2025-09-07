from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCM_FindCode(int windowsIndex, char* pattern, int offset, int times, int type, char* moduleName);
def HD内存_特征码(窗口序号: int, 特征码字符串: str, 偏移: int, 次数: int, 地址类型: int = 1, 模块名字: str = None) -> int:
    """
    特征码查找
    
    Args:
        窗口序号: 窗口序号（从1开始）
        特征码字符串: 特征码字符串（支持??）
        偏移: 正负偏移量
        次数: 查找次数（从1开始）
        地址类型: 地址类型（1=地址，2=基地址，3=CALL地址，4=地址中的值），默认1
        模块名字: 指定搜索的模块名（默认主模块）
    
    Returns:
        int: 查找到的内存地址/值
    """
    hd = Config.get_hd()
    
    HCM_FindCode = hd.HCM_FindCode
    HCM_FindCode.restype = ctypes.c_int64
    HCM_FindCode.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    
    ret = HCM_FindCode(
        ctypes.c_int(窗口序号),
        auto_encode(特征码字符串),
        ctypes.c_int(偏移),
        ctypes.c_int(次数),
        ctypes.c_int(地址类型),
        auto_encode(模块名字) if 模块名字 else None
    )
    return ret

# INT64 __stdcall HCM_FindCodeEx(int windowsIndex, INT64 startAddr, INT64 scanSize, char* pattern, int offset, int times, int type);
def HD内存_特征码Ex(窗口序号: int, 开始地址: int, 扫描范围大小: int, 特征码字符串: str, 偏移: int, 次数: int, 地址类型: int = 1) -> int:
    """
    特征码查找（扩展版本）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        开始地址: 扫描起始地址
        扫描范围大小: 扫描内存范围大小
        特征码字符串: 特征码字符串（支持??）
        偏移: 正负偏移量
        次数: 查找次数（从1开始）
        地址类型: 地址类型（1=地址，2=基地址，3=CALL地址，4=地址中的值），默认1
    
    Returns:
        int: 查找到的内存地址/值
    """
    hd = Config.get_hd()
    
    HCM_FindCodeEx = hd.HCM_FindCodeEx
    HCM_FindCodeEx.restype = ctypes.c_int64
    HCM_FindCodeEx.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    ret = HCM_FindCodeEx(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(开始地址),
        ctypes.c_int64(扫描范围大小),
        auto_encode(特征码字符串),
        ctypes.c_int(偏移),
        ctypes.c_int(次数),
        ctypes.c_int(地址类型)
    )
    return ret

# INT64 __stdcall HCM_Read(int windowsIndex, char* expression, int readSize, char* moduleName, BOOL isMainThread);
def HD内存_读表达式(窗口序号: int, 表达式字符串: str, 读取大小: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    读整数型数据
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式（例如"0x123456]+0x56]-0x44]"）
        读取大小: 读取字节数（1/2/4/8）
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用，默认False
    
    Returns:
        int: 读取的数值
    """
    hd = Config.get_hd()
    
    HCM_Read = hd.HCM_Read
    HCM_Read.restype = ctypes.c_int64
    HCM_Read.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_Read(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        ctypes.c_int(读取大小),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ReadAddr(int windowsIndex, INT64 addr, int readSize, BOOL isMainThread);
def HD内存_读地址(窗口序号: int, 内存地址: int, 读取大小: int, 是否主线程调用: bool = False) -> int:
    """
    直接读取内存地址数据
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        读取大小: 读取字节数（1/2/4/8）
        是否主线程调用: 是否强制主线程调用，默认False
    
    Returns:
        int: 读取的数值
    """
    hd = Config.get_hd()
    
    HCM_ReadAddr = hd.HCM_ReadAddr
    HCM_ReadAddr.restype = ctypes.c_int64
    HCM_ReadAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int, ctypes.c_bool]
    
    ret = HCM_ReadAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_int(读取大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_Write(int windowsIndex, char* expression, INT64 value, int writeSize, char* moduleName, BOOL isMainThread);
def HD内存_写表达式(窗口序号: int, 表达式字符串: str, 数值: int, 写入大小: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    写入整数数据到表达式地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        数值: 要写入的数值
        写入大小: 写入字节数（1~8）
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_Write = hd.HCM_Write
    HCM_Write.restype = ctypes.c_int64
    HCM_Write.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_Write(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        ctypes.c_int64(数值),
        ctypes.c_int(写入大小),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteAddr(int windowsIndex, INT64 addr, INT64 value, int writeSize, BOOL isMainThread);
def HD内存_写地址(窗口序号: int, 内存地址: int, 数值: int, 写入大小: int, 是否主线程调用: bool = False) -> int:
    """
    直接写入数据到内存地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        数值: 要写入的数值
        写入大小: 写入字节数（1~8）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_WriteAddr = hd.HCM_WriteAddr
    HCM_WriteAddr.restype = ctypes.c_int64
    HCM_WriteAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int, ctypes.c_bool]
    
    ret = HCM_WriteAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_int64(数值),
        ctypes.c_int(写入大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ReadData(int windowsIndex, char* expression, BYTE* byteBuffer, int bufferSize, int readSize, char* moduleName, BOOL isMainThread);
def HD内存_读表达式字节流(窗口序号: int, 表达式字符串: str, 字节缓冲区, 缓冲区大小: int, 读取大小: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    读取表达式地址的字节流数据
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        字节缓冲区: 由外部创建的ctypes缓冲区
        缓冲区大小: 缓冲区大小
        读取大小: 要读取的字节数
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 实际读取的字节数
    """
    hd = Config.get_hd()
    
    HCM_ReadData = hd.HCM_ReadData
    HCM_ReadData.restype = ctypes.c_int64
    HCM_ReadData.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_ReadData(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        字节缓冲区,
        ctypes.c_int(缓冲区大小),
        ctypes.c_int(读取大小),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ReadFloat(int windowsIndex, char* expression, int readSize, char* moduleName, BOOL isMainThread);
def HD内存_读表达式浮点数(窗口序号: int, 表达式字符串: str, 读取大小: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    读取表达式地址的浮点数
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        读取大小: 浮点数大小（4=单精度，8=双精度）
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 浮点数的整数形式
    """
    hd = Config.get_hd()
    
    HCM_ReadFloat = hd.HCM_ReadFloat
    HCM_ReadFloat.restype = ctypes.c_int64
    HCM_ReadFloat.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_ReadFloat(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        ctypes.c_int(读取大小),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ReadDataAddr(int windowsIndex, INT64 addr, int bufferSize, int readSize, BOOL isMainThread);
def HD内存_读地址字节流(窗口序号: int, 内存地址: int, 缓冲区大小: int, 读取大小: int, 是否主线程调用: bool = False) -> int:
    """
    读取内存地址的字节流数据
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        缓冲区大小: 缓冲区大小
        读取大小: 要读取的字节数
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 实际读取的字节数
    """
    hd = Config.get_hd()
    
    HCM_ReadDataAddr = hd.HCM_ReadDataAddr
    HCM_ReadDataAddr.restype = ctypes.c_int64
    HCM_ReadDataAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
    
    ret = HCM_ReadDataAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_int(缓冲区大小),
        ctypes.c_int(读取大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ReadFloatAddr(int windowsIndex, INT64 addr, int readSize, BOOL isMainThread);
def HD内存_读地址浮点数(窗口序号: int, 内存地址: int, 读取大小: int, 是否主线程调用: bool = False) -> int:
    """
    读取内存地址的浮点数
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        读取大小: 浮点数大小（4=单精度，8=双精度）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 浮点数的整数形式
    """
    hd = Config.get_hd()
    
    HCM_ReadFloatAddr = hd.HCM_ReadFloatAddr
    HCM_ReadFloatAddr.restype = ctypes.c_int64
    HCM_ReadFloatAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int, ctypes.c_bool]
    
    ret = HCM_ReadFloatAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_int(读取大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteData(int windowsIndex, char* expression, BYTE* byteBuffer, int writeSize, char* moduleName, BOOL isMainThread);
def HD内存_写表达式字节流(窗口序号: int, 表达式字符串: str, 字节数据: bytes, 写入大小: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    写入字节流数据到表达式地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        字节数据: 要写入的字节数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        写入大小: 写入字节数
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 实际写入的字节数
    """
    hd = Config.get_hd()
    
    HCM_WriteData = hd.HCM_WriteData
    HCM_WriteData.restype = ctypes.c_int64
    HCM_WriteData.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    buffer_type = ctypes.c_ubyte * len(字节数据)
    buffer_data = buffer_type(*字节数据)
    
    ret = HCM_WriteData(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        buffer_data,
        ctypes.c_int(写入大小),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteFloat(int windowsIndex, char* expression, float value, char* moduleName, BOOL isMainThread);
def HD内存_写表达式单浮点(窗口序号: int, 表达式字符串: str, 浮点值: float, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    写入单精度浮点数到表达式地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        浮点值: 要写入的单精度浮点数
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_WriteFloat = hd.HCM_WriteFloat
    HCM_WriteFloat.restype = ctypes.c_int64
    HCM_WriteFloat.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_float, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_WriteFloat(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        ctypes.c_float(浮点值),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteDouble(int windowsIndex, char* expression, double value, char* moduleName, BOOL isMainThread);
def HD内存_写表达式双浮点(窗口序号: int, 表达式字符串: str, 双浮点值: float, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    写入双精度浮点数到表达式地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        表达式字符串: 偏移表达式
        双浮点值: 要写入的双精度浮点数
        模块名字: 指定模块（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_WriteDouble = hd.HCM_WriteDouble
    HCM_WriteDouble.restype = ctypes.c_int64
    HCM_WriteDouble.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_WriteDouble(
        ctypes.c_int(窗口序号),
        auto_encode(表达式字符串),
        ctypes.c_double(双浮点值),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteDataAddr(int windowsIndex, INT64 addr, BYTE* byteBuffer, int writeSize, BOOL isMainThread);
def HD内存_写地址字节流(窗口序号: int, 内存地址: int, 字节数据: bytes, 写入大小: int, 是否主线程调用: bool = False) -> int:
    """
    写入字节流数据到内存地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        字节数据: 要写入的字节数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        写入大小: 写入字节数
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 实际写入的字节数
    """
    hd = Config.get_hd()
    
    HCM_WriteDataAddr = hd.HCM_WriteDataAddr
    HCM_WriteDataAddr.restype = ctypes.c_int64
    HCM_WriteDataAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_bool]
    
    buffer_type = ctypes.c_ubyte * len(字节数据)
    buffer_data = buffer_type(*字节数据)
    
    ret = HCM_WriteDataAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        buffer_data,
        ctypes.c_int(写入大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteFloatAddr(int windowsIndex, INT64 addr, float value, BOOL isMainThread);
def HD内存_写地址单浮点(窗口序号: int, 内存地址: int, 浮点值: float, 是否主线程调用: bool = False) -> int:
    """
    写入单精度浮点数到内存地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        浮点值: 要写入的单精度浮点数
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_WriteFloatAddr = hd.HCM_WriteFloatAddr
    HCM_WriteFloatAddr.restype = ctypes.c_int64
    HCM_WriteFloatAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_float, ctypes.c_bool]
    
    ret = HCM_WriteFloatAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_float(浮点值),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_WriteDoubleAddr(int windowsIndex, INT64 addr, double value, BOOL isMainThread);
def HD内存_写地址双浮点(窗口序号: int, 内存地址: int, 双浮点值: float, 是否主线程调用: bool = False) -> int:
    """
    写入双精度浮点数到内存地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 目标内存地址
        双浮点值: 要写入的双精度浮点数
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 操作结果代码
    """
    hd = Config.get_hd()
    
    HCM_WriteDoubleAddr = hd.HCM_WriteDoubleAddr
    HCM_WriteDoubleAddr.restype = ctypes.c_int64
    HCM_WriteDoubleAddr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_double, ctypes.c_bool]
    
    ret = HCM_WriteDoubleAddr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_double(双浮点值),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_GetModuleAddress(int windowsIndex, char* moduleName, BOOL isMainThread);
def HD内存_获取模块地址(窗口序号: int, 模块名字: str = None, 是否主线程调用: bool = False) -> int:
    """
    获取模块基地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        模块名字: 模块名字（默认主模块）
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 模块基地址
    """
    hd = Config.get_hd()
    
    HCM_GetModuleAddress = hd.HCM_GetModuleAddress
    HCM_GetModuleAddress.restype = ctypes.c_int64
    HCM_GetModuleAddress.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_GetModuleAddress(
        ctypes.c_int(窗口序号),
        auto_encode(模块名字) if 模块名字 else None,
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_GetProcAddress(int windowsIndex, char* moduleName, char* procName, BOOL isMainThread);
def HD内存_获取模块接口地址(窗口序号: int, 模块名字: str, 接口名字: str, 是否主线程调用: bool = False) -> int:
    """
    获取模块导出函数地址
    
    Args:
        窗口序号: 窗口序号（从1开始）
        模块名字: 模块名字
        接口名字: 导出函数名字
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 函数地址
    """
    hd = Config.get_hd()
    
    HCM_GetProcAddress = hd.HCM_GetProcAddress
    HCM_GetProcAddress.restype = ctypes.c_int64
    HCM_GetProcAddress.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCM_GetProcAddress(
        ctypes.c_int(窗口序号),
        auto_encode(模块名字),
        auto_encode(接口名字),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_IsValidPtr(int windowsIndex, INT64 addr, int size, BOOL isMainThread);
def HD内存_地址是否可读(窗口序号: int, 内存地址: int, 地址大小: int = 8, 是否主线程调用: bool = False) -> int:
    """
    检查内存地址是否可读
    
    Args:
        窗口序号: 窗口序号（从1开始）
        内存地址: 要检查的内存地址
        地址大小: 地址大小，默认8
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 是否可读（1=可读，0=不可读）
    """
    hd = Config.get_hd()
    
    HCM_IsValidPtr = hd.HCM_IsValidPtr
    HCM_IsValidPtr.restype = ctypes.c_int64
    HCM_IsValidPtr.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int, ctypes.c_bool]
    
    ret = HCM_IsValidPtr(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(内存地址),
        ctypes.c_int(地址大小),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

def HD内存_浮点取整数形式值(浮点值: float) -> int:
    """
    将浮点数转换为整数形式（用于内存操作）
    
    Args:
        浮点值: 要转换的浮点数
    
    Returns:
        int: 整数形式的值
    """
    import struct
    return struct.unpack('I', struct.pack('f', 浮点值))[0]

# INT64 __stdcall HCM_ExecAssemblyX86(int windowsIndex, INT64 targetAddr, char* assembly, BOOL releaseAddr, BOOL isMainThread);
def HD内存_执行汇编X86(窗口序号: int, 目标进程地址: int = 0, 汇编文本: str = None, 是否释放地址: bool = False, 是否主线程调用: bool = False) -> int:
    """
    执行X86汇编代码
    
    Args:
        窗口序号: 窗口序号（从1开始）
        目标进程地址: 目标进程地址，0表示自动分配
        汇编文本: 汇编代码文本
        是否释放地址: 执行完是否释放地址
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 执行结果或分配的地址
    """
    hd = Config.get_hd()
    
    HCM_ExecAssemblyX86 = hd.HCM_ExecAssemblyX86
    HCM_ExecAssemblyX86.restype = ctypes.c_int64
    HCM_ExecAssemblyX86.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCM_ExecAssemblyX86(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(目标进程地址),
        auto_encode(汇编文本) if 汇编文本 else None,
        ctypes.c_bool(是否释放地址),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCM_ExecAssemblyX64(int windowsIndex, INT64 targetAddr, char* assembly, BOOL releaseAddr, BOOL isMainThread);
def HD内存_执行汇编X64(窗口序号: int, 目标进程地址: int = 0, 汇编文本: str = None, 是否释放地址: bool = False, 是否主线程调用: bool = False) -> int:
    """
    执行X64汇编代码
    
    Args:
        窗口序号: 窗口序号（从1开始）
        目标进程地址: 目标进程地址，0表示自动分配
        汇编文本: 汇编代码文本
        是否释放地址: 执行完是否释放地址
        是否主线程调用: 是否强制主线程调用
    
    Returns:
        int: 执行结果或分配的地址
    """
    hd = Config.get_hd()
    
    HCM_ExecAssemblyX64 = hd.HCM_ExecAssemblyX64
    HCM_ExecAssemblyX64.restype = ctypes.c_int64
    HCM_ExecAssemblyX64.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCM_ExecAssemblyX64(
        ctypes.c_int(窗口序号),
        ctypes.c_int64(目标进程地址),
        auto_encode(汇编文本) if 汇编文本 else None,
        ctypes.c_bool(是否释放地址),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

def HD内存_浮点整数转浮点数(整数值: int) -> float:
    """
    将整数形式的浮点数转换为浮点数
    
    Args:
        整数值: 整数形式的浮点数值
    
    Returns:
        float: 转换后的浮点数
    """
    import struct
    return struct.unpack('f', struct.pack('I', 整数值))[0]

def HD内存_双浮点长整数转双浮点数(长整数值: int) -> float:
    """
    将长整数形式的双精度浮点数转换为双精度浮点数
    
    Args:
        长整数值: 长整数形式的双精度浮点数值
    
    Returns:
        float: 转换后的双精度浮点数
    """
    import struct
    return struct.unpack('d', struct.pack('Q', 长整数值))[0]
