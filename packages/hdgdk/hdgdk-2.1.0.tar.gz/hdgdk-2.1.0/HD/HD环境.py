from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCEnv_GetMaxWindowNum();
def HD环境_获取最大多开数() -> int:
    """
    获取最大多开数
    
    Returns:
        int: 最大多开数，窗口序号不能大于等于这个返回值同时也不能小于0
    """
    hd = Config.get_hd()
    
    HCEnv_GetMaxWindowNum = hd.HCEnv_GetMaxWindowNum
    HCEnv_GetMaxWindowNum.restype = ctypes.c_int64
    HCEnv_GetMaxWindowNum.argtypes = []
    
    ret = HCEnv_GetMaxWindowNum()
    return ret

# INT64 __stdcall HCEnv_GetWinExIndex(int winIndex);
def HD环境_获取副窗口序号(窗口序号: int) -> int:
    """
    获取副窗口序号
    
    Args:
        窗口序号: 传递窗口序号，返回一个与当前指定的窗口序号的一个副窗口序号
    
    Returns:
        int: 副窗口序号，这个副窗口序号可以用于登录器的绑定和操作，相当于窗口序号的一个助手，做一些额外的事情，相当于一个窗口序号可以操作2个进程。如：窗口序号1，那么他返回的窗口扩展序号就是1+31也就是32序号
    """
    hd = Config.get_hd()
    
    HCEnv_GetWinExIndex = hd.HCEnv_GetWinExIndex
    HCEnv_GetWinExIndex.restype = ctypes.c_int64
    HCEnv_GetWinExIndex.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCEnv_GetWinExIndex(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCEnv_GetGlobalWinExIndex();
def HD环境_全局副窗口序号() -> int:
    """
    获取全局副窗口序号，这是一个全局的序号
    
    Returns:
        int: 全局副窗口序号，一个中控仅有一个，计算方式：0+31也就是这个全局序号为31，序号从0开始。用途：给当前中控分配一个助手，来控制一个进程来辅助中控做一些事情
    """
    hd = Config.get_hd()
    
    HCEnv_GetGlobalWinExIndex = hd.HCEnv_GetGlobalWinExIndex
    HCEnv_GetGlobalWinExIndex.restype = ctypes.c_int64
    HCEnv_GetGlobalWinExIndex.argtypes = []
    
    ret = HCEnv_GetGlobalWinExIndex()
    return ret

# INT64 __stdcall HCEnv_Init(int timeOut);
def HD环境_初始化(通讯超时时间: int = 10000) -> int:
    """
    HD插件环境加载，登录后，必须再次调用此接口，进程中控环境的初始化，否则无法使用其他接口
    
    Args:
        通讯超时时间: 通讯超时毫秒
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_Init = hd.HCEnv_Init
    HCEnv_Init.restype = ctypes.c_int64
    HCEnv_Init.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCEnv_Init(ctypes.c_int32(通讯超时时间))
    return ret

# INT64 __stdcall HCEnv_InitEx(int 通讯超时毫秒, int 通讯检测间隔毫秒, int 回调响应毫秒);
def HD环境_初始化Ex(通讯超时毫秒: int = 10000, 通讯检测间隔毫秒: int = 20, 回调响应毫秒: int = 5) -> int:
    """
    HD插件环境加载扩展版本，登录后，必须再次调用此接口，进程中控环境的初始化，否则无法使用其他接口
    
    Args:
        通讯超时毫秒: 通讯超时毫秒
        通讯检测间隔毫秒: 通讯检测间隔毫秒
        回调响应毫秒: 回调响应毫秒
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_InitEx = hd.HCEnv_InitEx
    HCEnv_InitEx.restype = ctypes.c_int64
    HCEnv_InitEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCEnv_InitEx(
        ctypes.c_int32(通讯超时毫秒),
        ctypes.c_int32(通讯检测间隔毫秒),
        ctypes.c_int32(回调响应毫秒)
    )
    return ret

# INT64 __stdcall HCEnv_Load(int 窗口序号, int 目标进程PID, int 游戏类型);
def HD环境_加载窗口(窗口序号: int, 目标进程PID: int, 游戏类型: int = 0) -> int:
    """
    HD插件环境加载
    
    Args:
        窗口序号: 窗口序号，从1开始
        目标进程PID: 目标进程PID
        游戏类型: 内置了游戏接口，每个游戏类型值不同，可以在工具上查看对应的值
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_Load = hd.HCEnv_Load
    HCEnv_Load.restype = ctypes.c_int64
    HCEnv_Load.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCEnv_Load(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int32(游戏类型)
    )
    return ret

# INT64 __stdcall HCEnv_LoadEx(int 窗口序号, int 目标进程PID, int 游戏类型, BOOL 是否响应回调);
def HD环境_加载窗口Ex(窗口序号: int, 目标进程PID: int, 游戏类型: int = 0, 是否响应回调: bool = False) -> int:
    """
    HD插件环境加载扩展版本，涉及到回调
    
    Args:
        窗口序号: 窗口序号，从1开始
        目标进程PID: 目标进程PID
        游戏类型: 内置了游戏接口，每个游戏类型值不同，可以在工具上查看对应的值
        是否响应回调: 是否响应回调，如果需要开启跨进程回调（如：send sendto recv recvfrom，心跳等内置插件设置的回调触发），请开启
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_LoadEx = hd.HCEnv_LoadEx
    HCEnv_LoadEx.restype = ctypes.c_int64
    HCEnv_LoadEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCEnv_LoadEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(目标进程PID),
        ctypes.c_int32(游戏类型),
        ctypes.c_bool(是否响应回调)
    )
    return ret

