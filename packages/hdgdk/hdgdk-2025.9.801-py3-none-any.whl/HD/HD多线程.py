from .config import Config, ctypes
from .config import auto_encode

# HD多线程流程回调
# __int64(__stdcall *FUNTYPE )(__int32 windowsIndex);
HD_ProcessFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32)

# HD多线程操作回调
# __int64(__stdcall *FUNTYPE )(__int32 index);
HD_OperationFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32)

# HD多线程消息回调X64
# typedef __int64(__stdcall *MSGFUNTYPE )(WPARAM wparam,LPARAM lparam);
HD_MsgFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_void_p, ctypes.c_void_p)

# HD多线程UI回调
# typedef __int64(__stdcall *UIFUNTYPE)(__int32 windowsIndex, char *stepText, BOOL end1, BOOL pause1, __int32 threadState1, BOOL m_end2, BOOL m_pause2, __int32 threadState2);
HD_UiFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)

# HD多线程UIEx回调
# typedef __int64(__stdcall *UIFUNTYPE)(__int32 windowsIndex, char *stepText, void* lparam,  BOOL end1, BOOL pause1, __int32 threadState1, BOOL m_end2, BOOL m_pause2, __int32 threadState2);
HD_UiExFunType_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)

UI回调Fun = None
登录回调Fun = None
第一执行回调Fun = None
第二执行回调Fun = None
结束回调Fun = None
重启前回调Fun = None

# INT64 __stdcall HCMT_InitProcess(INT64 hwnd, void* updateUICallBack, void* loginCallBack, void* firstCallBack, void* secondCallBack, void* endCallBack, void* restartPreCallBack);
def HD多线程_初始化流程回调(窗口主句柄: int, UI回调: HD_UiFunType_stdcall, 登录回调: HD_ProcessFunType_stdcall, 第一执行回调: HD_ProcessFunType_stdcall, 第二执行回调: HD_ProcessFunType_stdcall, 结束回调: HD_ProcessFunType_stdcall, 重启前回调: HD_ProcessFunType_stdcall) -> int:
    """
    初始化多线程设置相关流程回调
    
    Args:
        窗口主句柄: 中控UI的窗口主句柄，内部会HOOK窗口过程
        UI回调: UI回调函数指针
        登录回调: 登录回调函数指针
        第一执行回调: 第一执行回调函数指针，注意：内部应该写成循环并配合HCMT_Sleep()和HCMT_IsRunning()，不要主动返回执行回调(return 1;)，应该调用接口内部结束或者其他操作
        第二执行回调: 第二执行回调函数指针，注意：内部应该写成循环并配合HCMT_Sleep()和HCMT_IsRunning()，不要主动返回执行回调(return 1;)，应该调用接口内部结束或者其他操作
        结束回调: 结束回调函数指针
        重启前回调: 重启前回调函数指针
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_InitProcess = hd.HCMT_InitProcess
    HCMT_InitProcess.restype = ctypes.c_int64
    HCMT_InitProcess.argtypes = [
        ctypes.c_int64,
        HD_UiFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
    ]
    
    global UI回调Fun, 登录回调Fun, 第一执行回调Fun, 第二执行回调Fun, 结束回调Fun, 重启前回调Fun
    UI回调Fun = HD_UiFunType_stdcall(UI回调)
    登录回调Fun = HD_ProcessFunType_stdcall(登录回调)
    第一执行回调Fun = HD_ProcessFunType_stdcall(第一执行回调)
    第二执行回调Fun = HD_ProcessFunType_stdcall(第二执行回调)
    结束回调Fun = HD_ProcessFunType_stdcall(结束回调)
    重启前回调Fun = HD_ProcessFunType_stdcall(重启前回调)
    
    ret = HCMT_InitProcess(
        ctypes.c_int64(窗口主句柄),
        UI回调Fun,
        登录回调Fun,
        第一执行回调Fun,
        第二执行回调Fun,
        结束回调Fun,
        重启前回调Fun
    )
    return ret

# INT64 __stdcall HCMT_InitProcessEx(INT64 hwnd, void* updateUICallBackEx, void* loginCallBack, void* firstCallBack, void* secondCallBack, void* endCallBack, void* restartPreCallBack, void* lparam);
def HD多线程_初始化流程回调Ex(窗口主句柄: int, UI回调: HD_UiExFunType_stdcall, 登录回调: HD_ProcessFunType_stdcall, 第一执行回调: HD_ProcessFunType_stdcall, 第二执行回调: HD_ProcessFunType_stdcall, 结束回调: HD_ProcessFunType_stdcall, 重启前回调: HD_ProcessFunType_stdcall, 额外参数: ctypes.c_void_p) -> int:
    """
    初始化多线程扩展版本设置相关流程回调
    
    Args:
        窗口主句柄: 中控UI的窗口主句柄，内部会HOOK窗口过程
        UI回调: UI回调函数指针
        登录回调: 登录回调函数指针
        第一执行回调: 第一执行回调函数指针，注意：内部应该写成循环并配合HCMT_Sleep()和HCMT_IsRunning()，不要主动返回执行回调(return 1;)，应该调用接口内部结束或者其他操作
        第二执行回调: 第二执行回调函数指针，注意：内部应该写成循环并配合HCMT_Sleep()和HCMT_IsRunning()，不要主动返回执行回调(return 1;)，应该调用接口内部结束或者其他操作
        结束回调: 结束回调函数指针
        重启前回调: 重启前回调函数指针
        额外参数: 绑定一个全局参数，一般我们指定为一个UI对象地址
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_InitProcessEx = hd.HCMT_InitProcessEx
    HCMT_InitProcessEx.restype = ctypes.c_int64
    HCMT_InitProcessEx.argtypes = [
        ctypes.c_int64,
        HD_UiExFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        HD_ProcessFunType_stdcall,
        ctypes.c_void_p
    ]
    
    global UI回调Fun, 登录回调Fun, 第一执行回调Fun, 第二执行回调Fun, 结束回调Fun, 重启前回调Fun
    UI回调Fun = HD_UiExFunType_stdcall(UI回调)
    登录回调Fun = HD_ProcessFunType_stdcall(登录回调)
    第一执行回调Fun = HD_ProcessFunType_stdcall(第一执行回调)
    第二执行回调Fun = HD_ProcessFunType_stdcall(第二执行回调)
    结束回调Fun = HD_ProcessFunType_stdcall(结束回调)
    重启前回调Fun = HD_ProcessFunType_stdcall(重启前回调)
    
    ret = HCMT_InitProcessEx(
        ctypes.c_int64(窗口主句柄),
        UI回调Fun,
        登录回调Fun,
        第一执行回调Fun,
        第二执行回调Fun,
        结束回调Fun,
        重启前回调Fun,
        额外参数
    )
    return ret

