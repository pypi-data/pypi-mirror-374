from .config import Config, ctypes
from .config import auto_encode

# __int64  __stdcall HCPOCR_AddModel (char* det_infer, char* cls_infer, char* rec_infer, char* keys,char* parameterjson,char* password = NULL);
def HDPOCR_添加模型(det_infer: str,cls_infer: str,rec_infer: str,keys: str,parameterjson: str,password: str) -> int:
    """
    添加onnx字库模型并开启OCR服务 (组件7)
    多次调用会自动关闭之前的服务然后重启

    Args:
        det_infer:训练模型onnx 如:ch_PP-OCRv5_mobile_det.onnx
        cls_infer:校验模型onnx 如:ch_PP-OCRv5_rec_mobile_infer.onnx
        rec_infer:方向模型onnx 如:ch_ppocr_mobile_v2.0_cls_infer.onnx 一般不指定默认使用官方默认的
        keys:字典字库文件txt 如:ppocrv5_dict.txt 一般官方有字集文件 如果没有就自己写一个 一行一个字
        parameterjson:参数json格式字符串
        password:模型加解密密码 调试版本不能使用加载模型
    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2 传递参数7来安装HPOCR组件模块
    json配置参数:"{ \"cpu_mem\":0,\"cpu_threads\":2,\"use_gpu\":false,\"gpu_id\":-1,\"gpu_mem\":1024,\"padding\":50,\"maxSideLen\":1024,\"boxScoreThresh\":0.5,\"boxThresh\":0.3,\"unClipRatio\":1.6,\"doAngle\":true,\"mostAngle\":true,\"visualize\":false,\"enable_log\":false,\"isOutputConsole\":true}";
    """
    hd = Config.get_hd()

    HCPOCR_AddModel = hd.HCPOCR_AddModel
    HCPOCR_AddModel.restype = ctypes.c_int64
    HCPOCR_AddModel.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p
    ]

    ret = HCPOCR_AddModel (auto_encode(det_infer),auto_encode(cls_infer),auto_encode(rec_infer),auto_encode(keys),  auto_encode(parameterjson),auto_encode(password))
    return ret


# __int64  __stdcall HCPOCR_Identify(__int32 windIndex, int x = -1, int y = -1, int w = -1, int h = -1, float conf = 0.7f, int fType  = 0, BOOL retText = TRUE, BOOL bDebug = FALSE);
def HDPOCR_识别(windIndex: int,x: int,y: int,w: int,h: int,conf: float,fType: int,retText: bool,bDebug: bool) -> int:
    """
    基于截图缓存识别 (组件7)

    Args:
        windIndex:窗口序号
        x,y,w,h:左上角+宽度+高度 全为-1表示全图 内部自动修正
        conf:每个字或字符的相似度 当retText为真同时大于0 表示对每个字符置信度进程过滤(返回匹配的字符数量) 当retText为真同时conf小于等于0表示直接返回字符串(不过滤)(有字符串返回1空字符串返回0)
        fType:过滤类型 0 默认表示字符串每个字符的相似度的总和然后求平均值,最后conf和这个平均值比较(返回值表示匹配的字符串数量) 1 表示每个字符单独的相似度比较(返回值表示匹配的字符数量)
        retText:是否仅返回文本信息 设置为真表示需要对文本进程处理 具体如何处理看conf置信度的值大小 反之设置为假包含各种坐标属性json信息(始终返回1 需要自行解析json)
        bDebug:是否调试查看识别图片

    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2 传递参数7来安装HPOCR组件模块
    json配置参数:"{ \"cpu_mem\":0,\"cpu_threads\":2,\"use_gpu\":false,\"gpu_id\":-1,\"gpu_mem\":1024,\"padding\":50,\"maxSideLen\":1024,\"boxScoreThresh\":0.5,\"boxThresh\":0.3,\"unClipRatio\":1.6,\"doAngle\":true,\"mostAngle\":true,\"visualize\":false,\"enable_log\":false,\"isOutputConsole\":true}";
    """
    hd = Config.get_hd()

    HCPOCR_Identify = hd.HCPOCR_Identify
    HCPOCR_Identify.restype = ctypes.c_int64
    HCPOCR_Identify.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_float,
        ctypes.c_int32,
        ctypes.c_bool,
        ctypes.c_bool
    ]

    ret = HCPOCR_Identify (ctypes.c_int32(windIndex),ctypes.c_int32(x),ctypes.c_int32(y),ctypes.c_int32(w),ctypes.c_int32(h),ctypes.c_float(conf),ctypes.c_int32(fType),ctypes.c_bool(retText),ctypes.c_bool(bDebug))
    return ret


