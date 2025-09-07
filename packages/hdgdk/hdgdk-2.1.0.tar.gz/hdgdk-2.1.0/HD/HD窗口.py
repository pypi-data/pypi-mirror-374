from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCWIN_SortWindows(int offsetW, int offsetH, int width, int height);
def HD窗口_排序通讯窗口(水平偏移: int, 垂直偏移: int, 宽度: int, 高度: int) -> int:
    """
    排序安装过插件的进程
    
    Args:
        水平偏移: 水平偏移距离（2个相邻窗口的左上角的水平距离）
        垂直偏移: 垂直偏移距离（2个相邻窗口的左上角的垂直距离）
        宽度: 窗口宽度
        高度: 窗口高度
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    
    Note:
        安装过插件的进程一般表现为：
        1. 通讯过的窗口序号对应的进程PID（未被第二次初始化序号HCInject_Init）
        2. 卸载进程环境不会影响绑定过的进程排序（不能调用初始化序号HCInject_Init的前提下，也就是可以重连的情况下）
        3. HCInject_Init接口一旦调用，会取消所有关联（意味着不能重连），从而影响当前绑定的窗口PID，意味着新窗口即将打开
    """
    hd = Config.get_hd()
    
    HCWIN_SortWindows = hd.HCWIN_SortWindows
    HCWIN_SortWindows.restype = ctypes.c_int64
    HCWIN_SortWindows.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCWIN_SortWindows(
        ctypes.c_int32(水平偏移),
        ctypes.c_int32(垂直偏移),
        ctypes.c_int32(宽度),
        ctypes.c_int32(高度)
    )
    return ret

# INT64 __stdcall HCWIN_CamouflageProcess(char* runName, char* targetPath, int type);
def HD窗口_伪装进程(运行名称: str, 目标路径: str, 进程位数: int) -> int:
    """
    伪装进程（防止检查到实际的进程存在）
    
    Args:
        运行名称: 给伪装进程取的别名（任意前缀/后缀名字），如：hd.dat
        目标路径: 需要伪装的进程全路径（包含.exe），如：c:\\game.exe
        进程位数: 需要伪装的进程位数，32或64
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_CamouflageProcess = hd.HCWIN_CamouflageProcess
    HCWIN_CamouflageProcess.restype = ctypes.c_int64
    HCWIN_CamouflageProcess.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32]
    
    ret = HCWIN_CamouflageProcess(
        auto_encode(运行名称),
        auto_encode(目标路径),
        ctypes.c_int32(进程位数)
    )
    return ret

# INT64 __stdcall HCWIN_SetWindowState(INT64 hwnd, int type);
def HD窗口_设置窗口状态(窗口句柄: int, 状态类型: int) -> int:
    """
    设置或者操作窗口状态
    
    Args:
        窗口句柄: 窗口句柄，如果状态类型==18/19表示刷新桌面，这个时候窗口句柄可以为0
        状态类型: 窗口状态类型（1-19），-1/0表示不指定
            激活指定窗口(1) 显示最小化窗口,并不激活(2) 显示最小化窗口,同时激活窗口(3) 显示最大化窗口,同时激活窗口(4)
            显示窗口,但是不激活(5) 隐藏窗口(6) 显示窗口,并激活(7) 置顶窗口(8) 取消置顶窗口(9) 禁止窗口(10) 取消禁止窗口(11)
            恢复并激活窗口(12) 强制结束窗口所在的进程(13) 闪烁窗口(14) 窗口获取输入焦点(15) 发消息关闭指定窗口,不是强制关闭(16)
            强制刷新指定窗口(17) 强制刷新桌面窗口(18) 强制刷新桌面窗口+任务栏(19)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_SetWindowState = hd.HCWIN_SetWindowState
    HCWIN_SetWindowState.restype = ctypes.c_int64
    HCWIN_SetWindowState.argtypes = [ctypes.c_int64, ctypes.c_int32]
    
    ret = HCWIN_SetWindowState(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(状态类型)
    )
    return ret