结束绑定回调Fun = None
暂停绑定回调Fun = None
恢复绑定回调Fun = None

# INT64 __stdcall HCMT_InitOperate(void* endBindCallBack, void* pauseBindCallBack, void* recoverBindCallBack);
def HD多线程_初始化操作回调(结束绑定回调: HD_OperationFunType_stdcall, 暂停绑定回调: HD_OperationFunType_stdcall, 恢复绑定回调: HD_OperationFunType_stdcall) -> int:
    """
    初始化多线程结束/暂停/恢复状态的操作回调
    
    Args:
        结束绑定回调: 结束绑定回调函数指针
        暂停绑定回调: 暂停绑定回调函数指针
        恢复绑定回调: 恢复绑定回调函数指针
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_InitOperate = hd.HCMT_InitOperate
    HCMT_InitOperate.restype = ctypes.c_int64
    HCMT_InitOperate.argtypes = [
        HD_OperationFunType_stdcall,
        HD_OperationFunType_stdcall,
        HD_OperationFunType_stdcall
    ]
    
    global 结束绑定回调Fun, 暂停绑定回调Fun, 恢复绑定回调Fun
    结束绑定回调Fun = HD_OperationFunType_stdcall(结束绑定回调)
    暂停绑定回调Fun = HD_OperationFunType_stdcall(暂停绑定回调)
    恢复绑定回调Fun = HD_OperationFunType_stdcall(恢复绑定回调)
    
    ret = HCMT_InitOperate(
        结束绑定回调Fun,
        暂停绑定回调Fun,
        恢复绑定回调Fun
    )
    return ret

# INT64 __stdcall HCMT_RegisterMessage(int msg, void* msgCallBack);
def HD多线程_注册消息回调(自定义消息整数值: int, 消息回调: HD_MsgFunType_stdcall) -> int:
    """
    注册窗口消息
    
    Args:
        自定义消息整数值: 自定义消息整数值，规定值大于等于41124
        消息回调: 消息回调函数指针
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_RegisterMessage = hd.HCMT_RegisterMessage
    HCMT_RegisterMessage.restype = ctypes.c_int64
    HCMT_RegisterMessage.argtypes = [
        ctypes.c_int32,
        ctypes.c_void_p
    ]
    
    消息回调Fun = HD_MsgFunType_stdcall(消息回调)
    消息回调Fun_ptr = ctypes.cast(消息回调Fun, ctypes.c_void_p).value if 消息回调Fun else ctypes.c_void_p(0)
    
    ret = HCMT_RegisterMessage(
        ctypes.c_int32(自定义消息整数值),
        消息回调Fun_ptr
    )
    return ret

