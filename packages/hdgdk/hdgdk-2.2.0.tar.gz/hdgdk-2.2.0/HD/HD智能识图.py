from .config import Config, ctypes
from .config import auto_encode

import ctypes

# INT64 __stdcall HCFI_FindImageA(int windowsIndex, char* imageNameSet, double sim, BOOL isGrayImage, BOOL openViewer);
def HD智能识图_找图A(窗口序号: int, 图片名字集合: str, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    """
    识图（返回的是圆型的圆点）（ASCII）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        图片名字集合: 如：hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1，默认0.8
        是否灰度图: 是否灰度图，默认False
        是否打开查看器: 是否打开查看器，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCFI_FindImageA = hd.HCFI_FindImageA
    HCFI_FindImageA.restype = ctypes.c_int64
    HCFI_FindImageA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCFI_FindImageA(
        ctypes.c_int32(窗口序号),
        auto_encode(图片名字集合),
        ctypes.c_double(相似度),
        ctypes.c_bool(是否灰度图),
        ctypes.c_bool(是否打开查看器)
    )
    return ret

# INT64 __stdcall HCFI_FindImageW(int 窗口序号, wchar_t*图片名字集合, double sim, BOOL 是否灰度图, BOOL 是否打开查看器);
def HD智能识图_找图W(窗口序号: int, 图片名字集合: str, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    """
    识图(返回的是圆型的圆点)(unicode)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1 (默认0.8)
        是否灰度图: 是否灰度图，默认开启 (默认False)
        是否打开查看器: 是否打开查看器 (默认False)
        
    Returns:
        返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFI_FindImageW = hd.HCFI_FindImageW
    HCFI_FindImageW.restype = ctypes.c_int64
    HCFI_FindImageW.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    image_bytes = auto_encode(图片名字集合)

    ret = HCFI_FindImageW(
        ctypes.c_int32(窗口序号),
        image_bytes,
        ctypes.c_double(相似度),
        ctypes.c_bool(是否灰度图),
        ctypes.c_bool(是否打开查看器)
    )

    return ret

# INT64 __stdcall HCFI_FindImageExA(int 窗口序号, char*图片名字集合, double sim = 0.8, BOOL 是否灰度图 = FALSE, BOOL 是否打开查看器 = FALSE);
def HD智能识图_找图ExA(窗口序号: int, 图片名字集合: str, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageExA(INT32 窗口序号, LPCSTR 图片名字集合, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    识图(返回的是矩形左上角和右下角)(扩展版本)(ascii)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片名字集合: 如:hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        是否灰度图: 是否灰度图  一般开启就行
        是否打开查看器: 是否打开
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
             返回数据格式：
             {
               "error":0,
               "ret":AAA,
               "data":[{"x1":XX,"y1":YY,"x2":XX,"y2":YY}],
               "time":ZZZ
             }
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageExA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(图片名字集合), 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_找图ExW(窗口序号: int, 图片名字集合: str, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageExW(INT32 窗口序号, LPCWSTR 图片名字集合, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    识图(返回的是矩形左上角和右下角)(扩展版本)(unicode)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        是否灰度图: 是否灰度图，默认开启
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageExW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, 图片名字集合, 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_范围找图ExA(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字集合: str, 信息类型: int = 0, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageA(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCSTR 图片名字集合, INT32 信息类型, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    范围内识图 (ascii)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        信息类型: 0表示返回圆点，1表示返回矩形左上角和右下角
        相似度: 相似度0-1
        是否灰度图: 是否灰度图，默认开启
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, auto_encode(图片名字集合), 信息类型, 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_范围找图ExW(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字集合: str, 信息类型: int = 0, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageW(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCWSTR 图片名字集合, INT32 信息类型, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    范围内识图 (unicode)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始X坐标
        y: 起始Y坐标
        w: 宽度
        h: 高度
        图片名字集合: 图片名字集合 (例如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp)
        信息类型: 0表示返回圆点, 1表示返回矩形左上角和右下角
        相似度: 相似度 (0-1)
        是否灰度图: 是否灰度图 (默认False)
        是否打开查看器: 是否打开查看器 (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_int32, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, 图片名字集合, 信息类型, 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_Tem范围找图A(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageTemA(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    Tem范围识图(ascii)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageTemA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)

def HD智能识图_Tem范围找图W(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageTemW(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCWSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    Tem范围识图(unicode)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageTemW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, 图片名字集合, 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)


def HD智能识图_Tem找图A(窗口序号: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageTemA(INT32 窗口序号, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    Tem识图 (ascii)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片名字集合: 图片名字集合 (例如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp)
        相似度: 相似度 (0-1)
        算法类型: 算法类型 (0-5, 默认5)
        是否灰度图: 是否灰度图 (默认False)
        是否全部: 是否全部 (默认False)
        是否打开查看器: 是否打开查看器 (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageTemA
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)

def HD智能识图_Tem找图W(窗口序号: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageTemW(INT32 窗口序号, LPCWSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    Tem识图 (unicode)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片名字集合: 图片名字集合 (例如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp)
        相似度: 相似度 (0-1)
        算法类型: 算法类型 (0-5, 默认5)
        是否灰度图: 是否灰度图 (默认False)
        是否全部: 是否全部 (默认False)
        是否打开查看器: 是否打开查看器 (默认False)
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageTemW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_wchar_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, 图片名字集合, 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)


def HD智能识图_找图从文件(窗口序号: int, 原图名字: str, 图片名字集合: str, 相似度: float = 0.9, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageByFile(INT32 窗口序号, LPCSTR 原图名字, LPCSTR 图片名字集合, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    从文件中加载截图数据并识图(返回的是矩形左上角和右下角)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        原图名字: 指定一张原图文件名(支持绝对路径和相对路径)
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        是否灰度图: 是否灰度图，默认开启
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageByFile
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(原图名字), auto_encode(图片名字集合), 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_Tem找图从文件(窗口序号: int, 原图名字: str, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageTemByFile(INT32 窗口序号, LPCSTR 原图名字, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    从文件中加载截图数据并识图(返回的是矩形左上角和右下角)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        原图名字: 指定一张原图文件名(支持绝对路径和相对路径)
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageTemByFile
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(原图名字), auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)

def HD智能识图_Tem范围找图从文件(窗口序号: int, x: int, y: int, w: int, h: int, 原图名字: str, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageTemByFile(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCSTR 原图名字, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    范围识图(原图从文件)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        原图名字: 指定一张原图文件名(支持绝对路径和相对路径)
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageTemByFile
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, auto_encode(原图名字), auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)

def HD智能识图_找图从内存(窗口序号: int, 图片字节数据: bytes, 图片字节大小: int, 图片名字集合: str, 相似度: float = 0.8, 是否灰度图: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageByMem(INT32 窗口序号, LPVOID 图片字节数据, INT32 图片字节大小, LPCSTR 图片名字集合, double 相似度, BOOL 是否灰度图, BOOL 是否打开查看器);
    """
    从内存中加载截图数据并识图(返回的是矩形左上角和右下角)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片字节数据: Bmp图片字节数据缓冲区地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        图片字节大小: Bmp图片字节大小
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        是否灰度图: 是否灰度图，默认开启
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageByMem
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    
    # 创建字节数组
    buffer = (ctypes.c_ubyte * len(图片字节数据))(*图片字节数据)
    
    return func(窗口序号, buffer, 图片字节大小, auto_encode(图片名字集合), 相似度, 是否灰度图, 是否打开查看器)

def HD智能识图_Tem找图从内存(窗口序号: int, 图片字节数据: bytes, 图片字节大小: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageTemByMem(INT32 窗口序号, LPVOID 图片字节数据, INT32 图片字节大小, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    范围识图(原图从内存)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        图片字节数据: Bmp图片字节数据缓冲区地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        图片字节大小: Bmp图片字节大小
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageTemByMem
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    # 创建字节数组
    buffer = (ctypes.c_ubyte * len(图片字节数据))(*图片字节数据)
    
    return func(窗口序号, buffer, 图片字节大小, auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)

def HD智能识图_Tem范围找图从内存(窗口序号: int, x: int, y: int, w: int, h: int, 图片字节数据: bytes, 图片字节大小: int, 图片名字集合: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageTemByMem(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPVOID 图片字节数据, INT32 图片字节大小, LPCSTR 图片名字集合, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    范围识图(原图从内存)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        图片字节数据: Bmp图片字节数据缓冲区地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        图片字节大小: Bmp图片字节大小
        图片名字集合: 如: hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageTemByMem
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    # 创建字节数组
    buffer = (ctypes.c_ubyte * len(图片字节数据))(*图片字节数据)
    
    return func(窗口序号, x, y, w, h, buffer, 图片字节大小, auto_encode(图片名字集合), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)


def HD智能识图_Tem找图来源内存(窗口序号: int, 子图内存地址集合字符串: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindImageTemFromMem(INT32 窗口序号, LPCSTR 子图内存地址集合字符串, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    识图(子图从内存)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        子图内存地址集合字符串: "地址1,长度1|地址2,长度2|地址3,长度3"
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindImageTemFromMem
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, auto_encode(子图内存地址集合字符串), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)


def HD智能识图_Tem范围找图来源内存(窗口序号: int, x: int, y: int, w: int, h: int, 子图内存地址集合字符串: str, 相似度: float = 0.9, 算法类型: int = 5, 是否灰度图: bool = False, 是否全部: bool = False, 是否打开查看器: bool = False) -> int:
    # INT64 __stdcall HCFI_FindRangeImageTemFromMem(INT32 窗口序号, INT32 x, INT32 y, INT32 w, INT32 h, LPCSTR 子图内存地址集合字符串, double 相似度, INT32 算法类型, BOOL 是否灰度图, BOOL 是否全部, BOOL 是否打开查看器);
    """
    范围识图(子图从内存)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: 起始坐标X
        y: 起始坐标Y
        w: 区域宽度
        h: 区域高度
        子图内存地址集合字符串: "地址1,长度1|地址2,长度2|地址3,长度3"
        相似度: 相似度0-1
        算法类型: 0 1 2 3 4 5 一共6种算法，默认使用5
        是否灰度图: 是否灰度图，默认开启
        是否全部: 是否找出全部结果，默认False
        是否打开查看器: 是否打开查看器
        
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCFI_FindRangeImageTemFromMem
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    
    return func(窗口序号, x, y, w, h, auto_encode(子图内存地址集合字符串), 相似度, 算法类型, 是否灰度图, 是否全部, 是否打开查看器)












