# INT64 __stdcall HCEnv_UnLoad(int 窗口序号);
def HD环境_卸载窗口(窗口序号: int) -> int:
    """
    HD插件环境卸载
    
    Args:
        窗口序号: 窗口序号，从1开始
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_UnLoad = hd.HCEnv_UnLoad
    HCEnv_UnLoad.restype = ctypes.c_int64
    HCEnv_UnLoad.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCEnv_UnLoad(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCEnv_UnLoadEx(int 窗口序号, BOOL bRecon);
def HD环境_卸载窗口Ex(窗口序号: int, 是否需要重连: bool = True) -> int:
    """
    HD插件环境卸载扩展版本
    
    Args:
        窗口序号: 窗口序号，从1开始
        是否需要重连: 是否还需要重连，默认是需要重连
    
    Returns:
        int: 返回值代码
    
    Note:
        调用这个接口需要先调用环境初始化模块中的初始化接口
        进程关闭一定要记得卸载窗口序号对应的窗口环境，以便于下次窗口序号使用
        1.没安装过插件的都不算重连窗口，全部当新窗口处理
        2.安装过插件的不管卸载环境还是崩溃或者重启窗口都可以重连窗口，一个序号只能绑定到一个窗口操作
    """
    hd = Config.get_hd()
    
    HCEnv_UnLoadEx = hd.HCEnv_UnLoadEx
    HCEnv_UnLoadEx.restype = ctypes.c_int64
    HCEnv_UnLoadEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCEnv_UnLoadEx(ctypes.c_int32(窗口序号), ctypes.c_bool(是否需要重连))
    return ret

# HD心跳回调 stdcall回调类型
# __int32(*HeartFunType)(__int32 窗口索引, __int32 type);
HD_HeartFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)

# INT64 __stdcall HCEnv_AttachHeart(int type, INT64 funCallbackAddr, int timeOutNor, int timeOut);
def HD环境_附加心跳(检测类型: int, 回调函数: HD_HeartFunType_stdcall = None, 正常心跳间隔: int = 10000, 检测超时: int = 10000) -> int:
    """
    给中控附加心跳
    
    Args:
        检测类型: 0->正常心跳（内部触发心跳回调+排序回调），1->通讯线程，2->主线程，3->卡屏，6->1+2+3
        回调函数: 当出现卡住或者掉线会触发相应的回调函数，并传递2个参数分别是->窗口索引和事件类型
        正常心跳间隔: 正常心跳间隔时间，超过此时间未检查到异常则触发正常心跳
        检测超时: 检测超时，超过此时间未发现改变则判定为卡住或掉线
    
    Returns:
        int: 返回值代码
    
    Note:
        检测主线程心跳需先HOOK主线程接口HC_HookMainThread
        回调函数返回值：1正常处理返回，0禁止当前窗口序号的心跳（永久无法恢复除非重启中控）
    """
    hd = Config.get_hd()
    
    HCEnv_AttachHeart = hd.HCEnv_AttachHeart
    HCEnv_AttachHeart.restype = ctypes.c_int64
    HCEnv_AttachHeart.argtypes = [
        ctypes.c_int32,
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    funCallback_ptr = ctypes.c_int64(ctypes.cast(HD_HeartFunType_stdcall(回调函数), ctypes.c_void_p).value) if 回调函数 else ctypes.c_int64(0)
    
    ret = HCEnv_AttachHeart(
        ctypes.c_int32(检测类型),
        funCallback_ptr,
        ctypes.c_int32(正常心跳间隔),
        ctypes.c_int32(检测超时)
    )
    return ret

# INT64 __stdcall HCEnv_SetScreenCheckHeart(int x, int y, int w, int h, int 最大次数, int 截屏前后间隔时间);
def HD环境_设置卡屏检查信息(客户端X坐标: int, 客户端Y坐标: int, 客户端宽度: int, 客户端高度: int, 检查次数: int, 截屏前后间隔时间: int = 1000) -> int:
    """
    当我们心跳检测指定了3或者6需要设置卡屏范围和卡屏检测次数，当大于这个次数就调用回调
    
    Args:
        客户端X坐标: 客户端X坐标
        客户端Y坐标: 客户端Y坐标
        客户端宽度: 客户端宽度
        客户端高度: 客户端高度
        检查次数: 检查次数
        截屏前后间隔时间: 检查间隔时间毫秒
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_SetScreenCheckHeart = hd.HCEnv_SetScreenCheckHeart
    HCEnv_SetScreenCheckHeart.restype = ctypes.c_int64
    HCEnv_SetScreenCheckHeart.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCEnv_SetScreenCheckHeart(
        ctypes.c_int32(客户端X坐标),
        ctypes.c_int32(客户端Y坐标),
        ctypes.c_int32(客户端宽度),
        ctypes.c_int32(客户端高度),
        ctypes.c_int32(检查次数),
        ctypes.c_int32(截屏前后间隔时间)
    )
    return ret

