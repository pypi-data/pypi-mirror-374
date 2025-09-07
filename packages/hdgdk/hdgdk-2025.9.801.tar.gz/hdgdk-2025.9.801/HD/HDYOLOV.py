from .config import Config, ctypes
from .config import auto_encode

def HDYOLOV_添加模型(版本: int, 模型数据: bytes, 参数数据: bytes, 图片大小: int = 640, 是否GPU: bool = False, 密码: str = "") -> int:
    """
    添加YOLOV（ncnn.bin和ncnn.param）模型文件（从内存中加载模型）
    需要调用HCHD_LoadDrv2传递参数4来安装YOLOV组件模块
    
    Args:
        版本: YOLOV版本，支持5、8、10、11版本
        模型数据: ncnn.bin模型文件的二进制数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        参数数据: ncnn.param模型文件的二进制数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        图片大小: 训练时候的图片大小，默认640
        是否GPU: 是否GPU识别，默认False
        密码: 密码，默认空
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_AddModel = hd.HCYOLO_AddModel
    HCYOLO_AddModel.restype = ctypes.c_int64
    HCYOLO_AddModel.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool, ctypes.c_char_p]
    
    模型数据缓冲区 = ctypes.create_string_buffer(模型数据)
    参数数据缓冲区 = ctypes.create_string_buffer(参数数据)
    
    ret = HCYOLO_AddModel(
        ctypes.c_int32(版本),
        ctypes.cast(模型数据缓冲区, ctypes.c_void_p),
        ctypes.c_int32(len(模型数据)),
        ctypes.cast(参数数据缓冲区, ctypes.c_void_p),
        ctypes.c_int32(len(参数数据)),
        ctypes.c_int32(图片大小),
        ctypes.c_bool(是否GPU),
        auto_encode(密码) if 密码 else None
    )
    return ret

def HDYOLOV_添加模型文件(版本: int, 模型文件名: str, 参数文件名: str, 图片大小: int = 640, 是否GPU: bool = False, 密码: str = "") -> int:
    """
    添加YOLOV（ncnn.bin和ncnn.param）模型文件（从文件中加载模型）
    需要调用HCHD_LoadDrv2传递参数4来安装YOLOV组件模块
    
    Args:
        版本: YOLOV版本，支持5、8、10、11版本
        模型文件名: ncnn.bin模型文件名（支持绝对路径或相对路径）
        参数文件名: ncnn.param模型文件名（支持绝对路径或相对路径）
        图片大小: 训练时候的图片大小，默认640
        是否GPU: 是否GPU识别，默认False
        密码: 密码，默认空
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_AddModelFile = hd.HCYOLO_AddModelFile
    HCYOLO_AddModelFile.restype = ctypes.c_int64
    HCYOLO_AddModelFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_char_p]
    
    ret = HCYOLO_AddModelFile(
        ctypes.c_int32(版本),
        auto_encode(模型文件名),
        auto_encode(参数文件名),
        ctypes.c_int32(图片大小),
        ctypes.c_bool(是否GPU),
        auto_encode(密码) if 密码 else None
    )
    return ret

def HDYOLOV_识别(窗口序号: int, 置信度: float = 0.7, IOU阈值: float = 0.4, 是否调试: bool = False) -> int:
    """
    YOLOV识别（后台截图）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        置信度: 置信度，默认0.7
        IOU阈值: IOU阈值，默认0.4
        是否调试: 是否调试模式，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_Detect = hd.HCYOLO_Detect
    HCYOLO_Detect.restype = ctypes.c_int64
    HCYOLO_Detect.argtypes = [ctypes.c_int32, ctypes.c_float, ctypes.c_float, ctypes.c_bool]
    
    ret = HCYOLO_Detect(
        ctypes.c_int32(窗口序号),
        ctypes.c_float(置信度),
        ctypes.c_float(IOU阈值),
        ctypes.c_bool(是否调试)
    )
    return ret

def HDYOLOV_识别从文件(窗口序号: int, 图片路径: str, 置信度: float = 0.7, IOU阈值: float = 0.4, 是否调试: bool = False) -> int:
    """
    YOLOV识别（从文件）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        图片路径: 图片文件路径
        置信度: 置信度，默认0.7
        IOU阈值: IOU阈值，默认0.4
        是否调试: 是否调试模式，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_DetectFromFile = hd.HCYOLO_DetectFromFile
    HCYOLO_DetectFromFile.restype = ctypes.c_int64
    HCYOLO_DetectFromFile.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_float, ctypes.c_float, ctypes.c_bool]
    
    ret = HCYOLO_DetectFromFile(
        ctypes.c_int32(窗口序号),
        auto_encode(图片路径),
        ctypes.c_float(置信度),
        ctypes.c_float(IOU阈值),
        ctypes.c_bool(是否调试)
    )
    return ret

