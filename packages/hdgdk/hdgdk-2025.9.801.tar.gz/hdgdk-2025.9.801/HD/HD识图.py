from .config import Config, ctypes
from .config import auto_encode

# __int64 __stdcall HCFP_Capture(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* fileNamePath, BOOL 是否打开查看器 = FALSE);
def HD识图_截图(窗口序号: int, x: int, y: int, w: int, h: int, fileNamePath: str, 是否打开查看器: bool = False) -> int:
    """
    截图并保存到文件(.bmp)
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param fileNamePath: 保存到文件的路径+文件名(.bmp)
    :param 是否打开查看器: 是否打开查看
    :return:
    """
    hd = Config.get_hd()
    hd.HCFP_Capture.restype = ctypes.c_int64
    # 定义函数指针类型
    hd.HCFP_Capture.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 矩形范围左上角x
        ctypes.c_int32,  # 矩形范围左上角y
        ctypes.c_int32,  # 矩形范围宽度
        ctypes.c_int32,  # 矩形范围高度
        ctypes.c_char_p,  # 保存到文件的路径+文件名(.bmp)
        ctypes.c_bool  # 是否打开查看
    ]
    ret = hd.HCFP_Capture(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        auto_encode(fileNamePath),
        ctypes.c_bool(是否打开查看器)
    )
    return ret