# INT64 __stdcall HCMT_MsgSend(int msg, void* wparam, void* lparam);
def HD多线程_同步发送消息(自定义消息整数值: int, 自定义参数1: int, 自定义参数2: int) -> int:
    """
    发送消息同步
    
    Args:
        自定义消息整数值: 消息整数值
        自定义参数1: 自定义参数1
        自定义参数2: 自定义参数2
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgSend = hd.HCMT_MsgSend
    HCMT_MsgSend.restype = ctypes.c_int64
    HCMT_MsgSend.argtypes = [
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.c_void_p
    ]
    
    ret = HCMT_MsgSend(
        ctypes.c_int32(自定义消息整数值),
        ctypes.cast(自定义参数1, ctypes.c_void_p),
        ctypes.cast(自定义参数2, ctypes.c_void_p)
    )
    return ret

# INT64 __stdcall HCMT_MsgPost(int msg, void* wparam, void* lparam);
def HD多线程_异步发送消息(自定义消息整数值: int, 自定义参数1: int, 自定义参数2: int) -> int:
    """
    发送消息异步
    
    Args:
        自定义消息整数值: 消息整数值
        自定义参数1: 自定义参数1
        自定义参数2: 自定义参数2
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgPost = hd.HCMT_MsgPost
    HCMT_MsgPost.restype = ctypes.c_int64
    HCMT_MsgPost.argtypes = [
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.c_void_p
    ]
    
    ret = HCMT_MsgPost(
        ctypes.c_int32(自定义消息整数值),
        ctypes.cast(自定义参数1, ctypes.c_void_p),
        ctypes.cast(自定义参数2, ctypes.c_void_p)
    )
    return ret

# INT64 __stdcall HCMT_MsgStart(int windowsIndex, BOOL bAsyn);
def HD多线程_开启窗口Msg(窗口序号: int, 是否异步发送: bool = False) -> int:
    """
    通过消息开启窗口操作
    
    Args:
        窗口序号: 窗口序号
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgStart = hd.HCMT_MsgStart
    HCMT_MsgStart.restype = ctypes.c_int64
    HCMT_MsgStart.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgStart(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否异步发送)
    )
    return ret

# INT64 __stdcall HCMT_MsgStop(int windowsIndex, BOOL bAsyn);
def HD多线程_停止窗口Msg(窗口序号: int, 是否异步发送: bool = False) -> int:
    """
    通过消息停止窗口操作
    
    Args:
        窗口序号: 窗口序号
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgStop = hd.HCMT_MsgStop
    HCMT_MsgStop.restype = ctypes.c_int64
    HCMT_MsgStop.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgStop(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否异步发送)
    )
    return ret

# INT64 __stdcall HCMT_MsgReStart(int windowsIndex, BOOL bAsyn);
def HD多线程_重启窗口Msg(窗口序号: int, 是否异步发送: bool = False) -> int:
    """
    通过消息重启窗口操作
    
    Args:
        窗口序号: 窗口序号
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgReStart = hd.HCMT_MsgReStart
    HCMT_MsgReStart.restype = ctypes.c_int64
    HCMT_MsgReStart.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgReStart(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否异步发送)
    )
    return ret

# INT64 __stdcall HCMT_MsgReStartEx(int windowsIndex, BOOL bUnload, BOOL bAsyn);
def HD多线程_重启窗口MsgEx(窗口序号: int, 是否卸载环境: bool = True, 是否重连: bool = True,是否异步发送: bool = False) -> int:
    """
    通过消息重启窗口操作扩展版
    
    Args:
        窗口序号: 窗口序号
        是否卸载环境: 是否卸载环境
        是否重连: 是否重连
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgReStartEx = hd.HCMT_MsgReStartEx
    HCMT_MsgReStartEx.restype = ctypes.c_int64
    HCMT_MsgReStartEx.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool,
        ctypes.c_bool,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgReStartEx(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否卸载环境),
        ctypes.c_bool(是否重连),
        ctypes.c_bool(是否异步发送)
    )
    return ret