def HDYOLOV_识别从内存(窗口序号: int, 图片数据: bytes, 置信度: float = 0.7, IOU阈值: float = 0.4, 是否调试: bool = False) -> int:
    """
    YOLOV识别（从内存）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        图片数据: 图片二进制数据 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        置信度: 置信度，默认0.7
        IOU阈值: IOU阈值，默认0.4
        是否调试: 是否调试模式，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_DetectFromMemory = hd.HCYOLO_DetectFromMemory
    HCYOLO_DetectFromMemory.restype = ctypes.c_int64
    HCYOLO_DetectFromMemory.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_float, ctypes.c_float, ctypes.c_bool]
    
    图片数据缓冲区 = ctypes.create_string_buffer(图片数据)
    
    ret = HCYOLO_DetectFromMemory(
        ctypes.c_int32(窗口序号),
        ctypes.cast(图片数据缓冲区, ctypes.c_void_p),
        ctypes.c_int32(len(图片数据)),
        ctypes.c_float(置信度),
        ctypes.c_float(IOU阈值),
        ctypes.c_bool(是否调试)
    )
    return ret

def HDYOLOV_范围识别(窗口序号: int, X坐标: int, Y坐标: int, 宽度: int, 高度: int, 置信度: float = 0.7, IOU阈值: float = 0.4, 是否调试: bool = False) -> int:
    """
    YOLOV范围识别（指定区域后台截图）
    
    Args:
        窗口序号: 窗口序号（从1开始）
        X坐标: 区域起始X坐标
        Y坐标: 区域起始Y坐标
        宽度: 区域宽度
        高度: 区域高度
        置信度: 置信度，默认0.7
        IOU阈值: IOU阈值，默认0.4
        是否调试: 是否调试模式，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_DetectRange = hd.HCYOLO_DetectRange
    HCYOLO_DetectRange.restype = ctypes.c_int64
    HCYOLO_DetectRange.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_float, ctypes.c_float, ctypes.c_bool]
    
    ret = HCYOLO_DetectRange(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(X坐标),
        ctypes.c_int32(Y坐标),
        ctypes.c_int32(宽度),
        ctypes.c_int32(高度),
        ctypes.c_float(置信度),
        ctypes.c_float(IOU阈值),
        ctypes.c_bool(是否调试)
    )
    return ret

def HDYOLOV_移除模型() -> int:
    """
    移除YOLOV模型
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_RemoveModel = hd.HCYOLO_RemoveModel
    HCYOLO_RemoveModel.restype = ctypes.c_int64
    HCYOLO_RemoveModel.argtypes = []
    
    ret = HCYOLO_RemoveModel()
    return ret

def HDYOLOV_设置标签(标签列表: str) -> int:
    """
    设置YOLOV识别标签
    
    Args:
        标签列表: 标签列表字符串，如："person,car,bicycle"
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCYOLO_SetLabel = hd.HCYOLO_SetLabel
    HCYOLO_SetLabel.restype = ctypes.c_int64
    HCYOLO_SetLabel.argtypes = [ctypes.c_char_p]
    
    ret = HCYOLO_SetLabel(auto_encode(标签列表))
    return ret