# __int64  __stdcall HCPOCR_IdentifyByFile(__int32 windIndex, char* imageFile, float conf = 0.7f, int fType = 0, BOOL retText = TRUE, BOOL bDebug = FALSE);
def HDPOCR_识别图片(windIndex: int,imageFile:str,conf: float,fType: int,retText: bool,bDebug: bool) -> int:
    """
    基于截图缓存识别 (组件7)

    Args:
        windIndex:窗口序号
        imageFile:图片路径(绝对路径或者相对路径)
        conf:每个字或字符的相似度 当retText为真同时大于0 表示对每个字符置信度进程过滤(返回匹配的字符数量) 当retText为真同时conf小于等于0表示直接返回字符串(不过滤)(有字符串返回1空字符串返回0)
        fType:过滤类型 0 默认表示字符串每个字符的相似度的总和然后求平均值,最后conf和这个平均值比较(返回值表示匹配的字符串数量) 1 表示每个字符单独的相似度比较(返回值表示匹配的字符数量)
        retText:是否仅返回文本信息 设置为真表示需要对文本进程处理 具体如何处理看conf置信度的值大小 反之设置为假包含各种坐标属性json信息(始终返回1 需要自行解析json)
        bDebug:是否调试查看识别图片

    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2 传递参数7来安装HPOCR组件模块
    json配置参数:"{ \"cpu_mem\":0,\"cpu_threads\":2,\"use_gpu\":false,\"gpu_id\":-1,\"gpu_mem\":1024,\"padding\":50,\"maxSideLen\":1024,\"boxScoreThresh\":0.5,\"boxThresh\":0.3,\"unClipRatio\":1.6,\"doAngle\":true,\"mostAngle\":true,\"visualize\":false,\"enable_log\":false,\"isOutputConsole\":true}";
    """
    hd = Config.get_hd()

    HCPOCR_Identify = hd.HCPOCR_Identify
    HCPOCR_Identify.restype = ctypes.c_int64
    HCPOCR_Identify.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_float,
        ctypes.c_int32,
        ctypes.c_bool,
        ctypes.c_bool
    ]

    ret = HCPOCR_Identify (ctypes.c_int32(windIndex),auto_encode(imageFile),ctypes.c_float(conf),ctypes.c_int32(fType),ctypes.c_bool(retText),ctypes.c_bool(bDebug))
    return ret


# __int64  __stdcall HCPOCR_IdentifyByMem(__int32 windIndex, void* imagebytedata, int size, float conf = 0.7f, int fType = 0, BOOL retText = TRUE, BOOL bDebug = FALSE);
def HDPOCR_识别图片数据(windIndex: int,imagebytedata:bytes,size:int,conf: float,fType: int,retText: bool,bDebug: bool) -> int:
    """
    基于指定图片内存识别 (组件7)

    Args:
        windIndex:窗口序号
        imagebytedata:一般是BMP图片数据 包含头+数据
        size:图片数据大小
        conf:每个字或字符的相似度 当retText为真同时大于0 表示对每个字符置信度进程过滤(返回匹配的字符数量) 当retText为真同时conf小于等于0表示直接返回字符串(不过滤)(有字符串返回1空字符串返回0)
        fType:过滤类型 0 默认表示字符串每个字符的相似度的总和然后求平均值,最后conf和这个平均值比较(返回值表示匹配的字符串数量) 1 表示每个字符单独的相似度比较(返回值表示匹配的字符数量)
        retText:是否仅返回文本信息 设置为真表示需要对文本进程处理 具体如何处理看conf置信度的值大小 反之设置为假包含各种坐标属性json信息(始终返回1 需要自行解析json)
        bDebug:是否调试查看识别图片

    Returns:
        int: 返回值代码（查看HD返回值表）

    Note:
    需要调用HCHD_LoadDrv2 传递参数7来安装HPOCR组件模块
    json配置参数:"{ \"cpu_mem\":0,\"cpu_threads\":2,\"use_gpu\":false,\"gpu_id\":-1,\"gpu_mem\":1024,\"padding\":50,\"maxSideLen\":1024,\"boxScoreThresh\":0.5,\"boxThresh\":0.3,\"unClipRatio\":1.6,\"doAngle\":true,\"mostAngle\":true,\"visualize\":false,\"enable_log\":false,\"isOutputConsole\":true}";
    """
    hd = Config.get_hd()

    HCPOCR_IdentifyByMem = hd.HCPOCR_IdentifyByMem
    HCPOCR_IdentifyByMem.restype = ctypes.c_int64
    HCPOCR_IdentifyByMem.argtypes = [
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.c_float,
        ctypes.c_int32,
        ctypes.c_bool,
        ctypes.c_bool
    ]

    # 创建字节数组
    buffer = (ctypes.c_ubyte * len(imagebytedata))(*imagebytedata)

    ret = HCPOCR_IdentifyByMem (ctypes.c_int32(windIndex),buffer,ctypes.c_int32(size),ctypes.c_float(conf),ctypes.c_int32(fType),ctypes.c_bool(retText),ctypes.c_bool(bDebug))
    return ret