# INT64 __stdcall HCEnv_DetachHeart();
def HD环境_脱离心跳() -> int:
    """
    脱离中控附加的心跳检测
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_DetachHeart = hd.HCEnv_DetachHeart
    HCEnv_DetachHeart.restype = ctypes.c_int64
    HCEnv_DetachHeart.argtypes = []
    
    ret = HCEnv_DetachHeart()
    return ret

# INT64 __stdcall HCEnv_Debug(BOOL 是否调试);
def HD环境_调试模式(是否调试: bool = False) -> int:
    """
    设置导入接口为调试模式
    
    Args:
        是否调试: 当使用HDDebug.dll导入接口的时候就需要调用这个设置为调试模式（否则插件安装不成功）然后方可继续后面的一系列操作
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_Debug = hd.HCEnv_Debug
    HCEnv_Debug.restype = ctypes.c_int64
    HCEnv_Debug.argtypes = [
        ctypes.c_bool
    ]
    
    ret = HCEnv_Debug(ctypes.c_bool(是否调试))
    return ret


# INT64  __stdcall  HCEnv_MsgFile(BOOL 是否文件提示 = TRUE);
def HD环境_开启文件提示(是否开启文件提示: bool = True) -> int:
    """
   设置是否打开文件提示窗口
    Args:
        是否文件提示:是否开启文件提示日志
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()

    HCEnv_MsgFile = hd.HCEnv_MsgFile
    HCEnv_MsgFile.restype = ctypes.c_int64
    HCEnv_MsgFile.argtypes = [
        ctypes.c_bool
    ]

    ret = HCEnv_MsgFile(ctypes.c_bool(是否开启文件提示))
    return ret


# __int64 __stdcall  HCEnv_GetExcuteEnvInfo(__int32 窗口序号);
def HD环境_获取插件执行环境信息(窗口序号: int) -> int:
    """
   获取通讯插件所绑定的目标进程的执行线程环境信息
   通过HCEnv_GetRetJson返回字符串格式:序号-进程ID:进程ID,窗口序号,线程ID,执行状态|进程ID,窗口序号,线程ID,执行状态|进程ID,窗口序号,线程ID,执行状态 | ....
    Args:
        窗口序号:窗口序号 （从1开始）
    Returns:
        查看返回值表HD返回值表

    """

    hd = Config.get_hd()

    HCEnv_GetExcuteEnvInfo = hd.HCEnv_GetExcuteEnvInfo
    HCEnv_GetExcuteEnvInfo.restype = ctypes.c_int64
    HCEnv_GetExcuteEnvInfo.argtypes = [
        ctypes.c_int32
    ]

    ret = HCEnv_GetExcuteEnvInfo(ctypes.c_int32(窗口序号))
    return ret


# __int64 __stdcall HCEnv_ExitProcess(__int32 窗口序号);
def HD环境_关闭绑定进程(窗口序号: int) -> int:
    """
   关闭绑定进程
   内部实现可能是正常关闭也可能是强制关闭 至于是哪一种会根据实际情况动态调用
    Args:
        窗口序号:窗口序号 （从1开始）
    Returns:
        查看返回值表HD返回值表

    """

    hd = Config.get_hd()

    HCEnv_ExitProcess = hd.HCEnv_ExitProcess
    HCEnv_ExitProcess.restype = ctypes.c_int64
    HCEnv_ExitProcess.argtypes = [
        ctypes.c_int32
    ]

    ret = HCEnv_ExitProcess(ctypes.c_int32(窗口序号))
    return ret

# __int64 __stdcall  HCEnv_ProtectFun(__int64 funAddr,__int32 offset,__int32 size);
def HD环境_保护函数(funAddr,offset,size) -> int:
    """
   添加安全函数
    Args:
        int64 funAddr:函数地址
        int offset:基于函数地址+偏移
        int size:从(函数地址+偏移) 开始保护多少字节 最大字节数不得超过1024
    Returns:
        是否添加成功

    """
    funCallback_ptr = ctypes.c_int64(ctypes.cast(funAddr, ctypes.c_void_p).value) if funAddr else ctypes.c_int64(0)

    hd = Config.get_hd()

    HCEnv_ProtectFun = hd.HCEnv_ProtectFun
    HCEnv_ProtectFun.restype = ctypes.c_int64
    HCEnv_ProtectFun.argtypes = [
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_int32
    ]

    ret = HCEnv_ProtectFun(funCallback_ptr,ctypes.c_int32(offset),ctypes.c_int32(size))
    return ret

# INT64 __stdcall HCEnv_AddThread(int 窗口序号, int 线程ID, int bDebug);
def HD环境_添加线程(窗口序号: int, 线程ID: int, 是否是调试模式: int = 0) -> int:
    """
    添加线程环境
    
    Args:
        窗口序号: 窗口序号，从1开始
        线程ID: 当前线程ID
        是否是调试模式: 是否是调试模式，如果是那么线程ID可以任意指定
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCEnv_AddThread = hd.HCEnv_AddThread
    HCEnv_AddThread.restype = ctypes.c_int64
    HCEnv_AddThread.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]
    
    ret = HCEnv_AddThread(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(线程ID),
        ctypes.c_int32(是否是调试模式)
    )
    return ret

