from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCFS_SetDictFile(int windowsIndex, int dictIndex, char* file);
def HD识字_设置字库(窗口序号: int, 字库序号: int, 字库文件: str) -> int:
    """
    设置当前像素识字的字库文件（为了提高识别效率，不支持多线程）
    
    Args:
        窗口序号: 窗口序号
        字库序号: 字库序号，自定义整数类型，枚举类型，宏定义，不要小于0
        字库文件: 字库文件名字（可以加路径），最后寻找路径：全局路径（HCRES_SetResPath设置路径）+ file
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCFS_SetDictFile = hd.HCFS_SetDictFile
    HCFS_SetDictFile.restype = ctypes.c_int64
    HCFS_SetDictFile.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
    
    ret = HCFS_SetDictFile(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(字库序号),
        auto_encode(字库文件)
    )
    return ret

# INT64 __stdcall HCFS_SetDictFileEx(int windowsIndex, int dictIndex, char* file);
def HD识字_设置字库Ex(窗口序号: int, 字库序号: int, 字库文件: str) -> int:
    """
    设置当前像素识字的字库文件（为了提高识别效率，不支持多线程）（扩展版本）
    
    Args:
        窗口序号: 窗口序号
        字库序号: 字库序号，自定义整数类型，枚举类型，宏定义，不要小于0
        字库文件: 字库文件名字（可以加路径），最后寻找路径：全局路径（HCRES_SetResPath设置路径）+ file
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCFS_SetDictFileEx = hd.HCFS_SetDictFileEx
    HCFS_SetDictFileEx.restype = ctypes.c_int64
    HCFS_SetDictFileEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]
    
    ret = HCFS_SetDictFileEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(字库序号),
        auto_encode(字库文件)
    )
    return ret

# INT64 __stdcall HCFS_SetDictFileExx(int windowsIndex, int dictIndex, char* file, char* password);
def HD识字_设置字库Exx(窗口序号: int, 字库序号: int, 字库文件: str, 密码: str = None) -> int:
    """
    设置当前像素识字的字库文件（为了提高识别效率，不支持多线程）
    建议在登录回调中最开始初始化调用
    其他线程需要那个序号就切换那个序号HCFS_SwitchCurDictFile
    调用一次会给所有窗口序号添加当前设置的字库文件
    
    Args:
        窗口序号: 窗口序号
        字库序号: 字库序号，自定义整数类型，枚举类型，宏定义，不要小于0
        字库文件: 字库文件名字（可以加路径）
        密码: 密码，使用综合工具进行加密，默认None
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCFS_SetDictFileExx = hd.HCFS_SetDictFileExx
    HCFS_SetDictFileExx.restype = ctypes.c_int64
    HCFS_SetDictFileExx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p]
    
    ret = HCFS_SetDictFileExx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(字库序号),
        auto_encode(字库文件),
        auto_encode(密码) if 密码 else None
    )
    return ret

# INT64 __stdcall HCFS_SwitchCurDictFile(int windowsIndex, int dictIndex);
def HD识字_切换字库序号(窗口序号: int, 字库序号: int) -> int:
    """
    设置当前像素识字的字库文件（为了提高识别效率，不支持多线程）请在主执行线程中最开始初始化调用
    
    Args:
        窗口序号: 窗口序号
        字库序号: 字库序号，自定义整数类型，枚举类型，宏定义，不要小于0
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCFS_SwitchCurDictFile = hd.HCFS_SwitchCurDictFile
    HCFS_SwitchCurDictFile.restype = ctypes.c_int64
    HCFS_SwitchCurDictFile.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCFS_SwitchCurDictFile(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(字库序号)
    )
    return ret

