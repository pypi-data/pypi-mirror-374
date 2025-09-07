from .config import Config, ctypes
from .config import auto_encode

# 回调函数模板

# HD多线程_初始化流程回调
def update_ui_callback(windows_index: int, step_text: bytes, end1: int, pause1: int, thread_state1: int, end2: int, pause2: int, thread_state2: int) -> int:
    """
    更新UI回调函数
    
    Args:
        windows_index: 窗口索引
        step_text: 步骤文本 (bytes) - C接口传递的字节数组，需要解码为字符串使用
        end1: 结束状态1
        pause1: 暂停状态1
        thread_state1: 线程状态1
        end2: 结束状态2
        pause2: 暂停状态2
        thread_state2: 线程状态2
    
    Returns:
        int: 返回值
    """
    # C接口传递的char*在Python中是bytes，需要解码为字符串
    text_str = step_text.decode('utf-8', errors='ignore') if step_text else ""
    print(f"Update UI callback called with window index: {windows_index}, step text: {text_str}")
    return 0

def update_ui_callback_ex(windows_index: int, step_text: bytes, lparam: int, m_end1: int, m_pause1: int, thread_state1: int, m_end2: int, m_pause2: int, thread_state2: int) -> int:
    """
    更新UI回调函数扩展版
    
    Args:
        windows_index: 窗口索引
        step_text: 步骤文本 (bytes) - C接口传递的字节数组，需要解码为字符串使用
        lparam: 参数
        m_end1: 结束状态1
        m_pause1: 暂停状态1
        thread_state1: 线程状态1
        m_end2: 结束状态2
        m_pause2: 暂停状态2
        thread_state2: 线程状态2
    
    Returns:
        int: 返回值
    """
    # C接口传递的char*在Python中是bytes，需要解码为字符串
    text_str = step_text.decode('utf-8', errors='ignore') if step_text else ""
    print(f"Update UI callback EX called with window index: {windows_index}, step text: {text_str}")
    return 0

def login_callback(windows_index: int) -> int:
    """
    登录回调函数
    
    Args:
        windows_index: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"Login callback called with window index: {windows_index}")
    return 0

def first_callback(windows_index: int) -> int:
    """
    第一步回调函数
    
    Args:
        windows_index: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"First callback called with window index: {windows_index}")
    return 0

def second_callback(windows_index: int) -> int:
    """
    第二步回调函数
    
    Args:
        windows_index: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"Second callback called with window index: {windows_index}")
    return 0

def end_callback(windows_index: int) -> int:
    """
    结束回调函数
    
    Args:
        windows_index: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"End callback called with window index: {windows_index}")
    return 0

def restart_pre_callback(windows_index: int) -> int:
    """
    重启前回调函数
    
    Args:
        windows_index: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"Restart pre callback called with window index: {windows_index}")
    return 0

# HD多线程_初始化操作回调
def operation_end_callback(index: int) -> int:
    """
    操作结束回调函数
    
    Args:
        index: 索引
    
    Returns:
        int: 返回值
    """
    print(f"End callback called with index: {index}")
    return 0

def pause_callback(index: int) -> int:
    """
    暂停回调函数
    
    Args:
        index: 索引
    
    Returns:
        int: 返回值
    """
    print(f"Pause callback called with index: {index}")
    return 0

def recover_callback(index: int) -> int:
    """
    恢复回调函数
    
    Args:
        index: 索引
    
    Returns:
        int: 返回值
    """
    print(f"Recover callback called with index: {index}")
    return 0

# HD中控_心跳操作回调
def heart_callback(windows: int, checkType: int) -> int:
    """
    心跳检查回调函数
    
    Args:
        windows: 窗口索引
        checkType: 检查类型
    
    Returns:
        int: 返回值
    """
    print(f"heart callback called with window index: {windows}, type: {checkType}")
    return 0

# HD安装_打开回调
# typedef __int64(__stdcall *UIFUNTYPE)(__int32 窗口序号);
def open_callback(winIndex: int) -> int:
    """
    打开进程回调函数
    
    Args:
        winIndex: 窗口索引
    
    Returns:
        int: 返回值
    """
    print(f"open_callBack winIndex: {winIndex}")
    return 0

# HD安装_检查回调
# typedef __int64(__stdcall *UIFUNTYPE)(int 窗口序号, int 之前窗口序号, int 之前进程PID, int 提示值);
def check_callback(winIndex: int, preWinIndex: int, prePid: int, error: int) -> int:
    """
    检查进程回调函数
    
    Args:
        winIndex: 窗口索引
        preWinIndex: 之前窗口索引
        prePid: 之前进程PID
        error: 错误提示值
    
    Returns:
        int: 返回值
    """
    print(f"check_callBack winIndex: {winIndex}, preWinIndex: {preWinIndex}, prePid: {prePid}, error: {error}")
    return 0

#####################################################
## stdcall回调类型
## stdcall回调类型