# INT64 __stdcall HCEnv_TestCALL_RetValue(int 窗口序号, INT64 rcx = 0, INT64 rdx = 0, INT64 r8 = 0, INT64 r9 = 0, INT64 lparam5 = 0, INT64 lparam6 = 0, BOOL 是否主线程调用 = FALSE);
def HD环境_测试通讯值(窗口序号: int, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, lparam5: int = 0, lparam6: int = 0, 是否主线程调用: bool = False) -> int:
    """
    测试是否通讯成功,返回单一值
    :param 窗口序号: 窗口序号 (从1开始)
    :param rcx: rcx
    :param rdx: rdx
    :param r8: r8
    :param r9: r9
    :param lparam5: lparam5
    :param lparam6: lparam6
    :param 是否主线程调用: 是否主线程调用
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_TestCALL_RetValue = hd.HCEnv_TestCALL_RetValue
    HCEnv_TestCALL_RetValue.restype = ctypes.c_int64
    HCEnv_TestCALL_RetValue.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int64,  # rcx
        ctypes.c_int64,  # rdx
        ctypes.c_int64,  # r8
        ctypes.c_int64,  # r9
        ctypes.c_int64,  # lparam5
        ctypes.c_int64,  # lparam6
        ctypes.c_bool    # 是否主线程调用
    ]

    # 调用C函数
    ret = HCEnv_TestCALL_RetValue(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(lparam5),
        ctypes.c_int64(lparam6),
        ctypes.c_bool(是否主线程调用)
    )
    return ret

# INT64 __stdcall HCEnv_TestCALL_RetArrayEx(int 窗口序号, int 线程ID, INT64 rcx = 0, INT64 rdx = 0, INT64 r8 = 0, INT64 r9 = 0, INT64 lparam5 = 0, INT64 lparam6 = 0, BOOL 是否主线程调用 = FALSE);
def HD环境_测试通讯字符串Ex(窗口序号: int, 线程ID: int, rcx: int = 0, rdx: int = 0, r8: int = 0, r9: int = 0, lparam5: int = 0, lparam6: int = 0, 是否主线程调用: bool = False) -> int:
    """
    测试是否通讯成功(扩展版本),返回json字符串
    :param 窗口序号: 窗口序号 (从1开始)
    :param 线程ID: 线程ID
    :param rcx: rcx
    :param rdx: rdx
    :param r8: r8
    :param r9: r9
    :param lparam5: lparam5
    :param lparam6: lparam6
    :param 是否主线程调用: 是否主线程调用
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_TestCALL_RetArrayEx = hd.HCEnv_TestCALL_RetArrayEx
    HCEnv_TestCALL_RetArrayEx.restype = ctypes.c_int64
    HCEnv_TestCALL_RetArrayEx.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # 线程ID
        ctypes.c_int64,  # rcx
        ctypes.c_int64,  # rdx
        ctypes.c_int64,  # r8
        ctypes.c_int64,  # r9
        ctypes.c_int64,  # lparam5
        ctypes.c_int64,  # lparam6
        ctypes.c_bool    # 是否主线程调用
    ]

    # 调用C函数
    ret = HCEnv_TestCALL_RetArrayEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(线程ID),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(lparam5),
        ctypes.c_int64(lparam6),
        ctypes.c_bool(是否主线程调用)
    )
    return ret


