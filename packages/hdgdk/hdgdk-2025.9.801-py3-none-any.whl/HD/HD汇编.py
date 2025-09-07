from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCSH_GetShellCode(int 模式, char* 汇编文本, BYTE* 机器码缓冲区, int 机器码缓冲区大小, INT64* 返回机器码字节大小的地址, INT64* 错误1变量的地址, INT64* 错误2变量的地址);
def HD汇编_转机器码(模式: int, 汇编文本: str, 机器码缓冲区=None, 机器码缓冲区大小: int = 1024, 错误1=None, 错误2=None) -> tuple:
    """
    汇编文本转换机器码
    
    Args:
        模式: 32位(4)/64位(8)
        汇编文本: 汇编代码文本
        机器码缓冲区: 预分配缓冲区，默认自动创建
        机器码缓冲区大小: 缓冲区容量，单位字节
        错误1: 返回错误行号变量地址，需ctypes.c_int()
        错误2: 返回错误描述变量地址，需ctypes.c_char_p()
    
    Returns:
        tuple: (结果代码, 实际机器码, 实际字节数, 错误行号, 错误描述)
    """
    hd = Config.get_hd()
    
    HCSH_GetShellCode = hd.HCSH_GetShellCode
    HCSH_GetShellCode.restype = ctypes.c_int64
    HCSH_GetShellCode.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_char_p)
    ]
    
    # 准备输出参数
    actual_size = ctypes.c_int32(0)
    error_line = ctypes.c_int32(0)
    error_desc = ctypes.c_char_p()
    
    # 自动创建缓冲区
    if not 机器码缓冲区:
        机器码缓冲区 = (ctypes.c_ubyte * 机器码缓冲区大小)()
    
    # 调用函数
    ret = HCSH_GetShellCode(
        ctypes.c_int32(模式),
        auto_encode(汇编文本),
        机器码缓冲区,
        ctypes.c_int32(机器码缓冲区大小),
        ctypes.byref(actual_size),
        ctypes.byref(error_line) if 错误1 is None else 错误1,
        ctypes.byref(error_desc) if 错误2 is None else 错误2
    )
    
    # 提取结果
    result_bytes = bytes(机器码缓冲区)[:actual_size.value] if ret == 0 else b''
    return (
        ret,
        result_bytes,
        actual_size.value,
        error_line.value,
        error_desc.value.decode('utf-8', errors='ignore') if error_desc.value else ""
    )

# INT64 __stdcall HCSH_WriteShellCode(int pid, BYTE* 机器码缓冲区, int 机器码缓冲区大小, INT64* 返回变量的地址);
def HD汇编_写入机器码(目标进程PID: int, 机器码缓冲区: bytes, 返回地址变量=None) -> tuple:
    """
    将机器码写入目标进程内存
    
    Args:
        目标进程PID: 目标进程ID
        机器码缓冲区: 机器码bytes对象 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        返回地址变量: 接收地址的ctypes变量，默认自动创建
    
    Returns:
        tuple: (结果代码, 写入的地址)
    """
    hd = Config.get_hd()
    
    HCSH_WriteShellCode = hd.HCSH_WriteShellCode
    HCSH_WriteShellCode.restype = ctypes.c_int64
    HCSH_WriteShellCode.argtypes = [
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_uint64)
    ]
    
    # 自动创建接收变量
    allocated_addr = ctypes.c_uint64(0) if 返回地址变量 is None else 返回地址变量
    
    # 转换缓冲区
    buffer_type = ctypes.c_ubyte * len(机器码缓冲区)
    buffer_ptr = buffer_type.from_buffer_copy(机器码缓冲区)
    
    ret = HCSH_WriteShellCode(
        ctypes.c_int32(目标进程PID),
        buffer_ptr,
        ctypes.c_int32(len(机器码缓冲区)),
        ctypes.byref(allocated_addr) if 返回地址变量 is None else 返回地址变量
    )
    
    return ret, allocated_addr.value if ret == 0 else 0
