from .config import Config, ctypes
from .config import auto_encode

# void __stdcall HCRES_SetResPathA(char * path);
def HD资源_设置路径A(路径: str) -> None:
    """
    设置ANSI编码资源路径
    :param 路径: ANSI编码路径字符串(自动转换为本地编码)
    :return: None
    """
    hd = Config.get_hd()

    HCRES_SetResPathA = hd.HCRES_SetResPathA
    HCRES_SetResPathA.restype = None
    HCRES_SetResPathA.argtypes = [ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    path_bytes = auto_encode(路径)

    HCRES_SetResPathA(path_bytes)


# void __stdcall HCRES_SetResPathW(wchar_t * path);
def HD资源_设置路径W(路径: str) -> None:
    """
    设置Unicode资源路径(Windows原生宽字符)
    :param 路径: Unicode路径字符串
    :return: None
    """
    hd = Config.get_hd()

    HCRES_SetResPathW = hd.HCRES_SetResPathW
    HCRES_SetResPathW.restype = None
    HCRES_SetResPathW.argtypes = [ctypes.c_wchar_p]

    # 直接传递Python字符串，ctypes自动转换宽字符
    HCRES_SetResPathW(ctypes.c_wchar_p(路径))

# void __stdcall  HCRES_SetResPathEx(__int32 windIndex, char * path);
def HD资源_设置路径Ex(窗口序号: int, 路径: str) -> None:
    """
    设置ANSI编码资源路径Ex
    :param 窗口序号: 窗口序号
    :param 路径: ANSI编码路径字符串(自动转换为本地编码)
    :return: None
    """
    hd = Config.get_hd()

    HCRES_SetResPathEx = hd.HCRES_SetResPathEx
    HCRES_SetResPathEx.restype = None
    HCRES_SetResPathEx.argtypes = [ctypes.c_int32,ctypes.c_char_p]

    # 使用auto_encode自动转换编码
    path_bytes = auto_encode(路径)

    HCRES_SetResPathEx(ctypes.c_int32(窗口序号),path_bytes)