# INT64 __stdcall HCEnv_SetProcessType(int 进程位数);
def HD环境_设置目标进程位数(进程位数: int) -> int:
    """
    设置目标进程位数
    :param 进程位数: 32/64
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_SetProcessType = hd.HCEnv_SetProcessType
    HCEnv_SetProcessType.restype = ctypes.c_int64
    HCEnv_SetProcessType.argtypes = [
        ctypes.c_int32  # 进程位数
    ]

    # 调用C函数
    ret = HCEnv_SetProcessType(ctypes.c_int32(进程位数))
    return ret


# INT64 __stdcall HCEnv_SetProcessTypeEx(__int32 窗口序号, __int32 进程位数);
def HD环境_设置目标进程位数Ex(窗口序号: int, 进程位数: int) -> int:
    """
    指定某个序号绑定的进程位数(扩展版本)
    :param 窗口序号: 窗口序号
    :param 进程位数: 32/64
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_SetProcessTypeEx = hd.HCEnv_SetProcessTypeEx
    HCEnv_SetProcessTypeEx.restype = ctypes.c_int64
    HCEnv_SetProcessTypeEx.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32   # 进程位数
    ]

    # 调用C函数
    ret = HCEnv_SetProcessTypeEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(进程位数)
    )
    return ret

# HDHandleEventInfo
# Python 侧定义并确保对齐一致
class HDHandleEventInfo(ctypes.Structure):
    _pack_ = 8  # 对齐方式必须与 C++ 的 #pragma pack(push, 8) 一致
    _fields_ = [
        ("m_callType", ctypes.c_int32),
        ("_padding1", ctypes.c_byte*4),  # 填充4字节，保证后面的8字节对齐
        ("m_call", ctypes.c_int64),
        ("m_rcx", ctypes.c_int64),
        ("m_rdx", ctypes.c_int64),
        ("m_r8", ctypes.c_int64),
        ("m_r9", ctypes.c_int64),
        ("m_lparam5", ctypes.c_int64),
        ("m_lparam6", ctypes.c_int64),
        ("m_lparam7", ctypes.c_int64),
        ("m_lparam8", ctypes.c_int64),
        ("m_value", ctypes.c_int64),
        ("m_size", ctypes.c_int64),
        ("m_buffer", ctypes.c_char * 260),  # 定长字符数组
        ("m_buffer2", ctypes.c_char * 260),  # 定长字符数组
        ("m_pRetValue", ctypes.c_void_p),#值 单独
        ("m_pRetJson", ctypes.c_void_p)#字符串 返回
    ]