# INT64 __stdcall HCWIN_SetWindowSize(INT64 hwnd, int width, int height, BOOL bCenter);
def HD窗口_设置窗口大小(窗口句柄: int, 宽度: int, 高度: int, 是否居中: bool = False) -> int:
    """
    设置窗口大小
    
    Args:
        窗口句柄: 窗口句柄
        宽度: 窗口宽度
        高度: 窗口高度
        是否居中: 窗口是否居中，默认False
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_SetWindowSize = hd.HCWIN_SetWindowSize
    HCWIN_SetWindowSize.restype = ctypes.c_int64
    HCWIN_SetWindowSize.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]
    
    ret = HCWIN_SetWindowSize(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(宽度),
        ctypes.c_int32(高度),
        ctypes.c_bool(是否居中)
    )
    return ret

# INT64 __stdcall HCWIN_MoveWindow(INT64 hwnd, int x, int y);
def HD窗口_窗口移动(窗口句柄: int, X坐标: int, Y坐标: int) -> int:
    """
    移动窗口
    
    Args:
        窗口句柄: 窗口句柄
        X坐标: 窗口x坐标
        Y坐标: 窗口y坐标
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_MoveWindow = hd.HCWIN_MoveWindow
    HCWIN_MoveWindow.restype = ctypes.c_int64
    HCWIN_MoveWindow.argtypes = [ctypes.c_int64, ctypes.c_int32, ctypes.c_int32]
    
    ret = HCWIN_MoveWindow(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(X坐标),
        ctypes.c_int32(Y坐标)
    )
    return ret