# __int64 __stdcall HCFS_GetCurDictInfo(__int32 窗口序号);
def HD识字_获取当前字库(窗口序号: int) -> int:
    """
    设置当前像素识字的字库文件(为了提高识别效率,不支持多线程) 请在主执行线程中最开始初始化调用
    :param 窗口序号: 窗口序号
    :return: 返回值代码(查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFS_GetCurDictInfo = hd.HCFS_GetCurDictInfo
    HCFS_GetCurDictInfo.restype = ctypes.c_int64
    HCFS_GetCurDictInfo.argtypes = [ctypes.c_int32]

    ret = HCFS_GetCurDictInfo(
        ctypes.c_int32(窗口序号)
    )
    return ret

# __int64 __stdcall HCFS_GetCurDictIndex(__int32 窗口序号);
def HD识字_获取当前字库序号(窗口序号: int) -> int:
    """
    获取当前线程绑定的字库索引 (支持多线程)
    :param 窗口序号: 窗口序号
    :return: 返回值代码(查看HD返回值表) 或者 返回大于等于0的值是当前线程绑定的字库索引
    """
    hd = Config.get_hd()

    HCFS_GetCurDictIndex = hd.HCFS_GetCurDictIndex
    HCFS_GetCurDictIndex.restype = ctypes.c_int64
    HCFS_GetCurDictIndex.argtypes = [ctypes.c_int32]

    ret = HCFS_GetCurDictIndex(
        ctypes.c_int32(窗口序号)
    )
    return ret


# INT64 __stdcall HCFS_FindStr(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR deltaColor, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_单字符找字(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内找字(只支持单字符串并且是单字符字库)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 字符串用HCEnv_GetRetJson获取
    """
    hd = Config.get_hd()

    HCFS_FindStr = hd.HCFS_FindStr
    HCFS_FindStr.restype = ctypes.c_int64
    HCFS_FindStr.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_long,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)

    ret = HCFS_FindStr(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_long(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64 __stdcall HCFS_FindStrEx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR deltaColor, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_单字符找字Ex(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内找字(支持多个字符串并且是单字符字库)(扩展版本)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 字符串用HCEnv_GetRetJson获取
    """
    hd = Config.get_hd()

    HCFS_FindStrEx = hd.HCFS_FindStrEx
    HCFS_FindStrEx.restype = ctypes.c_int64
    HCFS_FindStrEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_long,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)

    # 调用C函数
    ret = HCFS_FindStrEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_long(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64 __stdcall HCFS_FindStrExx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR deltaColor, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_单字符找字Exx(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内找字(支持多个字符串并且是单字符字库)(扩展版本)找到一个就返回
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 大于0表示:高4字节为x 低4字节为y 同时字符串信息存在json中
    """
    hd = Config.get_hd()

    HCFS_FindStrExx = hd.HCFS_FindStrExx
    HCFS_FindStrExx.restype = ctypes.c_int64
    HCFS_FindStrExx.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_long,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)

    # 调用C函数
    ret = HCFS_FindStrExx(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_long(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64  __stdcall HCFS_FindStrMutilVPoints(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_列表单列找字(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    单字符串找 字库是字符串 例如:洛阳 多行 返回多个坐标 一行只找一列(一次)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 大于0表示:找到的数量
    """
    hd = Config.get_hd()

    HCFS_FindStrMutilVPoints = hd.HCFS_FindStrMutilVPoints
    HCFS_FindStrMutilVPoints.restype = ctypes.c_int64
    HCFS_FindStrMutilVPoints.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_long,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)

    # 调用C函数
    ret = HCFS_FindStrMutilVPoints(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_long(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64  __stdcall HCFS_FindStrMutilVPointsByFile(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, LPCSTR iamgeName, int bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_列表单列找字从文件(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片名字: str, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    单字符串找 (原图从文件) 字库是字符串 例如:洛阳 多行 返回多个坐标 一行只找一列(一次)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        图片名字: bmp图片名字,支持加路径,不加路径则在全局路径找,图片后缀不要省略(支持绝对路径和相对路径)
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 大于0表示:找到的数量
    """
    hd = Config.get_hd()

    HCFS_FindStrMutilVPointsByFile = hd.HCFS_FindStrMutilVPointsByFile
    HCFS_FindStrMutilVPointsByFile.restype = ctypes.c_int64
    HCFS_FindStrMutilVPointsByFile.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_char_p,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)
    图片名字_bytes = auto_encode(图片名字)

    # 调用C函数
    ret = HCFS_FindStrMutilVPointsByFile(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_char_p(图片名字_bytes),
        ctypes.c_int32(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64  __stdcall HCFS_FindStrMutilVPointsByMem(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, BYTE* data, int dataSize, int bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_列表单列找字从内存(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片数据: bytes, 图片数据大小: int, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    单字符串找 (原图从内存) 字库是字符串 例如:洛阳 多行 返回多个坐标 一行只找一列(一次)
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
        偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
        相似度: 整个像素矩阵的相似度
        图片数据: bmp图片格式的二进制内存数据首地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        图片数据大小: 图片数据大小
        是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
        排序方向类型: 排序类型 / 方向类型 排序/方向类型
        水平间距: 字体水平间距 默认11像素
        垂直间距: 字体垂直间距 默认11像素
        周围占比: 一个字的周围占比 默认0.1
        是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
        
    Returns:
        返回值代码(查看HD返回值表) 或者 大于0表示:找到的数量
    """
    hd = Config.get_hd()

    HCFS_FindStrMutilVPointsByMem = hd.HCFS_FindStrMutilVPointsByMem
    HCFS_FindStrMutilVPointsByMem.restype = ctypes.c_int64
    HCFS_FindStrMutilVPointsByMem.argtypes = [
        ctypes.c_int32,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_long,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_double,
        ctypes.c_bool
    ]

    字符串_bytes = auto_encode(字符串)
    偏色_bytes = auto_encode(偏色)

    # 将图片数据转换为ctypes数组
    图片数据_array = (ctypes.c_ubyte * 图片数据大小)(*图片数据)

    # 调用C函数
    ret = HCFS_FindStrMutilVPointsByMem(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(字符串_bytes),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        图片数据_array,
        ctypes.c_int32(图片数据大小),
        ctypes.c_int32(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64 __stdcall HCFS_FindStrMutilHVPoints(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE)
def HD识字_列表多列找字(窗口序号: int, x: int, y: int, w: int, h: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    多行多列找字(完整屏幕版)
    :param 窗口序号: 1开始的窗口索引
    :param x: 起始X坐标
    :param y: 起始Y坐标
    :param w: 区域宽度
    :param h: 区域高度
    :param 字符串: 要查找的字符串(支持"|"分割多个)
    :param 偏色: 颜色格式"RRGGBB-RRGGBB|..."
    :param 相似度: 0.0~1.0的相似度阈值
    :param 是否开启反向相似度: True/False
    :param 排序方向类型: 排序方向类型
    :param 水平间距: 文字水平间距(默认11像素)
    :param 垂直间距: 文字垂直间距(默认11像素)
    :param 周围占比: 字符周边占比(默认0.1)
    :param 是否独占11: 是否独占11像素区域
    :return: 结果数量或错误码
    """
    hd = Config.get_hd()
    func = hd.HCFS_FindStrMutilHVPoints
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double,
        ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    str_bytes = auto_encode(字符串)
    color_bytes = auto_encode(偏色)

    return func(
        窗口序号, x, y, w, h,
        str_bytes, color_bytes, 相似度,
        是否开启反向相似度, 排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_FindStrMutilHVPointsByFile(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, LPCSTR iamgeName, int bfx, int dirType= 0, int spaceH = 11, int spaceV = 11, double groundRate = 0.1, BOOL bOne11= TRUE);
def HD识字_列表多列找字从文件(窗口序号: int, x: int, y: int, w: int, h: int, 字符串: str, 偏色: str, 相似度: float, 图片文件名: str, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    从图片文件进行多行多列找字
    
    Args:
        窗口序号: 窗口序号
        x: x坐标
        y: y坐标  
        w: 宽度
        h: 高度
        字符串: 字符串
        偏色: 偏色
        相似度: 相似度
        图片文件名: 图片文件名
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序方向类型
        水平间距: 水平间距
        垂直间距: 垂直间距
        周围占比: 周围占比
        是否独占11: 是否独占11
        
    Returns:
        返回值代码
    """
    hd = Config.get_hd()
    
    func = hd.HCFS_FindStrMutilHVPointsByFile
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double,
        ctypes.c_char_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, w, h,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        auto_encode(图片文件名), 是否开启反向相似度,
        排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_FindStrMutilHVPointsByMem(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, BYTE* data, int dataSize, int bfx, int dirType= 0, int spaceH = 11, int spaceV = 11, double groundRate = 0.1, BOOL bOne11= TRUE);
def HD识字_列表多列找字从内存(窗口序号: int, x: int, y: int, w: int, h: int, 字符串: str, 偏色: str, 相似度: float, 图片数据: bytes, 数据大小: int, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    从内存图像数据找字
    
    Args:
        窗口序号: 窗口序号
        x: x坐标
        y: y坐标
        w: 宽度
        h: 高度
        字符串: 字符串
        偏色: 偏色
        相似度: 相似度
        图片数据: 图片数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        数据大小: 数据大小
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序方向类型
        水平间距: 水平间距
        垂直间距: 垂直间距
        周围占比: 周围占比
        是否独占11: 是否独占11
        
    Returns:
        返回值代码
    """
    hd = Config.get_hd()
    
    func = hd.HCFS_FindStrMutilHVPointsByMem
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double,
        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    buffer = (ctypes.c_ubyte * 数据大小).from_buffer_copy(图片数据)

    return func(
        窗口序号, x, y, w, h,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        buffer, 数据大小, 是否开启反向相似度,
        排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64 __stdcall HCFS_FindStrMutilsAuto(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    支持多字符串识别的自动识字功能
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串，支持多字符串分割（示例："大理|无量山|溶洞"）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAuto
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        是否开启反向相似度, 排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64 __stdcall HCFS_FindStrMutilsAutoByFile(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, LPCSTR iamgeName, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字从文件(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片名字: str, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    从文件中识别多字符串的自动识字功能
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串，支持多字符串分割（示例："大理|无量山|溶洞"）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        图片名字: bmp图片名字，支持加路径
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAutoByFile
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p,
        ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        auto_encode(图片名字), 是否开启反向相似度,
        排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64 __stdcall HCFS_FindStrMutilsAutoByMem(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, BYTE* data, int dataSize, int bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字从内存(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片数据: bytes, 图片数据大小: int, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    从内存中识别多字符串的自动识字功能
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串，支持多字符串分割（示例："大理|无量山|溶洞"）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        图片数据: 图片的二进制数据
        图片数据大小: 图片数据的大小
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAutoByMem
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double,
        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    buffer = (ctypes.c_ubyte * 图片数据大小).from_buffer_copy(图片数据)

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        buffer, 图片数据大小, 是否开启反向相似度,
        排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64 __stdcall HCFS_FindStrMutilsAutoEx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, long bfx, int dirType=0, int bFindOne=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字Ex(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, CA字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 是否找到一个就返回: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    扩展版自动识字功能，支持找到一个就返回的控制
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        CA字符串: 需要找的字符串，支持多字符串分割
        偏色: RGB偏色设置
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        是否找到一个就返回: 是否找到一个就返回（默认0）
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAutoEx
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(CA字符串), auto_encode(偏色), 相似度,
        是否开启反向相似度, 排序方向类型, 是否找到一个就返回,
        水平间距, 垂直间距, 周围占比, 是否独占11
    )

# INT64  __stdcall HCFS_FindStrMutilsAutoByFileEx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, LPCSTR iamgeName, long bfx, int dirType=0, int bFindOne=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字从文件Ex(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片名字: str, 是否开启反向相似度: int, 排序方向类型: int = 0, 是否找到一个就返回: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    扩展版从文件识别多字符串的自动识字功能，支持找到一个就返回
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串，支持多字符串分割（示例："大理|无量山|溶洞"）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        图片名字: bmp图片名字，支持加路径
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        是否找到一个就返回: 是否找到一个就返回（默认0）
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAutoByFileEx
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p,
        ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        auto_encode(图片名字), 是否开启反向相似度,
        排序方向类型, 是否找到一个就返回, 水平间距,
        垂直间距, 周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_FindStrMutilsAutoByMemEx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR strs, LPCSTR color_format, double sim, BYTE* data, int dataSize, int bfx, int dirType=0, int bFindOne=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_自动识字从内存Ex(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 图片数据: bytes, 图片数据大小: int, 是否开启反向相似度: int, 排序方向类型: int = 0, 是否找到一个就返回: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    扩展版从内存识别多字符串的自动识字功能，支持找到一个就返回
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串，支持多字符串分割（示例："大理|无量山|溶洞"）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        图片数据: 图片的二进制数据
        图片数据大小: 图片数据的大小
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        是否找到一个就返回: 是否找到一个就返回（默认0）
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsAutoByMemEx
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double,
        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    buffer = (ctypes.c_ubyte * 图片数据大小).from_buffer_copy(图片数据)

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        buffer, 图片数据大小, 是否开启反向相似度,
        排序方向类型, 是否找到一个就返回, 水平间距,
        垂直间距, 周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_FindStrMutil(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_多字符识字(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    多字符识别功能，字库为字符串格式
    
    Args:
        窗口序号: 窗口序号 (从1开始)
        x: x坐标
        y: y坐标
        宽度: 宽度
        高度: 高度
        字符串: 需要找的字符串（示例：洛阳）
        偏色: RGB偏色设置（示例："ffffff-000000|1c1c1c-000000"）
        相似度: 整个像素矩阵的相似度
        是否开启反向相似度: 是否开启反向相似度
        排序方向类型: 排序类型/方向类型
        水平间距: 字体水平间距（默认11像素）
        垂直间距: 字体垂直间距（默认11像素）
        周围占比: 一个字的周围占比（默认0.1）
        是否独占11: 一个字是否独占11像素（默认True）
        
    Returns:
        返回值代码或成功找到返回MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutil
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        是否开启反向相似度, 排序方向类型, 水平间距,
        垂直间距, 周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_FindStrMutilsEx(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR str, LPCSTR color_format, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_多字符识字Ex(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 字符串: str, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    多字符串找(扩展版本) 字库是字符串 例如:洛阳| 北京|广州
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: x坐标
    :param y: y坐标
    :param 宽度: 宽度
    :param 高度: 高度
    :param 字符串: 需要找的字符串 支持多字符串 例如: 大理|无量山|溶洞 "|" 分割
    :param 偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
    :param 相似度: 整个像素矩阵的相似度
    :param 是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
    :param 排序方向类型: 排序类型 / 方向类型 排序/方向类型
    :param 水平间距: 字体水平间距 默认11像素
    :param 垂直间距: 字体垂直间距 默认11像素
    :param 周围占比: 一个字的周围占比 默认0.1
    :param 是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
    :return: 返回值代码(查看HD返回值表) 或者 成功找到返回:MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_FindStrMutilsEx
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_long,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(字符串), auto_encode(偏色), 相似度,
        是否开启反向相似度, 排序方向类型, 水平间距,
        垂直间距, 周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_Ocr(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR deltaColor, double sim, long bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_Ocr(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 偏色: str, 相似度: float, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内识别字 字库是字符串或单字 拼接+字符串都支持
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: x坐标
    :param y: y坐标
    :param 宽度: 宽度
    :param 高度: 高度
    :param 偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
    :param 相似度: 整个像素矩阵的相似度
    :param 是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
    :param 排序方向类型: 排序类型 / 方向类型 排序/方向类型
    :param 水平间距: 字体水平间距 默认11像素
    :param 垂直间距: 字体垂直间距 默认11像素
    :param 周围占比: 一个字的周围占比 默认0.1
    :param 是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
    :return: 返回值代码(查看HD返回值表) 或者 成功找到返回:MAKEXYWHTO8(fx1, fy1, w, h)
    """
    hd = Config.get_hd()

    func = hd.HCFS_Ocr
    func.restype = ctypes.c_int64
    func.argtypes = [
        ctypes.c_int, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long,
        ctypes.c_char_p, ctypes.c_double, ctypes.c_long,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool
    ]

    return func(
        窗口序号, x, y, 宽度, 高度,
        auto_encode(偏色), 相似度, 是否开启反向相似度,
        排序方向类型, 水平间距, 垂直间距,
        周围占比, 是否独占11
    )


# INT64  __stdcall HCFS_OcrByFile(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR color_format, double sim, LPCSTR iamgeName, int bfx, int dirType=0, int spaceH=11, int spaceV=11, double groundRate=0.1, BOOL bOne11=TRUE);
def HD识字_Ocr从文件(窗口序号: int, x: int, y: int, 宽度: int, 高度: int, 偏色: str, 相似度: float, 图片名字: str, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内识别字(原图从文件) 字库是字符串或单字 拼接+字符串都支持
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: x坐标
    :param y: y坐标
    :param 宽度: 宽度
    :param 高度: 高度
    :param 偏色: 偏色(如: ffffff-000000|1c1c1c-000000) RGB 十六进制 "|" 分割 多点找字
    :param 相似度: 整个像素矩阵的相似度
    :param 图片名字: 指定一张识字的图片文件(.bmp),支持加路径,不加路径则在全局路径找,图片后缀不要省略(支持绝对路径和相对路径)
    :param 是否开启反向相似度: 是否开启反向相似度(开启更精准,但是对于一些小范围的可能会过滤掉,一般开启就行)
    :param 排序方向类型: 排序类型 / 方向类型 排序/方向类型
    :param 水平间距: 字体水平间距 默认11像素
    :param 垂直间距: 字体垂直间距 默认11像素
    :param 周围占比: 一个字的周围占比 默认0.1
    :param 是否独占11: 一个字是否独占11像素 默认真/TRUE/开启
    :return: 返回值代码(查看HD返回值表) 或者 json格式的识字结果
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCFS_OcrByFile = hd.HCFS_OcrByFile
    HCFS_OcrByFile.restype = ctypes.c_int64
    HCFS_OcrByFile.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_long,   # x
        ctypes.c_long,   # y
        ctypes.c_long,   # 宽度
        ctypes.c_long,   # 高度
        ctypes.c_char_p, # 偏色
        ctypes.c_double, # 相似度
        ctypes.c_char_p, # 图片名字
        ctypes.c_int32,  # 是否开启反向相似度
        ctypes.c_int32,  # 排序方向类型
        ctypes.c_int32,  # 水平间距
        ctypes.c_int32,  # 垂直间距
        ctypes.c_double, # 周围占比
        ctypes.c_bool    # 是否独占11
    ]

    # 将偏色和图片名字转换为字节串
    偏色_bytes = auto_encode(偏色)
    图片名字_bytes = auto_encode(图片名字)

    # 调用C函数
    ret = HCFS_OcrByFile(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(宽度),
        ctypes.c_long(高度),
        ctypes.c_char_p(偏色_bytes),
        ctypes.c_double(相似度),
        ctypes.c_char_p(图片名字_bytes),
        ctypes.c_int32(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )
    return ret


# INT64  __stdcall HCFS_OcrByMem(int 窗口序号, long findX, long findY, long findW, long findH, LPCSTR color_format, double sim, BYTE* data, int dataSize, int bfx, int dirType= 0 , int spaceH = 11, int spaceV = 11, double groundRate = 0.1, BOOL bOne11= TRUE);
def HD识字_Ocr从内存(窗口序号: int, x: int, y: int, w: int, h: int, 偏色: str, 相似度: float, 图片数据: bytes, 图片数据大小: int, 是否开启反向相似度: int, 排序方向类型: int = 0, 水平间距: int = 11, 垂直间距: int = 11, 周围占比: float = 0.1, 是否独占11: bool = True) -> int:
    """
    在客户区范围内识别字(原图从内存) 字库是字符串或单字 拼接+字符串都支持
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 起始X坐标
    :param y: 起始Y坐标
    :param w: 宽度
    :param h: 高度
    :param 偏色: 偏色 (例如: ffffff-000000|1c1c1c-000000)
    :param 相似度: 整个像素矩阵的相似度
    :param 图片数据: 图片数据的二进制内存首地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
    :param 图片数据大小: 图片数据大小
    :param 是否开启反向相似度: 是否开启反向相似度 (开启更精准)
    :param 排序方向类型: 排序类型/方向类型 (默认0)
    :param 水平间距: 字体水平间距 (默认11像素)
    :param 垂直间距: 字体垂直间距 (默认11像素)
    :param 周围占比: 一个字的周围占比 (默认0.1)
    :param 是否独占11: 一个字是否独占11像素 (默认True)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCFS_OcrByMem = hd.HCFS_OcrByMem
    HCFS_OcrByMem.restype = ctypes.c_int64
    HCFS_OcrByMem.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_long,        # x
        ctypes.c_long,        # y
        ctypes.c_long,        # w
        ctypes.c_long,        # h
        ctypes.c_char_p,      # 偏色
        ctypes.c_double,      # 相似度
        ctypes.POINTER(ctypes.c_ubyte),  # 图片数据
        ctypes.c_int32,       # 图片数据大小
        ctypes.c_int32,       # 是否开启反向相似度
        ctypes.c_int32,       # 排序方向类型
        ctypes.c_int32,       # 水平间距
        ctypes.c_int32,       # 垂直间距
        ctypes.c_double,      # 周围占比
        ctypes.c_bool         # 是否独占11
    ]

    # 将偏色转换为字节串
    color_bytes = auto_encode(偏色)

    # 调用C函数
    ret = HCFS_OcrByMem(
        ctypes.c_int32(窗口序号),
        ctypes.c_long(x),
        ctypes.c_long(y),
        ctypes.c_long(w),
        ctypes.c_long(h),
        color_bytes,
        ctypes.c_double(相似度),
        图片数据,
        ctypes.c_int32(图片数据大小),
        ctypes.c_int32(是否开启反向相似度),
        ctypes.c_int32(排序方向类型),
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距),
        ctypes.c_double(周围占比),
        ctypes.c_bool(是否独占11)
    )

    return ret


# INT64  __stdcall HCFS_SetCharSpaceHV(int lenH = 11, int lenV = 11);
def HD识字_设置水平垂直间距(水平间距: int = 11, 垂直间距: int = 11) -> int:
    """
    设置间距 (在识别拼接字和OCR中尤其重要)
    :param 水平间距: 水平方向的间距 (默认11像素)
    :param 垂直间距: 垂直方向的间距 (默认11像素)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCFS_SetCharSpaceHV = hd.HCFS_SetCharSpaceHV
    HCFS_SetCharSpaceHV.restype = ctypes.c_int64
    HCFS_SetCharSpaceHV.argtypes = [
        ctypes.c_int32,  # 水平间距
        ctypes.c_int32   # 垂直间距
    ]

    # 调用C函数
    ret = HCFS_SetCharSpaceHV(
        ctypes.c_int32(水平间距),
        ctypes.c_int32(垂直间距)
    )

    return ret

# INT64  __stdcall HCFS_IsOne11(BOOL b = TRUE);
def HD识字_设置11(是否独占11: bool = True) -> int:
    """
    设置11行中(同宽)矩形内,是否只有一个字
    :param 是否独占11: 是否独占11像素 (默认True)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCFS_IsOne11 = hd.HCFS_IsOne11
    HCFS_IsOne11.restype = ctypes.c_int64
    HCFS_IsOne11.argtypes = [
        ctypes.c_bool  # 是否独占11
    ]

    # 调用C函数
    ret = HCFS_IsOne11(
        ctypes.c_bool(是否独占11)
    )

    return ret

# double  __stdcall HCFS_GroundRate(double rate = 0.1);
def HD识字_设置周围占比(周围占比: float = 0.1) -> int:
    """
    设置字周围一个像素 上下左右的像素占比
    :param 周围占比: 一个字的周围占比 (默认0.1)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCFS_GroundRate = hd.HCFS_GroundRate
    HCFS_GroundRate.restype = ctypes.c_double
    HCFS_GroundRate.argtypes = [
        ctypes.c_double  # 周围占比
    ]

    # 调用C函数
    ret = HCFS_GroundRate(
        ctypes.c_double(周围占比)
    )

    return ret