# INT64 __stdcall HCMT_MsgUpdateUI(int windowsIndex, BOOL bAsyn);
def HD多线程_更新UI(窗口序号: int, 是否异步发送: bool = False) -> int:
    """
    通过消息触发UI回调，并传递线程状态信息和日志操作信息给UI回调
    
    Args:
        窗口序号: 窗口序号
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgUpdateUI = hd.HCMT_MsgUpdateUI
    HCMT_MsgUpdateUI.restype = ctypes.c_int64
    HCMT_MsgUpdateUI.argtypes = [
        ctypes.c_int32,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgUpdateUI(
        ctypes.c_int32(窗口序号),
        ctypes.c_bool(是否异步发送)
    )
    return ret

# INT64 __stdcall HCMT_MsgStepText(int windowsIndex, char* text, BOOL bAsyn);
def HD多线程_发送文本(窗口序号: int, 文本: str, 是否异步发送: bool = False) -> int:
    """
    通过消息触发UI回调，并传递线程状态信息和日志操作信息给UI回调
    
    Args:
        窗口序号: 窗口序号
        文本: 要发送的文本字符串
        是否异步发送: 是否异步发送
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_MsgStepText = hd.HCMT_MsgStepText
    HCMT_MsgStepText.restype = ctypes.c_int64
    HCMT_MsgStepText.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_bool
    ]
    
    ret = HCMT_MsgStepText(
        ctypes.c_int32(窗口序号),
        auto_encode(文本),
        ctypes.c_bool(是否异步发送)
    )
    return ret