#print(ctypes.sizeof(HDHandleEventInfo))  # 应该等于C++中的sizeof(HDHandleEventInfo)
#HDHOOK send HOOK回调
#typedef __int32(__stdcall *HandleEventFunType)(__int32 窗口序号, __int32 插件序号, HDHandleEventInfo Info);
HD_HandleEventFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,HDHandleEventInfo)


# INT64 __stdcall HCEnv_SetHandleEventCallBack(INT64 funCallBack);
def HD环境_设置中控事件处理回调函数(事件处理回调函数: HD_HandleEventFunType_stdcall) -> int:
    """
    设置中控事件处理回调函数
    :param 事件处理回调函数: 事件处理回调函数(查看HD回调)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_SetHandleEventCallBack = hd.HCEnv_SetHandleEventCallBack
    HCEnv_SetHandleEventCallBack.restype = ctypes.c_int64
    HCEnv_SetHandleEventCallBack.argtypes = [
        ctypes.c_int64  # 事件处理回调函数
    ]
    #
    HD_HandleEventFunType_stdcall_Fun = HD_HandleEventFunType_stdcall(事件处理回调函数)
    # 正确获取回调函数的地址并转换为64位整数：使用ctypes.cast将回调对象转换为c_void_p，然后获取其数值并转为c_int64。
    HD_HandleEventFunType_stdcall_Fun_ptr = ctypes.c_int64(ctypes.cast(HD_HandleEventFunType_stdcall_Fun, ctypes.c_void_p).value) if HD_HandleEventFunType_stdcall_Fun else ctypes.c_int64(0)

    # 调用C函数
    ret = HCEnv_SetHandleEventCallBack(HD_HandleEventFunType_stdcall_Fun_ptr)
    return ret

# 定义关闭回调类型
# typedef __int32(__stdcall *ShutDownEventFunType)(__int32 code);
HD_ShutDownEventFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32, ctypes.c_int32)

def HD环境_设置关闭回调函数(py_callback: HD_ShutDownEventFunType_stdcall) -> int:
    """
    设置关闭回调函数(处理HD功能失效,内部自动关闭中控前的操作)
    Args:
        py_callback: Python函数，签名为 callback(code:int) -> int
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    HCEnv_SetShutDownCallBack = hd.HCEnv_SetShutDownCallBack
    HCEnv_SetShutDownCallBack.restype = ctypes.c_int64
    HCEnv_SetShutDownCallBack.argtypes = [ctypes.c_int64]

    c_callback = HD_ShutDownEventFunType_stdcall(py_callback) if py_callback else None
    callback_ptr = ctypes.c_int64(ctypes.cast(c_callback, ctypes.c_void_p).value) if c_callback else ctypes.c_int64(0)
    ret = HCEnv_SetShutDownCallBack(callback_ptr)
    return ret


# INT64 __stdcall HCEnv_SetCheckComItlTime(int 通讯检测间隔毫秒 = 20);
def HD环境_设置通讯检测间隔(通讯检测间隔毫秒: int = 20) -> int:
    """
    设置通讯检测间隔毫秒(丢弃)
    :param 通讯检测间隔毫秒: 默认就行,越小响应越快,CPU占用了越高(也可以调用HCEnv_InitEx 设置)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_SetCheckComItlTime = hd.HCEnv_SetCheckComItlTime
    HCEnv_SetCheckComItlTime.restype = ctypes.c_int64
    HCEnv_SetCheckComItlTime.argtypes = [
        ctypes.c_int32  # 通讯检测间隔毫秒
    ]

    # 调用C函数
    ret = HCEnv_SetCheckComItlTime(ctypes.c_int32(通讯检测间隔毫秒))
    return ret


# INT64 __stdcall HCEnv_SetCheckCallBackTime(int 回调响应毫秒 = 5);
def HD环境_设置回调响应间隔(回调响应毫秒: int = 5) -> int:
    """
    设置回调响应毫秒(丢弃)
    :param 回调响应毫秒: 默认就行,越小响应越快,CPU占用了越高(也可以调用HCEnv_InitEx 设置)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_SetCheckCallBackTime = hd.HCEnv_SetCheckCallBackTime
    HCEnv_SetCheckCallBackTime.restype = ctypes.c_int64
    HCEnv_SetCheckCallBackTime.argtypes = [
        ctypes.c_int32  # 回调响应毫秒
    ]

    # 调用C函数
    ret = HCEnv_SetCheckCallBackTime(ctypes.c_int32(回调响应毫秒))
    return ret