# __int64 __stdcall HCFP_FindColor(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType);
def HD识图_单点找色(窗口序号: int, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    单点找色
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制 RGB-偏色|000000-000000|000000-000000
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColor = hd.HCFP_FindColor
    HCFP_FindColor.restype = ctypes.c_int64
    HCFP_FindColor.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColor(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindColors(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType);
def HD识图_多点找色(窗口序号: int, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    多点找色
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制 RGB-偏色|000000-000000|000000-000000
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColors = hd.HCFP_FindColors
    HCFP_FindColors.restype = ctypes.c_int64
    HCFP_FindColors.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColors(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindColorsOffset(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* firstDeltaColor, char* deltaColor, double sim, __int32 bALL, __int32 dirType);
def HD识图_多点偏移找色(窗口序号: int, x: int, y: int, w: int, h: int, firstDeltaColor: str, deltaColor: str, sim: float, bALL: int = 0, dirType: int = 0) -> int:
    """
    多点偏移找色
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param firstDeltaColor: 首色 XXXXXX-YYYYYY 格式
    :param deltaColor: 偏移色 x1|y1|XXXXXX-YYYYYY| XXXXXX-YYYYYY| ...,x2|y3|XXXXXX-YYYYYY| XXXXXX-YYYYYY| ...,...格式
    :param sim: 整个像素矩阵的相似度
    :param bALL: 是否返回所有 (默认0)
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorsOffset = hd.HCFP_FindColorsOffset
    HCFP_FindColorsOffset.restype = ctypes.c_int64
    HCFP_FindColorsOffset.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    firstDeltaColor_bytes = auto_encode(firstDeltaColor)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorsOffset(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        firstDeltaColor_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(bALL),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_CmpColors(__int32 窗口序号, __int32 x, __int32 y, char* deltaColor);
def HD识图_比较颜色(窗口序号: int, x: int, y: int, deltaColor: str) -> int:
    """
    比较颜色
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param deltaColor: XXXXXX-YYYYYY 格式
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColors = hd.HCFP_CmpColors
    HCFP_CmpColors.restype = ctypes.c_int64
    HCFP_CmpColors.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_CmpColors(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        deltaColor_bytes
    )
    return ret

# __int64 __stdcall HCFP_CmpColorExs(__int32 窗口序号, char* deltaXYColor);
def HD识图_比较颜色Ex(窗口序号: int, deltaXYColor: str) -> int:
    """
    多点找色确定某个图像块,指定多个具体点
    :param 窗口序号: 窗口序号 (从1开始)
    :param deltaXYColor: x1|y1|e3e6eb-101010|e3e6eb-101010|e3e6eb-101010|...,x2|y2|e3e6eb-101010|e3e6eb-101010|e3e6eb-101010|...
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColorExs = hd.HCFP_CmpColorExs
    HCFP_CmpColorExs.restype = ctypes.c_int64
    HCFP_CmpColorExs.argtypes = [ctypes.c_int32, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    deltaXYColor_bytes = auto_encode(deltaXYColor)

    ret = HCFP_CmpColorExs(
        ctypes.c_int32(窗口序号),
        deltaXYColor_bytes
    )
    return ret
# __int64 __stdcall HCFP_GetColor(__int32 窗口序号, __int32 x, __int32 y);
def HD识图_获取颜色(窗口序号: int, x: int, y: int) -> int:
    """
    获取某个点的颜色值
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_GetColor = hd.HCFP_GetColor
    HCFP_GetColor.restype = ctypes.c_int64
    HCFP_GetColor.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

    ret = HCFP_GetColor(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y)
    )
    return ret
# __int64 __stdcall HCFP_FindPic(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字: str, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    在客户区范围内找图
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param 图片名字: 一张图片(bmp)文件名字(不包含路径，路径调用HCRES_SetResPath全局设置)
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPic = hd.HCFP_FindPic
    HCFP_FindPic.restype = ctypes.c_int64
    HCFP_FindPic.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    图片名字_bytes = auto_encode(图片名字)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPic(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_FindPicEx(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字集合, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图Ex(窗口序号: int, x: int, y: int, w: int, h: int, 图片名字集合: str, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    在客户区范围内找图 (返回找到其中一张信息)
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param 图片名字集合: 多张张图片(bmp)文件名字(不包含路径，路径调用HCRES_SetResPath全局设置) ,以'|'分隔开
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicEx = hd.HCFP_FindPicEx
    HCFP_FindPicEx.restype = ctypes.c_int64
    HCFP_FindPicEx.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    图片名字集合_bytes = auto_encode(图片名字集合)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字集合_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret


# __int64 __stdcall HCFP_IsDisplayDead(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, __int32 mstime);
def HD识图_是否卡屏(窗口序号: int, x: int, y: int, w: int, h: int, mstime: int) -> int:
    """
    在客户区范围内检测再规定时间内是否卡图
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param mstime: 间隔时间(不变就说明卡屏了),不会卡主线程
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_IsDisplayDead = hd.HCFP_IsDisplayDead
    HCFP_IsDisplayDead.restype = ctypes.c_int64
    HCFP_IsDisplayDead.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

    ret = HCFP_IsDisplayDead(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        ctypes.c_int32(mstime)
    )
    return ret
# __int64 __stdcall HCFP_GetRangeCRC(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h);
def HD识图_获取区域图像CRC(窗口序号: int, x: int, y: int, w: int, h: int) -> int:
    """
    在客户区范围内获取像素CRC值,用于卡屏校验
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_GetRangeCRC = hd.HCFP_GetRangeCRC
    HCFP_GetRangeCRC.restype = ctypes.c_int64
    HCFP_GetRangeCRC.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

    ret = HCFP_GetRangeCRC(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h)
    )
    return ret
# __int64 __stdcall HCFP_FindColorByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType);
def HD识图_单点找色从文件(窗口序号: int, orgImageName: str, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    单点找色(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 指定一张原图数据(支持绝对路径和相对路径)bmp图片文件
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorByFile = hd.HCFP_FindColorByFile
    HCFP_FindColorByFile.restype = ctypes.c_int64
    HCFP_FindColorByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindColorByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType);
def HD识图_单点找色从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    单点找色(从内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorByMem = hd.HCFP_FindColorByMem
    HCFP_FindColorByMem.restype = ctypes.c_int64
    HCFP_FindColorByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindColorsByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType);
def HD识图_多点找色从文件(窗口序号: int, orgImageName: str, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    多点找色(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 指定一张原图数据(支持绝对路径和相对路径)bmp图片文件
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorsByFile = hd.HCFP_FindColorsByFile
    HCFP_FindColorsByFile.restype = ctypes.c_int64
    HCFP_FindColorsByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorsByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64  __stdcall   HCFP_FindColorsByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char* deltaColor, double sim, __int32 dirType= 0);
def HD识图_多点找色从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, w: int, h: int, deltaColor: str, sim: float, dirType: int = 0) -> int:
    """
    多点找色(从内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorsByMem = hd.HCFP_FindColorsByMem
    HCFP_FindColorsByMem.restype = ctypes.c_int64
    HCFP_FindColorsByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorsByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindColorsOffsetByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char* firstDeltaColor, char* deltaColor, double sim, __int32 bALL, __int32 dirType);
def HD识图_多点偏移找色从文件(窗口序号: int, orgImageName: str, x: int, y: int, w: int, h: int, firstDeltaColor: str, deltaColor: str, sim: float, bALL: int = 0, dirType: int = 0) -> int:
    """
    多点偏移找色(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 指定一张原图数据(支持绝对路径和相对路径)bmp图片文件
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param firstDeltaColor: 偏色(如:303030) RGB 十六进制
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param bALL: 是否全部 (默认0)
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorsOffsetByFile = hd.HCFP_FindColorsOffsetByFile
    HCFP_FindColorsOffsetByFile.restype = ctypes.c_int64
    HCFP_FindColorsOffsetByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)
    firstDeltaColor_bytes = auto_encode(firstDeltaColor)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorsOffsetByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        firstDeltaColor_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(bALL),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_FindColorsOffsetByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char* firstDeltaColor, char* deltaColor, double sim, __int32 bALL, __int32 dirType);
def HD识图_多点偏移找色从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, w: int, h: int, firstDeltaColor: str, deltaColor: str, sim: float, bALL: int = 0, dirType: int = 0) -> int:
    """
    多点偏移找色(从内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param x: 矩形范围左上角x
    :param y: 矩形范围左上角y
    :param w: 矩形范围宽度
    :param h: 矩形范围高度
    :param firstDeltaColor: 偏色(如:303030) RGB 十六进制
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 整个像素矩阵的相似度
    :param bALL: 是否全部 (默认0)
    :param dirType: 排序类型 / 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindColorsOffsetByMem = hd.HCFP_FindColorsOffsetByMem
    HCFP_FindColorsOffsetByMem.restype = ctypes.c_int64
    HCFP_FindColorsOffsetByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    firstDeltaColor_bytes = auto_encode(firstDeltaColor)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindColorsOffsetByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        firstDeltaColor_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(bALL),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindPicByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图从文件(窗口序号: int, 原图名字: str, x: int, y: int, w: int, h: int, 图片名字: str, deltaColor: str, sim: float = 0.9, dirType: int = 0) -> int:
    """
    范围找图(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param 原图名字: 指定一张原图文件名(支持绝对路径和相对路径)
    :param x: 左上角x
    :param y: 左上角y
    :param w: 宽度
    :param h: 高度
    :param 图片名字: 如:hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 相似度0-1 (默认0.9)
    :param dirType: 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicByFile = hd.HCFP_FindPicByFile
    HCFP_FindPicByFile.restype = ctypes.c_int64
    HCFP_FindPicByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    原图名字_bytes = auto_encode(原图名字)
    图片名字_bytes = auto_encode(图片名字)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicByFile(
        ctypes.c_int32(窗口序号),
        原图名字_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_FindPicByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, w: int, h: int, 图片名字: str, deltaColor: str, sim: float = 0.9, dirType: int = 0) -> int:
    """
    范围找图(从内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: 图片数据
    :param dataSize: 图片数据长度
    :param x: 左上角x
    :param y: 左上角y
    :param w: 宽度
    :param h: 高度
    :param 图片名字: 一张图片(bmp)文件名字(路径调用HCRES_SetResPath全局设置) (支持绝对路径和相对路径)
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 相似度0-1 (默认0.9)
    :param dirType: 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicByMem = hd.HCFP_FindPicByMem
    HCFP_FindPicByMem.restype = ctypes.c_int64
    HCFP_FindPicByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    图片名字_bytes = auto_encode(图片名字)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_FindPicExByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字集合, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图从文件Ex(窗口序号: int, 原图名字: str, x: int, y: int, w: int, h: int, 图片名字: str, deltaColor: str, sim: float = 0.9, dirType: int = 0) -> int:
    """
    范围找图(从文件)Ex
    :param 窗口序号: 窗口序号 (从1开始)
    :param 原图名字: 指定一张原图文件名(支持绝对路径和相对路径)
    :param x: 左上角x
    :param y: 左上角y
    :param w: 宽度
    :param h: 高度
    :param 图片名字: 如:hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 相似度0-1 (默认0.9)
    :param dirType: 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicExByFile = hd.HCFP_FindPicExByFile
    HCFP_FindPicExByFile.restype = ctypes.c_int64
    HCFP_FindPicExByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    原图名字_bytes = auto_encode(原图名字)
    图片名字_bytes = auto_encode(图片名字)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicExByFile(
        ctypes.c_int32(窗口序号),
        原图名字_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret

# __int64 __stdcall HCFP_FindPicExByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char* 图片名字集合, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图从内存Ex(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, w: int, h: int, 图片名字: str, deltaColor: str, sim: float = 0.9, dirType: int = 0) -> int:
    """
    范围找图(从内存)Ex
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: 图片数据
    :param dataSize: 图片数据长度
    :param x: 左上角x
    :param y: 左上角y
    :param w: 宽度
    :param h: 高度
    :param 图片名字: 如:hd1.bmp|hd2.bmp|hd3.bmp|hd4.bmp|
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 相似度0-1 (默认0.9)
    :param dirType: 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicExByMem = hd.HCFP_FindPicExByMem
    HCFP_FindPicExByMem.restype = ctypes.c_int64
    HCFP_FindPicExByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    图片名字_bytes = auto_encode(图片名字)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicExByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        图片名字_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_FindPicExFromMem(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char* 子图内存地址集合字符串, char* deltaColor, double sim, __int32 dirType);
def HD识图_范围找图来源内存Ex(窗口序号: int, x: int, y: int, w: int, h: int, 子图内存地址集合字符串: str, deltaColor: str, sim: float = 0.9, dirType: int = 0) -> int:
    """
    范围找图(来源内存)Ex
    :param 窗口序号: 窗口序号 (从1开始)
    :param x: 左上角x
    :param y: 左上角y
    :param w: 宽度
    :param h: 高度
    :param 子图内存地址集合字符串: "地址1,长度1|地址2,长度2|地址3,长度3"  地址和长度用十进制表示
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :param sim: 相似度0-1 (默认0.9)
    :param dirType: 方向类型 (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_FindPicExFromMem = hd.HCFP_FindPicExFromMem
    HCFP_FindPicExFromMem.restype = ctypes.c_int64
    HCFP_FindPicExFromMem.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    子图内存地址集合字符串_bytes = auto_encode(子图内存地址集合字符串)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_FindPicExFromMem(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        子图内存地址集合字符串_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_int32(dirType)
    )
    return ret
# __int64 __stdcall HCFP_CmpColorsByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y, char* deltaColor);
def HD识图_比较颜色从文件(窗口序号: int, orgImageName: str, x: int, y: int, deltaColor: str) -> int:
    """
    比较颜色(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 原图名字
    :param x: 坐标x
    :param y: 坐标y
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColorsByFile = hd.HCFP_CmpColorsByFile
    HCFP_CmpColorsByFile.restype = ctypes.c_int64
    HCFP_CmpColorsByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_CmpColorsByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        deltaColor_bytes
    )
    return ret
# __int64 __stdcall HCFP_CmpColorsByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, char* deltaColor);
def HD识图_比较颜色从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int, deltaColor: str) -> int:
    """
    比较颜色(来源内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param x: 坐标x
    :param y: 坐标y
    :param deltaColor: 偏色(如:303030) RGB 十六进制
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColorsByMem = hd.HCFP_CmpColorsByMem
    HCFP_CmpColorsByMem.restype = ctypes.c_int64
    HCFP_CmpColorsByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    deltaColor_bytes = auto_encode(deltaColor)

    ret = HCFP_CmpColorsByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        deltaColor_bytes
    )
    return ret
# __int64 __stdcall HCFP_CmpColorExsByFile(__int32 窗口序号, char* orgImageName, char* deltaXYColor);
def HD识图_比较颜色从文件Ex(窗口序号: int, orgImageName: str, deltaXYColor: str) -> int:
    """
    多点找色确定某个图像块,指定多个具体点,从文件
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 原图名字
    :param deltaXYColor: 偏色坐标字符串 (如:"x1,y1,303030-x2,y2,404040")
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColorExsByFile = hd.HCFP_CmpColorExsByFile
    HCFP_CmpColorExsByFile.restype = ctypes.c_int64
    HCFP_CmpColorExsByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)
    deltaXYColor_bytes = auto_encode(deltaXYColor)

    ret = HCFP_CmpColorExsByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        deltaXYColor_bytes
    )
    return ret
# __int64 __stdcall  HCFP_CmpColorExsByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, char* deltaXYColor);
def HD识图_比较颜色从内存Ex(窗口序号: int, data: bytes, dataSize: int, deltaXYColor: str) -> int:
    """
    多点找色确定某个图像块,指定多个具体点,来源内存
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param deltaXYColor: 偏色坐标字符串 (如:"x1,y1,303030-x2,y2,404040")
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_CmpColorExsByMem = hd.HCFP_CmpColorExsByMem
    HCFP_CmpColorExsByMem.restype = ctypes.c_int64
    HCFP_CmpColorExsByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    deltaXYColor_bytes = auto_encode(deltaXYColor)

    ret = HCFP_CmpColorExsByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        deltaXYColor_bytes
    )
    return ret
# __int64 __stdcall HCFP_GetColorByFile(__int32 窗口序号, char* orgImageName, __int32 x, __int32 y);
def HD识图_获取颜色从文件(窗口序号: int, orgImageName: str, x: int, y: int) -> int:
    """
    获取颜色(从文件)
    :param 窗口序号: 窗口序号 (从1开始)
    :param orgImageName: 原图名字
    :param x: 坐标x
    :param y: 坐标y
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_GetColorByFile = hd.HCFP_GetColorByFile
    HCFP_GetColorByFile.restype = ctypes.c_int64
    HCFP_GetColorByFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32]

    # 使用auto_encode自动转换编码
    orgImageName_bytes = auto_encode(orgImageName)

    ret = HCFP_GetColorByFile(
        ctypes.c_int32(窗口序号),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y)
    )
    return ret

# __int64 __stdcall HCFP_GetColorByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y);
def HD识图_获取颜色从内存(窗口序号: int, data: bytes, dataSize: int, x: int, y: int) -> int:
    """
    获取颜色(来源内存)
    :param 窗口序号: 窗口序号 (从1开始)
    :param data: Bmp图片字节数据缓冲区地址
    :param dataSize: Bmp图片字节大小
    :param x: 坐标x
    :param y: 坐标y
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HCFP_GetColorByMem = hd.HCFP_GetColorByMem
    HCFP_GetColorByMem.restype = ctypes.c_int64
    HCFP_GetColorByMem.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

    ret = HCFP_GetColorByMem(
        ctypes.c_int32(窗口序号),
        data,
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y)
    )
    return ret

def HD识图_范围找图EXX(
    window_index: int,
    x: int,
    y: int,
    w: int,
    h: int,
    pic_names: str,
    deltaColor: str,
    sim: float,
    bAll: bool = True,
    dirType: int = 0
) -> int:
    """
    接口说明:
        在客户区范围内找图 (返回全部找到的信息)

    函数原型 ：
        __int64 __stdcall  HCFP_FindPicExx(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char*图片名字集合, char* deltaColor, double sim, BOOL bAll = TRUE, __int32 dirType = 0);

    参数说明:
        window_index: 窗口序号 (从1开始)  0表示全局全屏识别
        x: 矩形范围左上角x
        y: 矩形范围左上角y
        w: 矩形范围宽度
        h: 矩形范围高度
        pic_names: 多张图片(bmp)文件名字(不包含路径，路径调用HCRES_SetResPath全局设置) ,以'|'分隔开
        deltaColor: 偏色(如:303030) RGB 十六进制
        sim: 整个像素矩阵的相似度
        bAll: 是否全部找 如果不是表示每个图片只找一次就换下个图片
        dirType: 排序类型/方向类型

    返回值:
        int: 见HD返回值表，返回 0 1 或错误值
        返回json： {error:0,ret:[{bRet:NN,info:MM}]}
        MM：index1,x1,y1,w1,h1|index2,x2,y2,w3,h3|index3,x3,y3,w3,h3| 含义:  图片索引(0开始),左上角X,左上角Y,宽度,高度|

    备注:
        注意返回值含义和xy值的提取
    """
    hd = Config.get_hd()
    HCFP_FindPicExx = hd.HCFP_FindPicExx
    HCFP_FindPicExx.restype = ctypes.c_int64
    HCFP_FindPicExx.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_int32
    ]
    pic_names_bytes = auto_encode(pic_names)
    deltaColor_bytes = auto_encode(deltaColor)
    ret = HCFP_FindPicExx(
        ctypes.c_int32(window_index),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        pic_names_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_bool(bAll),
        ctypes.c_int32(dirType)
    )
    return ret

def HD识图_范围找图从文件Exx(
    window_index: int,
    orgImageName: str,
    x: int,
    y: int,
    w: int,
    h: int,
    pic_names: str,
    deltaColor: str,
    sim: float,
    bAll: bool = True,
    dirType: int = 0
) -> int:
    """
    接口说明:
        在客户区范围内找图(从文件) (找全部图片信息坐标)

    函数原型 ：
        __int64  __stdcall  HCFP_FindPicExxByFile(__int32 窗口序号, char*orgImageName, __int32 x, __int32 y, __int32 w, __int32 h, char*图片名字集合, char* deltaColor, double sim, BOOL bAll = TRUE, __int32 dirType= 0);

    参数说明:
        window_index: 窗口序号 (从1开始) 0表示全局全屏识别
        orgImageName: 指定一张原图数据(支持绝对路径和相对路径)
        x: 矩形范围左上角x
        y: 矩形范围左上角y
        w: 矩形范围宽度
        h: 矩形范围高度
        pic_names: 多张图片(bmp)文件名字(不包含路径，路径调用HCRES_SetResPath全局设置) ,以'|'分隔开(支持绝对路径和相对路径)
        deltaColor: 偏色(如:303030) RGB 十六进制
        sim: 整个像素矩阵的相似度
        bAll: 是否全部找 如果不是表示每个图片只找一次就换下个图片
        dirType: 排序类型/方向类型

    返回值:
        int: 见HD返回值表，返回 0 1 或错误值
        返回json： {error:0,ret:[{bRet:NN,info:MM}]}
        MM： index1,x1,y1,w1,h1|index2,x2,y2,w3,h3|index3,x3,y3,w3,h3| 含义:   图片索引(0开始),左上角X,左上角Y,宽度,高度|

    备注:
        注意返回值含义和xy值的提取
    """
    hd = Config.get_hd()
    HCFP_FindPicExxByFile = hd.HCFP_FindPicExxByFile
    HCFP_FindPicExxByFile.restype = ctypes.c_int64
    HCFP_FindPicExxByFile.argtypes = [
        ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_int32
    ]
    orgImageName_bytes = auto_encode(orgImageName)
    pic_names_bytes = auto_encode(pic_names)
    deltaColor_bytes = auto_encode(deltaColor)
    ret = HCFP_FindPicExxByFile(
        ctypes.c_int32(window_index),
        orgImageName_bytes,
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        pic_names_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_bool(bAll),
        ctypes.c_int32(dirType)
    )
    return ret

def HD识图_范围找图来源内存Exx(
    window_index: int,
    x: int,
    y: int,
    w: int,
    h: int,
    sub_img_mem_str: str,
    deltaColor: str,
    sim: float,
    bAll: bool = True,
    dirType: int = 0
) -> int:
    """
    接口说明:
        在客户区范围内找图(子图从内存) (找全部图片信息坐标)

    函数原型 ：
        __int64  __stdcall  HCFP_FindPicExxFromMem(__int32 窗口序号, __int32 x, __int32 y, __int32 w, __int32 h, char*子图内存地址集合字符串, char* deltaColor, double sim,  BOOL bAll = TRUE, __int32 dirType= 0);

    参数说明:
        window_index: 窗口序号 (从1开始)  0表示全局全屏识别
        sub_img_mem_str: "地址1,长度1|地址2,长度2|地址3,长度3" 地址和长度用十进制表示
        x: 矩形范围左上角x
        y: 矩形范围左上角y
        w: 矩形范围宽度
        h: 矩形范围高度
        deltaColor: 偏色(如:303030) RGB 十六进制
        sim: 整个像素矩阵的相似度
        bAll: 是否全部找 如果不是表示每个图片只找一次就换下个图片
        dirType: 排序类型/方向类型

    返回值:
        int: 见HD返回值表，返回 0 1 或错误值
        返回json： {error:0,ret:[{bRet:NN,info:MM}]}
        MM：index1,x1,y1,w1,h1|index2,x2,y2,w3,h3|index3,x3,y3,w3,h3| 含义:   图片索引(0开始),左上角X,左上角Y,宽度,高度|

    备注:
        注意返回值含义和xy值的提取
        图片内存缓冲区自己维护
    """
    hd = Config.get_hd()
    HCFP_FindPicExxFromMem = hd.HCFP_FindPicExxFromMem
    HCFP_FindPicExxFromMem.restype = ctypes.c_int64
    HCFP_FindPicExxFromMem.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_int32
    ]
    sub_img_mem_str_bytes = auto_encode(sub_img_mem_str)
    deltaColor_bytes = auto_encode(deltaColor)
    ret = HCFP_FindPicExxFromMem(
        ctypes.c_int32(window_index),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        sub_img_mem_str_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_bool(bAll),
        ctypes.c_int32(dirType)
    )
    return ret

def HD识图_范围找图从内存Exx(
    window_index: int,
    data: bytes,
    dataSize: int,
    x: int,
    y: int,
    w: int,
    h: int,
    pic_names: str,
    deltaColor: str,
    sim: float,
    bAll: bool = True,
    dirType: int = 0
) -> int:
    """
    接口说明:
        在客户区范围内找图(从内存)(找全部图片信息坐标)

    函数原型 ：
        __int64  __stdcall  HCFP_FindPicExxByMem(__int32 窗口序号, BYTE* data, __int32 dataSize, __int32 x, __int32 y, __int32 w, __int32 h, char*图片名字集合, char* deltaColor, double sim, BOOL bAll = TRUE, __int32 dirType= 0);

    参数说明:
        window_index: 窗口序号 (从1开始)  0表示全局全屏识别
        data: Bmp图片字节数据缓冲区地址
        dataSize: Bmp图片字节大小
        x: 矩形范围左上角x
        y: 矩形范围左上角y
        w: 矩形范围宽度
        h: 矩形范围高度
        pic_names: 多张图片(bmp)文件名字(不包含路径，路径调用HCRES_SetResPath全局设置) ,以'|'分隔开(支持绝对路径和相对路径)
        deltaColor: 偏色(如:303030) RGB 十六进制
        sim: 整个像素矩阵的相似度
        bAll: 是否全部找 如果不是表示每个图片只找一次就换下个图片
        dirType: 排序类型/方向类型

    返回值:
        int: 见HD返回值表，返回 0 1 或错误值
        返回json： {error:0,ret:[{bRet:NN,info:MM}]}
        MM： index1,x1,y1,w1,h1|index2,x2,y2,w3,h3|index3,x3,y3,w3,h3| 含义:  图片索引(0开始),左上角X,左上角Y,宽度,高度|

    备注:
        注意返回值含义和xy值的提取
        图片内存缓冲区自己维护
    """
    hd = Config.get_hd()
    HCFP_FindPicExxByMem = hd.HCFP_FindPicExxByMem
    HCFP_FindPicExxByMem.restype = ctypes.c_int64
    HCFP_FindPicExxByMem.argtypes = [
        ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double, ctypes.c_bool, ctypes.c_int32
    ]
    data_buffer = ctypes.create_string_buffer(data, dataSize)
    pic_names_bytes = auto_encode(pic_names)
    deltaColor_bytes = auto_encode(deltaColor)
    ret = HCFP_FindPicExxByMem(
        ctypes.c_int32(window_index),
        ctypes.cast(data_buffer, ctypes.c_void_p),
        ctypes.c_int32(dataSize),
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(w),
        ctypes.c_int32(h),
        pic_names_bytes,
        deltaColor_bytes,
        ctypes.c_double(sim),
        ctypes.c_bool(bAll),
        ctypes.c_int32(dirType)
    )
    return ret