# INT64 __stdcall HCWIN_IsWow64Process(INT64 hwnd, int pid);
def HD窗口_是否64位进程(窗口句柄: int, 进程ID: int = 0) -> int:
    """
    判断窗口是否是64位进程
    
    Args:
        窗口句柄: 窗口句柄
        进程ID: 进程id，默认0
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_IsWow64Process = hd.HCWIN_IsWow64Process
    HCWIN_IsWow64Process.restype = ctypes.c_int64
    HCWIN_IsWow64Process.argtypes = [ctypes.c_int64, ctypes.c_int32]
    
    ret = HCWIN_IsWow64Process(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(进程ID)
    )
    return ret

# INT64 __stdcall HCWIN_GetWindowTitle(INT64 hwnd);
def HD窗口_获取窗口标题(窗口句柄: int) -> int:
    """
    获取窗口标题
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowTitle = hd.HCWIN_GetWindowTitle
    HCWIN_GetWindowTitle.restype = ctypes.c_int64
    HCWIN_GetWindowTitle.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_GetWindowTitle(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetWindowThreadProcessId(INT64 hwnd);
def HD窗口_获取窗口线程ID(窗口句柄: int) -> int:
    """
    获取目标窗口句柄的线程ID
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowThreadProcessId = hd.HCWIN_GetWindowThreadProcessId
    HCWIN_GetWindowThreadProcessId.restype = ctypes.c_int64
    HCWIN_GetWindowThreadProcessId.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_GetWindowThreadProcessId(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetWindowProcessId(INT64 hwnd);
def HD窗口_获取窗口进程ID(窗口句柄: int) -> int:
    """
    获取目标窗口句柄的进程ID
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowProcessId = hd.HCWIN_GetWindowProcessId
    HCWIN_GetWindowProcessId.restype = ctypes.c_int64
    HCWIN_GetWindowProcessId.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_GetWindowProcessId(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetWindowProcessPath(INT64 hwnd);
def HD窗口_获取窗口进程路径(窗口句柄: int) -> int:
    """
    获取目标窗口句柄的进程路径
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowProcessPath = hd.HCWIN_GetWindowProcessPath
    HCWIN_GetWindowProcessPath.restype = ctypes.c_int64
    HCWIN_GetWindowProcessPath.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_GetWindowProcessPath(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetWindowRect(INT64 hwnd, void* pRect);
def HD窗口_获取窗口位置(窗口句柄: int, 矩形指针=None) -> int:
    """
    获取窗口在屏幕上的位置
    
    Args:
        窗口句柄: 窗口句柄
        矩形指针: 指向RECT结构体地址（供C/C++调用，其他语言指定空），这个参数可以直接获取值，如果是其他语言可以HCEnv_GetRetJson获取字符串
    
    Returns:
        int: 返回值代码（查看HD返回值表），"left|top|right|bottom|"字符串从返回值json接口获取
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowRect = hd.HCWIN_GetWindowRect
    HCWIN_GetWindowRect.restype = ctypes.c_int64
    HCWIN_GetWindowRect.argtypes = [ctypes.c_int64, ctypes.c_void_p]
    
    ret = HCWIN_GetWindowRect(ctypes.c_int64(窗口句柄), 矩形指针)
    return ret

# INT64 __stdcall HCWIN_GetWindowClass(INT64 hwnd);
def HD窗口_获取窗口类名(窗口句柄: int) -> int:
    """
    获取目标窗口句柄的窗口类名
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowClass = hd.HCWIN_GetWindowClass
    HCWIN_GetWindowClass.restype = ctypes.c_int64
    HCWIN_GetWindowClass.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_GetWindowClass(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetWindowState(INT64 hwnd, int flag);
def HD窗口_获取窗口状态(窗口句柄: int, 状态标志: int) -> int:
    """
    获取目标窗口句柄的窗口状态
    
    Args:
        窗口句柄: 窗口句柄
        状态标志: 状态类型
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindowState = hd.HCWIN_GetWindowState
    HCWIN_GetWindowState.restype = ctypes.c_int64
    HCWIN_GetWindowState.argtypes = [ctypes.c_int64, ctypes.c_int32]
    
    ret = HCWIN_GetWindowState(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(状态标志)
    )
    return ret

# INT64 __stdcall HCWIN_GetSpecialWindow(int flag);
def HD窗口_获取特殊窗口(特殊标志: int) -> int:
    """
    获取特殊窗口 桌面 Shell_TrayWnd
    
    Args:
        特殊标志: 桌面(0), Shell_TrayWnd(1)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetSpecialWindow = hd.HCWIN_GetSpecialWindow
    HCWIN_GetSpecialWindow.restype = ctypes.c_int64
    HCWIN_GetSpecialWindow.argtypes = [ctypes.c_int32]
    
    ret = HCWIN_GetSpecialWindow(ctypes.c_int32(特殊标志))
    return ret

# INT64 __stdcall HCWIN_GetWindow(INT64 hwnd, int flag);
def HD窗口_获取窗口关联句柄(窗口句柄: int, 关联标志: int) -> int:
    """
    获取目标窗口句柄的关联窗口句柄
    
    Args:
        窗口句柄: 窗口句柄
        关联标志: 获取父窗口(0),获取第一个子窗口(1),获取第一个窗口(2),获取最后个窗口(3),获取下一个窗口(4),获取上一个窗口(5),获取拥有者窗口(6),获取顶层窗口(7)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetWindow = hd.HCWIN_GetWindow
    HCWIN_GetWindow.restype = ctypes.c_int64
    HCWIN_GetWindow.argtypes = [ctypes.c_int64, ctypes.c_int32]
    
    ret = HCWIN_GetWindow(
        ctypes.c_int64(窗口句柄),
        ctypes.c_int32(关联标志)
    )
    return ret

# INT64 __stdcall HCWIN_GetMousePointWindow();
def HD窗口_获取鼠标指向窗口句柄() -> int:
    """
    获取鼠标指向窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetMousePointWindow = hd.HCWIN_GetMousePointWindow
    HCWIN_GetMousePointWindow.restype = ctypes.c_int64
    HCWIN_GetMousePointWindow.argtypes = []
    
    ret = HCWIN_GetMousePointWindow()
    return ret

# INT64 __stdcall HCWIN_GetPointWindow(int x, int y);
def HD窗口_获取指向窗口句柄(X坐标: int, Y坐标: int) -> int:
    """
    获取指定坐标的窗口句柄
    
    Args:
        X坐标: x坐标
        Y坐标: y坐标
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetPointWindow = hd.HCWIN_GetPointWindow
    HCWIN_GetPointWindow.restype = ctypes.c_int64
    HCWIN_GetPointWindow.argtypes = [ctypes.c_int32, ctypes.c_int32]
    
    ret = HCWIN_GetPointWindow(
        ctypes.c_int32(X坐标),
        ctypes.c_int32(Y坐标)
    )
    return ret

# INT64 __stdcall HCWIN_GetForegroundWindow();
def HD窗口_获取顶层活动窗口句柄() -> int:
    """
    获取顶层活动窗口，可以获取到按键自带插件无法获取到的句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）或者句柄
    """
    hd = Config.get_hd()
    
    HCWIN_GetForegroundWindow = hd.HCWIN_GetForegroundWindow
    HCWIN_GetForegroundWindow.restype = ctypes.c_int64
    HCWIN_GetForegroundWindow.argtypes = []
    
    ret = HCWIN_GetForegroundWindow()
    return ret

# INT64 __stdcall HCWIN_GetForegroundFocus();
def HD窗口_获取顶层焦点窗口句柄() -> int:
    """
    获取顶层活动窗口中具有输入焦点的窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）或者句柄
    """
    hd = Config.get_hd()
    
    HCWIN_GetForegroundFocus = hd.HCWIN_GetForegroundFocus
    HCWIN_GetForegroundFocus.restype = ctypes.c_int64
    HCWIN_GetForegroundFocus.argtypes = []
    
    ret = HCWIN_GetForegroundFocus()
    return ret

# INT64 __stdcall HCWIN_SetForegroundFocus(INT64 hwnd);
def HD窗口_设置焦点到窗口(窗口句柄: int) -> int:
    """
    设置输入焦点到窗口
    
    Args:
        窗口句柄: 窗口句柄
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_SetForegroundFocus = hd.HCWIN_SetForegroundFocus
    HCWIN_SetForegroundFocus.restype = ctypes.c_int64
    HCWIN_SetForegroundFocus.argtypes = [ctypes.c_int64]
    
    ret = HCWIN_SetForegroundFocus(ctypes.c_int64(窗口句柄))
    return ret

# INT64 __stdcall HCWIN_GetClientSize(INT64 hwnd, void* pW, void* pH);
def HD窗口_获取窗口客户区域(窗口句柄: int, 宽度指针=None, 高度指针=None) -> int:
    """
    获取窗口客户区域的宽度和高度
    
    Args:
        窗口句柄: 窗口句柄
        宽度指针: 调用HD通用_获取最近返回Json获取字符串并自行解析
        高度指针: 调用HD通用_获取最近返回Json获取字符串并自行解析
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetClientSize = hd.HCWIN_GetClientSize
    HCWIN_GetClientSize.restype = ctypes.c_int64
    HCWIN_GetClientSize.argtypes = [ctypes.c_int64, ctypes.c_void_p, ctypes.c_void_p]
    
    ret = HCWIN_GetClientSize(
        ctypes.c_int64(窗口句柄),
        宽度指针,
        高度指针
    )
    return ret

# INT64 __stdcall HCWIN_GetClientRectInWindow(INT64 hwnd, void* pRect);
def HD窗口_获取窗口客户区域在屏幕(窗口句柄: int, 矩形指针=None) -> int:
    """
    获取窗口客户区域在屏幕上的位置
    
    Args:
        窗口句柄: 窗口句柄
        矩形指针: 调用HD通用_获取最近返回Json获取字符串并自行解析
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_GetClientRectInWindow = hd.HCWIN_GetClientRectInWindow
    HCWIN_GetClientRectInWindow.restype = ctypes.c_int64
    HCWIN_GetClientRectInWindow.argtypes = [ctypes.c_int64, ctypes.c_void_p]
    
    ret = HCWIN_GetClientRectInWindow(
        ctypes.c_int64(窗口句柄),
        矩形指针
    )
    return ret

# INT64 __stdcall HCWIN_FindWindowEx(INT64 parentHwnd, char* className, char* title, BOOL bType);
def HD窗口_查找窗口(父窗口句柄: int, 类名: str = None, 标题: str = None, 是否模糊: bool = True) -> int:
    """
    查找符合类名或者标题名的顶层可见窗口，如果指定了parent，则在parent的第一层子窗口中查找
    
    Args:
        父窗口句柄: 窗口的父窗口句柄（不指定则从桌面窗口开始搜索）
        类名: 窗口类名（不指定为None）
        标题: 窗口标题（不指定为None）
        是否模糊: True为模糊匹配，False为完全匹配
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_FindWindowEx = hd.HCWIN_FindWindowEx
    HCWIN_FindWindowEx.restype = ctypes.c_int64
    HCWIN_FindWindowEx.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
    
    类名字节 = auto_encode(类名) if 类名 else None
    标题字节 = auto_encode(标题) if 标题 else None
    
    ret = HCWIN_FindWindowEx(
        ctypes.c_int64(父窗口句柄),
        类名字节,
        标题字节,
        ctypes.c_bool(是否模糊)
    )
    return ret

# INT64 __stdcall HCWIN_FindTopWindow(char* className, char* title, BOOL bType);
def HD窗口_查找顶层窗口(类名: str = None, 标题: str = None, 是否模糊: bool = True) -> int:
    """
    查找顶层窗口句柄，父窗口句柄为NULL
    
    Args:
        类名: 窗口类名（不指定为None）
        标题: 窗口标题（不指定为None）
        是否模糊: True为模糊匹配，False为完全匹配
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_FindTopWindow = hd.HCWIN_FindTopWindow
    HCWIN_FindTopWindow.restype = ctypes.c_int64
    HCWIN_FindTopWindow.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
    
    类名字节 = auto_encode(类名) if 类名 else None
    标题字节 = auto_encode(标题) if 标题 else None
    
    ret = HCWIN_FindTopWindow(
        类名字节,
        标题字节,
        ctypes.c_bool(是否模糊)
    )
    return ret

# INT64 __stdcall HCWIN_EnumWindowByProcess(char* processName, char* className, char* title, int filter, BOOL bType);
def HD窗口_枚举查找窗口(进程名: str, 类名: str, 标题: str, 过滤器: int, 是否模糊: bool) -> int:
    """
    根据指定进程以及其它条件，枚举系统中符合条件的窗口
    
    Args:
        进程名: 进程名（如果是完全匹配要加.exe，如果是模糊匹配自行判断）
        类名: 窗口类名（不指定为None）
        标题: 窗口标题（不指定为None）
        过滤器: 1标题 2类名 4第一个PID 8检测是否有父窗口 16检查窗口句柄是否有效 32检索多PID 多个标识可以用|累加
        是否模糊: True为模糊匹配，False为完全匹配
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_EnumWindowByProcess = hd.HCWIN_EnumWindowByProcess
    HCWIN_EnumWindowByProcess.restype = ctypes.c_int64
    HCWIN_EnumWindowByProcess.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool]
    
    ret = HCWIN_EnumWindowByProcess(
        auto_encode(进程名),
        auto_encode(类名),
        auto_encode(标题),
        ctypes.c_int32(过滤器),
        ctypes.c_bool(是否模糊)
    )
    return ret

# INT64 __stdcall HCWIN_EnumWindowByProcessId(int pid, char* className, char* title, int filter, BOOL bType);
def HD窗口_枚举查找窗口Ex(进程ID: int, 类名: str, 标题: str, 过滤器: int, 是否模糊: bool) -> int:
    """
    根据指定进程以及其它条件，枚举系统中符合条件的窗口
    
    Args:
        进程ID: 进程ID
        类名: 窗口类名（不指定为None）
        标题: 窗口标题（不指定为None）
        过滤器: 标题 2类名 8检测是否有父窗口（也就是是否是顶级窗口）16检查窗口句柄是否有效 多个标识可以用|累加
        是否模糊: True为模糊匹配，False为完全匹配
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_EnumWindowByProcessId = hd.HCWIN_EnumWindowByProcessId
    HCWIN_EnumWindowByProcessId.restype = ctypes.c_int64
    HCWIN_EnumWindowByProcessId.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool]
    
    ret = HCWIN_EnumWindowByProcessId(
        ctypes.c_int32(进程ID),
        auto_encode(类名),
        auto_encode(标题),
        ctypes.c_int32(过滤器),
        ctypes.c_bool(是否模糊)
    )
    return ret

# INT64 __stdcall HCWIN_EnumProcess(char* processName, BOOL bType);
def HD窗口_枚举进程(进程名: str, 是否模糊: bool) -> int:
    """
    根据指定进程名，枚举系统中符合条件的进程PID
    
    Args:
        进程名: 进程名（如果是完全匹配要加.exe，如果是模糊匹配自行判断）
        是否模糊: True为模糊匹配，False为完全匹配
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_EnumProcess = hd.HCWIN_EnumProcess
    HCWIN_EnumProcess.restype = ctypes.c_int64
    HCWIN_EnumProcess.argtypes = [ctypes.c_char_p, ctypes.c_bool]
    
    ret = HCWIN_EnumProcess(
        auto_encode(进程名),
        ctypes.c_bool(是否模糊)
    )
    return ret

# INT64 __stdcall HCWIN_EnumWindow(INT64 parentHwnd, char* className, char* title, int filter, BOOL bType);
def HD窗口_枚举窗口(父窗口句柄: int, 类名: str, 标题: str, 过滤器: int, 是否模糊: bool, 是否子窗口: bool = False) -> int:
    """
    根据指定条件，枚举系统中符合条件的窗口，可以枚举到按键自带的无法枚举到的窗口
    
    Args:
        父窗口句柄: 父窗口句柄（0为顶层窗口）
        类名: 窗口类名（不指定为None）
        标题: 窗口标题（不指定为None）
        过滤器: 标题 2类名 8检测是否有父窗口（也就是是否是顶级窗口）16检查窗口句柄是否有效 多个标识可以用|累加
        是否模糊: True为模糊匹配，False为完全匹配
        是否子窗口: True为枚举子窗口，False为枚举顶级窗口
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    HCWIN_EnumWindow = hd.HCWIN_EnumWindow
    HCWIN_EnumWindow.restype = ctypes.c_int64
    HCWIN_EnumWindow.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool]
    
    ret = HCWIN_EnumWindow(
        ctypes.c_int64(父窗口句柄),
        auto_encode(类名),
        auto_encode(标题),
        ctypes.c_int32(过滤器),
        ctypes.c_bool(是否模糊),
        ctypes.c_bool(是否子窗口)
    )
    return ret