# INT64 __stdcall HCMT_SetAllPause();
def HD多线程_所有窗口暂停() -> int:
    """
    设置所有窗口暂停
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetAllPause = hd.HCMT_SetAllPause
    HCMT_SetAllPause.restype = ctypes.c_int64
    HCMT_SetAllPause.argtypes = []
    
    ret = HCMT_SetAllPause()
    return ret

# INT64 __stdcall HCMT_GetState(int index);
def HD多线程_获取线程状态值(主副序号: int) -> int:
    """
    获取主副序号对应的线程的状态值
    
    Args:
        主副序号: 主副序号
    
    Returns:
        int: 状态值
    """
    hd = Config.get_hd()
    
    HCMT_GetState = hd.HCMT_GetState
    HCMT_GetState.restype = ctypes.c_int64
    HCMT_GetState.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_GetState(ctypes.c_int32(主副序号))
    return ret

# char* __stdcall HCMT_GetStateString(int threadState);
def HD多线程_获取线程状态说明(状态值: int) -> str:
    """
    获取状态整数值对应的字符串
    
    Args:
        状态值: 是HD多线程_获取线程状态值返回的值
    
    Returns:
        str: 状态说明字符串
    """
    hd = Config.get_hd()
    
    HCMT_GetStateString = hd.HCMT_GetStateString
    HCMT_GetStateString.restype = ctypes.c_char_p
    HCMT_GetStateString.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_GetStateString(ctypes.c_int32(状态值))
    # C接口返回的char*需要解码为Python字符串
    if ret:
        return ret.decode('utf-8', errors='ignore')
    else:
        return ""

# INT64 __stdcall HCMT_Start(int windowsIndex);
def HD多线程_开启窗口(窗口序号: int) -> int:
    """
    直接开启窗口操作
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_Start = hd.HCMT_Start
    HCMT_Start.restype = ctypes.c_int64
    HCMT_Start.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_Start(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMT_SetAllRecover();
def HD多线程_所有窗口恢复() -> int:
    """
    设置所有窗口恢复
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetAllRecover = hd.HCMT_SetAllRecover
    HCMT_SetAllRecover.restype = ctypes.c_int64
    HCMT_SetAllRecover.argtypes = []
    
    ret = HCMT_SetAllRecover()
    return ret

# INT64 __stdcall HCMT_SetAllStop();
def HD多线程_所有窗口停止() -> int:
    """
    设置所有窗口停止
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetAllStop = hd.HCMT_SetAllStop
    HCMT_SetAllStop.restype = ctypes.c_int64
    HCMT_SetAllStop.argtypes = []
    
    ret = HCMT_SetAllStop()
    return ret

# INT64 __stdcall HCMT_SetPause(int windowsIndex);
def HD多线程_暂停窗口(窗口序号: int) -> int:
    """
    设置窗口暂停
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetPause = hd.HCMT_SetPause
    HCMT_SetPause.restype = ctypes.c_int64
    HCMT_SetPause.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_SetPause(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMT_SetPauseEx(int index);
def HD多线程_暂停线程(线程序号: int) -> int:
    """
    设置主副序号对应的线程暂停
    
    Args:
        线程序号: 线程序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetPauseEx = hd.HCMT_SetPauseEx
    HCMT_SetPauseEx.restype = ctypes.c_int64
    HCMT_SetPauseEx.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_SetPauseEx(ctypes.c_int32(线程序号))
    return ret

# INT64 __stdcall HCMT_SetRecover(int windowsIndex);
def HD多线程_恢复窗口(窗口序号: int) -> int:
    """
    设置窗口恢复
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetRecover = hd.HCMT_SetRecover
    HCMT_SetRecover.restype = ctypes.c_int64
    HCMT_SetRecover.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_SetRecover(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMT_SetRecoverEx(int index);
def HD多线程_恢复线程(线程序号: int) -> int:
    """
    设置主副序号对应的线程恢复
    
    Args:
        线程序号: 线程序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetRecoverEx = hd.HCMT_SetRecoverEx
    HCMT_SetRecoverEx.restype = ctypes.c_int64
    HCMT_SetRecoverEx.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_SetRecoverEx(ctypes.c_int32(线程序号))
    return ret

# INT64 __stdcall HCMT_SetStop(int windowsIndex);
def HD多线程_停止窗口(窗口序号: int) -> int:
    """
    设置窗口停止
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_SetStop = hd.HCMT_SetStop
    HCMT_SetStop.restype = ctypes.c_int64
    HCMT_SetStop.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_SetStop(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMT_IsRunning();
def HD多线程_是否运行中() -> int:
    """
    在第一第二回调里面调用，检查当前线程是否结束
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_IsRunning = hd.HCMT_IsRunning
    HCMT_IsRunning.restype = ctypes.c_int64
    HCMT_IsRunning.argtypes = []
    
    ret = HCMT_IsRunning()
    return ret

# INT64 __stdcall HCMT_IsCanStart(int windowsIndex);
def HD多线程_是否能开启(窗口序号: int) -> int:
    """
    在第一第二回调里面调用，检查当前线程是否结束
    
    Args:
        窗口序号: 窗口序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_IsCanStart = hd.HCMT_IsCanStart
    HCMT_IsCanStart.restype = ctypes.c_int64
    HCMT_IsCanStart.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_IsCanStart(ctypes.c_int32(窗口序号))
    return ret

# INT64 __stdcall HCMT_IsPause(int index);
def HD多线程_是否暂停(线程序号: int) -> int:
    """
    判断主副序号对应的线程是否是已被暂停状态
    
    Args:
        线程序号: 线程序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_IsPause = hd.HCMT_IsPause
    HCMT_IsPause.restype = ctypes.c_int64
    HCMT_IsPause.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_IsPause(ctypes.c_int32(线程序号))
    return ret

# INT64 __stdcall HCMT_IsStop(int index);
def HD多线程_是否停止(线程序号: int) -> int:
    """
    判断主副序号对应的线程是否是已被结束状态
    
    Args:
        线程序号: 线程序号
    
    Returns:
        int: 返回值代码
    """
    hd = Config.get_hd()
    
    HCMT_IsStop = hd.HCMT_IsStop
    HCMT_IsStop.restype = ctypes.c_int64
    HCMT_IsStop.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_IsStop(ctypes.c_int32(线程序号))
    return ret

# INT64 __stdcall HCMT_Sleep(int mis);
def HD多线程_延迟(毫秒延迟: int) -> int:
    """
    延迟函数，自带暂停/结束/恢复检查
    
    Args:
        毫秒延迟: 毫秒延迟
    
    Returns:
        int: 返回值代码，1：正常，2：线程结束，3：线程被暂停过
    """
    hd = Config.get_hd()
    
    HCMT_Sleep = hd.HCMT_Sleep
    HCMT_Sleep.restype = ctypes.c_int64
    HCMT_Sleep.argtypes = [
        ctypes.c_int32
    ]
    
    ret = HCMT_Sleep(ctypes.c_int32(毫秒延迟))
    return ret


