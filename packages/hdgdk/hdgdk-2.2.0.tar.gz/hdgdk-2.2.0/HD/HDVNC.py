from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCVnc_Connect(int windowIndex, int port);
def HDVNC_连接虚拟机(窗口序号: int, 端口: int) -> int:
    """
    连接虚拟机VNC服务
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口，指定0表示重连
        端口: 虚拟机开启VNC设置的端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_Connect = hd.HCVnc_Connect
    HCVnc_Connect.restype = ctypes.c_int64
    HCVnc_Connect.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCVnc_Connect(ctypes.c_int32(窗口序号), ctypes.c_int32(端口))
    return ret

# INT64 __stdcall HCVnc_Close(int windowIndex);
def HDVNC_关闭连接(窗口序号: int) -> int:
    """
    关闭VNC虚拟机连接
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_Close = hd.HCVnc_Close
    HCVnc_Close.restype = ctypes.c_int64
    HCVnc_Close.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_Close(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_MoveTo(int windowIndex, int x, int y);
def HDVNC_鼠标绝对移动(窗口序号: int, X坐标: int, Y坐标: int) -> int:
    """
    VNC鼠标绝对移动（自带移动轨迹，直线波动防检测）
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        X坐标: 虚拟机屏幕坐标X
        Y坐标: 虚拟机屏幕坐标Y
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_MoveTo = hd.HCVnc_MoveTo
    HCVnc_MoveTo.restype = ctypes.c_int64
    HCVnc_MoveTo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCVnc_MoveTo(ctypes.c_int32(窗口序号), ctypes.c_int32(X坐标), ctypes.c_int32(Y坐标))
    return ret

# INT64 __stdcall HCVnc_MoveToOffset(int windowIndex, int x, int y);
def HDVNC_鼠标相对移动(窗口序号: int, X偏移: int, Y偏移: int) -> int:
    """
    VNC鼠标相对移动（自带移动轨迹，直线波动防检测）
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        X偏移: 虚拟机屏幕相对坐标X
        Y偏移: 虚拟机屏幕相对坐标Y
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_MoveToOffset = hd.HCVnc_MoveToOffset
    HCVnc_MoveToOffset.restype = ctypes.c_int64
    HCVnc_MoveToOffset.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCVnc_MoveToOffset(ctypes.c_int32(窗口序号), ctypes.c_int32(X偏移), ctypes.c_int32(Y偏移))
    return ret

# INT64 __stdcall HCVnc_LeftDown(int windowIndex);
def HDVNC_鼠标左键按下(窗口序号: int) -> int:
    """
    VNC鼠标左键按下
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_LeftDown = hd.HCVnc_LeftDown
    HCVnc_LeftDown.restype = ctypes.c_int64
    HCVnc_LeftDown.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_LeftDown(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_LeftUp(int windowIndex);
def HDVNC_鼠标左键弹起(窗口序号: int) -> int:
    """
    VNC鼠标左键弹起
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_LeftUp = hd.HCVnc_LeftUp
    HCVnc_LeftUp.restype = ctypes.c_int64
    HCVnc_LeftUp.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_LeftUp(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_LeftDoubleClick(int windowIndex);
def HDVNC_鼠标左键双击(窗口序号: int) -> int:
    """
    VNC鼠标左键双击
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_LeftDoubleClick = hd.HCVnc_LeftDoubleClick
    HCVnc_LeftDoubleClick.restype = ctypes.c_int64
    HCVnc_LeftDoubleClick.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_LeftDoubleClick(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_LeftClick(int windowIndex);
def HDVNC_鼠标左键点击(窗口序号: int) -> int:
    """
    VNC鼠标左键点击
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_LeftClick = hd.HCVnc_LeftClick
    HCVnc_LeftClick.restype = ctypes.c_int64
    HCVnc_LeftClick.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_LeftClick(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_RightClick(int windowIndex);
def HDVNC_鼠标右键点击(窗口序号: int) -> int:
    """
    VNC鼠标右键点击
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_RightClick = hd.HCVnc_RightClick
    HCVnc_RightClick.restype = ctypes.c_int64
    HCVnc_RightClick.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_RightClick(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_RightDown(int windowIndex);
def HDVNC_鼠标右键按下(窗口序号: int) -> int:
    """
    VNC鼠标右键按下
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_RightDown = hd.HCVnc_RightDown
    HCVnc_RightDown.restype = ctypes.c_int64
    HCVnc_RightDown.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_RightDown(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_RightUp(int windowIndex);
def HDVNC_鼠标右键弹起(窗口序号: int) -> int:
    """
    VNC鼠标右键弹起
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_RightUp = hd.HCVnc_RightUp
    HCVnc_RightUp.restype = ctypes.c_int64
    HCVnc_RightUp.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_RightUp(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_WheelDown(int windowIndex);
def HDVNC_鼠标滚轮滚下(窗口序号: int) -> int:
    """
    VNC鼠标滚轮向下滚动
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_WheelDown = hd.HCVnc_WheelDown
    HCVnc_WheelDown.restype = ctypes.c_int64
    HCVnc_WheelDown.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_WheelDown(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_WheelUp(int windowIndex);
def HDVNC_鼠标滚轮滚上(窗口序号: int) -> int:
    """
    VNC鼠标滚轮向上滚动
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_WheelUp = hd.HCVnc_WheelUp
    HCVnc_WheelUp.restype = ctypes.c_int64
    HCVnc_WheelUp.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_WheelUp(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_KeyTap(int windowIndex, int keycode, BOOL isKeypad);
def HDVNC_键盘按键敲击(窗口序号: int, 键码: int, 是否小键盘: bool = False) -> int:
    """
    VNC键盘按键敲击（按下+弹起）
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        键码: 键盘按键码
        是否小键盘: 是否为小键盘按键，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_KeyTap = hd.HCVnc_KeyTap
    HCVnc_KeyTap.restype = ctypes.c_int64
    HCVnc_KeyTap.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
    
    ret = HCVnc_KeyTap(ctypes.c_int32(窗口序号), ctypes.c_int32(键码), ctypes.c_bool(是否小键盘))
    return ret

# INT64 __stdcall HCVnc_KeyDown(int windowIndex, int keycode);
def HDVNC_键盘按键按下(窗口序号: int, 键码: int) -> int:
    """
    VNC键盘按键按下
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        键码: 键盘按键码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_KeyDown = hd.HCVnc_KeyDown
    HCVnc_KeyDown.restype = ctypes.c_int64
    HCVnc_KeyDown.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCVnc_KeyDown(ctypes.c_int32(窗口序号), ctypes.c_int32(键码))
    return ret

# INT64 __stdcall HCVnc_KeyUp(int windowIndex, int keycode);
def HDVNC_键盘按键弹起(窗口序号: int, 键码: int) -> int:
    """
    VNC键盘按键弹起
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        键码: 键盘按键码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_KeyUp = hd.HCVnc_KeyUp
    HCVnc_KeyUp.restype = ctypes.c_int64
    HCVnc_KeyUp.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCVnc_KeyUp(ctypes.c_int32(窗口序号), ctypes.c_int32(键码))
    return ret

# INT64 __stdcall HCVnc_KeysString(int windowIndex, char* strText, BOOL isKeypad);
def HDVNC_键盘连续按键字符串(窗口序号: int, 文本内容: str, 是否小键盘: bool = False) -> int:
    """
    VNC键盘连续按键字符串（只支持英文字符串）
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        文本内容: 要输入的字符串（只支持英文）
        是否小键盘: 是否为小键盘按键，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_KeysString = hd.HCVnc_KeysString
    HCVnc_KeysString.restype = ctypes.c_int64
    HCVnc_KeysString.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCVnc_KeysString(ctypes.c_int32(窗口序号), auto_encode(文本内容), ctypes.c_bool(是否小键盘))
    return ret

# INT64 __stdcall HCVnc_InputString(int windowIndex, char* strText);
def HDVNC_键盘输入字符串(窗口序号: int, 文本内容: str) -> int:
    """
    VNC键盘输入字符串（支持中文）
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
        文本内容: 要输入的字符串（支持中文）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_InputString = hd.HCVnc_InputString
    HCVnc_InputString.restype = ctypes.c_int64
    HCVnc_InputString.argtypes = [ctypes.c_int32, ctypes.c_char_p]
    
    ret = HCVnc_InputString(ctypes.c_int32(窗口序号), auto_encode(文本内容))
    return ret

# INT64 __stdcall HCVnc_OpenCapture(int windowIndex);
def HDVNC_开启截图(窗口序号: int) -> int:
    """
    开启VNC截图功能
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_OpenCapture = hd.HCVnc_OpenCapture
    HCVnc_OpenCapture.restype = ctypes.c_int64
    HCVnc_OpenCapture.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_OpenCapture(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCVnc_CloseCapture(int windowIndex);
def HDVNC_关闭截图(窗口序号: int) -> int:
    """
    关闭VNC截图功能
    
    Args:
        窗口序号: 窗口序号，每个窗口序号可以绑定一个虚拟机VNC端口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCVnc_CloseCapture = hd.HCVnc_CloseCapture
    HCVnc_CloseCapture.restype = ctypes.c_int64
    HCVnc_CloseCapture.argtypes = [ctypes.c_int32]
    
    ret = HCVnc_CloseCapture(ctypes.c_int32(窗口序号))
    return ret