# INT64 __stdcall HCEnv_TerminateThread(int 窗口序号, int threadId, BOOL 是否操作锁 = TRUE);
def HD环境_强制结束线程(窗口序号: int, threadId: int, 是否操作锁: bool = True) -> int:
    """
    强制结束当前线程(可以在卸载环境后调用)
    :param 窗口序号: 指定当前强制关闭线程所操作的窗口序号
    :param threadId: 强制关闭的线程ID,调用此接口的线程不要和结束的线程是同一个(虽然内部有检查)
    :param 是否操作锁: 一般为了安全的强制关闭线程,必须为真, 否则会很有可能出现死锁的情况
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_TerminateThread = hd.HCEnv_TerminateThread
    HCEnv_TerminateThread.restype = ctypes.c_int64
    HCEnv_TerminateThread.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int32,  # threadId
        ctypes.c_bool    # 是否操作锁
    ]

    # 调用C函数
    ret = HCEnv_TerminateThread(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(threadId),
        ctypes.c_bool(是否操作锁)
    )
    return ret


# INT64 __stdcall HCEnv_TerminateThreadEx(int 窗口序号, INT64 threadHandle, BOOL 是否操作锁 = TRUE);
def HD环境_强制结束线程Ex(窗口序号: int, threadHandle: int, 是否操作锁: bool = True) -> int:
    """
    强制结束当前线程(可以在卸载环境后调用)(扩展版本)
    :param 窗口序号: 指定当前强制关闭线程所操作的窗口序号
    :param threadHandle: 强制关闭的线程句柄,调用此接口的线程不要和结束的线程是同一个(虽然有检查但是可能会崩溃)
    :param 是否操作锁: 一般为了安全的强制关闭线程,必须为真, 否则会很有可能出现死锁的情况
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HCEnv_TerminateThreadEx = hd.HCEnv_TerminateThreadEx
    HCEnv_TerminateThreadEx.restype = ctypes.c_int64
    HCEnv_TerminateThreadEx.argtypes = [
        ctypes.c_int32,  # 窗口序号
        ctypes.c_int64,  # threadHandle
        ctypes.c_bool    # 是否操作锁
    ]

    # 调用C函数
    ret = HCEnv_TerminateThreadEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(threadHandle),
        ctypes.c_bool(是否操作锁)
    )
    return ret


def HD环境_设置窗口排序信息(
    x: int,
    y: int,
    offsetx: int,
    offsety: int,
    cols: int,
    funCallback: ctypes.WINFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32) = None
) -> int:
    """
    接口说明:
        设置窗口排序信息

    函数原型:
        __int64  __stdcall  HCEnv_SetWindowsSortInfo(__int32 x, __int32 y, __int32 offsetx, __int32 offsety,__int32 cols, __int64 funCallbackAddr);

    参数说明:
        x: 屏幕左上角X开始
        y: 屏幕左上角Y开始
        offsetx: 每列左上角的X偏移
        offsety: 每行左上角的Y偏移
        cols: 列数 一排有多少个窗口 -1表示 一排无限窗口
        funCallback: 排序窗口回调  这个在触发正常心跳回调的时候会触发  必须HCEnv_AttachHeart附加心跳 才有效
            回调类型: typedef __int32(__stdcall *WindowsSortFunType)(__int32 窗口索引, __int32 pid, __int32 x, __int32 y);

    返回值:
        int: 见HD返回值表

    备注:
        无
    """
    hd = Config.get_hd()
    HCEnv_SetWindowsSortInfo = hd.HCEnv_SetWindowsSortInfo
    HCEnv_SetWindowsSortInfo.restype = ctypes.c_int64
    HCEnv_SetWindowsSortInfo.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int64]
    # 回调类型定义
    WindowsSortFunType = ctypes.WINFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)
    funCallback_ptr = ctypes.c_int64(ctypes.cast(WindowsSortFunType(funCallback), ctypes.c_void_p).value) if funCallback else ctypes.c_int64(0)
    ret = HCEnv_SetWindowsSortInfo(
        ctypes.c_int32(x),
        ctypes.c_int32(y),
        ctypes.c_int32(offsetx),
        ctypes.c_int32(offsety),
        ctypes.c_int32(cols),
        funCallback_ptr
    )
    return ret