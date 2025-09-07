from .config import Config, ctypes
from .config import auto_encode

# INT64 __stdcall HCHD_LoadDrv();
def HD驱动_安装() -> int:
    """
    加载HD驱动
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_LoadDrv
    func.restype = ctypes.c_int64
    func.argtypes = []
    
    return func()

# INT64 __stdcall HCHD_LoadDrv2(int type);
def HD驱动_安装2(驱动类型: int = 0) -> int:
    """
    云下发加载驱动或组件（可指定驱动序号加载不同版本的驱动）
    
    Args:
        驱动类型: 驱动序号，-1正式驱动，0定制版本，1备用版本，2~6为其他组件，默认0
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_LoadDrv2
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(驱动类型)

# INT64 __stdcall HCHD_InitFastRW();
def HD驱动_初始化快速读写() -> int:
    """
    初始化HD驱动快速读写(一般在HD安装驱动接口后的下一句就开始初始化)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    func = hd.HCHD_InitFastRW
    func.restype = ctypes.c_int64
    func.argtypes = []

    return func()

# __int64 __stdcall HCHD_InjectX86X64(char* injectExeName, __int32 dllBits, __int32 injectMode, __int32 memoryHide, PVOID injectData, __int32 injectSize);
def HD驱动_无痕注入DLL(injectExeName: str, dllBits: int, injectMode: int, memoryHide: int, injectData: bytes, injectSize: int) -> int:
    """
    把DLL注入到指定进程中
    
    Args:
        injectExeName: 进程名(如:Game.exe)
        dllBits: 进程位(32/64)
        injectMode: 注入模式(0/1/2),一般0,1模式就行,2用于steam游戏
        memoryHide: 内存保护模式(0/1/2)
        injectData: 注入数据缓冲区首地址 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
        injectSize: 注入数据缓冲区大小(单位:字节)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    func = hd.HCHD_InjectX86X64
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]

    return func(
        auto_encode(injectExeName),
        dllBits, injectMode, memoryHide,
        ctypes.c_char_p(injectData), injectSize
    )

# __int64 __stdcall HCHD_InstallPlugX86(char* injectExeName, __int32 injectMode, __int32 memoryHide);
def HD驱动_无痕安装插件X86(injectExeName: str, injectMode: int, memoryHide: int) -> int:
    """
    安装HD插件到指定进程中(X86版本)
    
    Args:
        injectExeName: 进程名(如:Game.exe)
        injectMode: 注入模式(0/1/2),一般0,1模式就行,2用于steam游戏
        memoryHide: 内存保护模式(0/1/2)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    func = hd.HCHD_InstallPlugX86
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]

    return func(auto_encode(injectExeName), injectMode, memoryHide)

# __int64 __stdcall HCHD_InstallPlugX64(char* injectExeName, __int32 injectMode, __int32 memoryHide);
def HD驱动_无痕安装插件X64(injectExeName: str, injectMode: int, memoryHide: int) -> int:
    """
    安装HD插件到指定进程中(X64版本)
    
    Args:
        injectExeName: 进程名(如:Game.exe)
        injectMode: 注入模式(0/1/2),一般0,1模式就行,2用于steam游戏
        memoryHide: 内存保护模式(0/1/2)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()

    func = hd.HCHD_InstallPlugX64
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]

    return func(auto_encode(injectExeName), injectMode, memoryHide)

# INT64 __stdcall HCHD_UnInstallPlug();
def HD驱动_卸载插件() -> int:
    """
    卸载插件（并不是从进程中卸载，而是清除了下一次进程打开的时候安装插件的缓存）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_UnInstallPlug
    func.restype = ctypes.c_int64
    func.argtypes = []
    
    return func()


#  __int64 __stdcall  HCHD_SetMMTrackType(__int32 type);
def HD驱动_设置鼠标轨迹(type: int) -> int:
    """
    前台鼠标移动点击

    Args:
        type:轨迹类型 -1或0 表示无轨迹  1 表示随机轨迹 2表示直线轨迹 3表示直线波动轨迹(过检测强)  具体的轨迹效果可以参考:后台键鼠的轨迹

    Returns:
        int: 返回值代码（查看HD返回值表） 返回之前的轨迹类型
    """
    hd = Config.get_hd()

    func = hd.HCHD_SetMMTrackType
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]

    return func(type)



# INT64 __stdcall HCHD_MousePress(int abx, int aby, int mButCode, int mis);
def HD驱动_前台鼠标移动点击(X坐标: int, Y坐标: int, 鼠标按钮代码: int, 间隔毫秒: int) -> int:
    """
    前台鼠标移动点击
    
    Args:
        X坐标: 屏幕坐标X
        Y坐标: 屏幕坐标Y
        鼠标按钮代码: 鼠标按钮值（1=左按下, 2=左弹起, 4=中按下, 8=中弹起, 16=右按下, 32=右弹起）
        间隔毫秒: 按下和弹起之间的毫秒差
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MousePress
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(X坐标, Y坐标, 鼠标按钮代码, 间隔毫秒)

# INT64 __stdcall HCHD_MousePressEx(INT64 hwnd, int x, int y, int mButCode, int mis);
def HD驱动_前台鼠标移动点击Ex(窗口句柄: int, X坐标: int, Y坐标: int, 鼠标按钮代码: int, 间隔毫秒: int) -> int:
    """
    前台驱动鼠标移动并点击（可指定句柄）
    
    Args:
        窗口句柄: 窗口句柄
        X坐标: 窗口客户区坐标X
        Y坐标: 窗口客户区坐标Y
        鼠标按钮代码: 鼠标按钮值（1=左按下, 2=左弹起, 4=中按下, 8=中弹起, 16=右按下, 32=右弹起）
        间隔毫秒: 按下和弹起之间的毫秒差
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MousePressEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口句柄, X坐标, Y坐标, 鼠标按钮代码, 间隔毫秒)

# INT64 __stdcall HCHD_MouseDown(INT64 hwnd, int x, int y, int mButCode);
def HD驱动_前台鼠标移动按下(窗口句柄: int, X坐标: int, Y坐标: int, 鼠标按钮代码: int) -> int:
    """
    前台驱动鼠标移动并按下
    
    Args:
        窗口句柄: 窗口句柄
        X坐标: 窗口客户区坐标X
        Y坐标: 窗口客户区坐标Y
        鼠标按钮代码: 鼠标按钮值（1=左按下, 4=中按下, 16=右按下）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MouseDown
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口句柄, X坐标, Y坐标, 鼠标按钮代码)

# INT64 __stdcall HCHD_MouseUp(INT64 hwnd, int x, int y, int mButCode);
def HD驱动_前台鼠标移动弹起(窗口句柄: int, X坐标: int, Y坐标: int, 鼠标按钮代码: int) -> int:
    """
    前台驱动鼠标移动并弹起
    
    Args:
        窗口句柄: 窗口句柄
        X坐标: 窗口客户区坐标X
        Y坐标: 窗口客户区坐标Y
        鼠标按钮代码: 鼠标按钮值（2=左弹起, 8=中弹起, 32=右弹起）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MouseUp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    return func(窗口句柄, X坐标, Y坐标, 鼠标按钮代码)

# INT64 __stdcall HCHD_KbPress(int virtualKeyCode, int mis);
def HD驱动_前台按键(虚拟键码: int, 间隔毫秒: int) -> int:
    """
    前台驱动键盘（按下并弹起）
    
    Args:
        虚拟键码: 虚拟键码
        间隔毫秒: 按下和弹起之间的毫秒差
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_KbPress
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int]
    
    return func(虚拟键码, 间隔毫秒)

# INT64 __stdcall HCHD_KbDown(int virtualKeyCode);
def HD驱动_前台按键按下(虚拟键码: int) -> int:
    """
    前台驱动键盘（按下）
    
    Args:
        虚拟键码: 虚拟键码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_KbDown
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(虚拟键码)

# INT64 __stdcall HCHD_KbUp(int virtualKeyCode);
def HD驱动_前台按键弹起(虚拟键码: int) -> int:
    """
    前台驱动键盘（弹起）
    
    Args:
        虚拟键码: 虚拟键码
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_KbUp
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(虚拟键码)

# INT64 __stdcall HCHD_RW(int pid, INT64 targetAddress, INT64 bufferAddress, int bufferOfBytes, int rwType);
def HD驱动_驱动读写(进程PID: int, 目标地址: int, 缓冲区地址: int, 缓冲区大小: int, 读写类型: int) -> int:
    """
    驱动读写
    
    Args:
        进程PID: 进程ID
        目标地址: 目标地址
        缓冲区地址: 数据缓冲区指针
        缓冲区大小: 数据缓冲区大小
        读写类型: 读写类型（0=读内存, 1=写内存, 2=强写内存）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_RW
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int, ctypes.c_int]
    
    v2 = ctypes.cast(缓冲区地址, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(进程PID, 目标地址, v3, 缓冲区大小, 读写类型)

# INT64 __stdcall HCHD_RWEx(INT64 targetAddress, INT64 bufferAddress, int bufferOfBytes, int rwType);
def HD驱动_驱动读写Ex(目标地址: int, 缓冲区地址: int, 缓冲区大小: int, 读写类型: int) -> int:
    """
    驱动读写Ex（批量读写）
    
    Args:
        目标地址: 目标地址
        缓冲区地址: 数据缓冲区指针
        缓冲区大小: 数据缓冲区大小
        读写类型: 读写类型（0=读内存, 1=写内存, 2=强写内存）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_RWEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.c_int, ctypes.c_int]
    
    v2 = ctypes.cast(缓冲区地址, ctypes.c_void_p)
    v3 = int(v2.value)

    return func(目标地址, v3, 缓冲区大小, 读写类型)

# INT64 __stdcall HCHD_BeginRWEx(int pid);
def HD驱动_开始读写(进程PID: int) -> int:
    """
    驱动读写Ex（开始批读写）与HD驱动_结束读写成对出现，适合快速遍历
    
    Args:
        进程PID: 进程ID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_BeginRWEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(进程PID)

# INT64 __stdcall HCHD_EndRWEx();
def HD驱动_结束读写(进程PID: int) -> int:
    """
    驱动读写Ex（结束批读写）与HD驱动_开始读写成对出现，适合快速遍历
    
    Args:
        进程PID: 进程ID（实际API不需要此参数，保持向下兼容）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_EndRWEx
    func.restype = ctypes.c_int64
    func.argtypes = []
    
    return func()

# INT64 __stdcall HCHD_AddrIsRead(int pid, INT64 addr, int size);
def HD驱动_地址是否可读(进程PID: int, 地址: int, 字节大小: int) -> int:
    """
    地址是否可读
    
    Args:
        进程PID: 进程ID
        地址: 需要测试的地址
        字节大小: 地址所涉及到的字节大小（4字节或者8字节），不能为其他字节数
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_AddrIsRead
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int]
    
    return func(进程PID, 地址, 字节大小)

# INT64 __stdcall HCHD_PP(int pid, BOOL bOpen);
def HD驱动_进程保护(进程PID: int, 是否开启: bool) -> int:
    """
    进程保护
    
    Args:
        进程PID: 进程ID
        是否开启: 是否开启保护（True=开启保护, False=关闭保护）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_PP
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_bool]
    
    return func(进程PID, 是否开启)

# INT64 __stdcall HCHD_PHide(int pid);
def HD驱动_进程隐藏(进程PID: int) -> int:
    """
    进程隐藏
    
    Args:
        进程PID: 进程ID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_PHide
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(进程PID)

# INT64 __stdcall HCHD_PShow(int pid);
def HD驱动_进程显示(进程PID: int) -> int:
    """
    进程显示
    
    Args:
        进程PID: 进程ID
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_PShow
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(进程PID)

# __int64 __stdcall  HCHD_PPKill(char* processName,__int32 pid);
def HD_进程杀死(
    processName: str,
    pid: int
) -> int:
    """
    进程杀死
    Args:
        processName (str): 进程名，把当前所有相同进程名全部杀掉
        pid (int): 进程PID，指定了PID进程名就失效
    Returns:
        int: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()
    func = hd.HCHD_PPKill
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_char_p, ctypes.c_int]
    
    return func(auto_encode(processName), pid)


# INT64 __stdcall HCHD_MemoryAllocate(int pid, INT64 memorySize, int memoryProtect, BOOL bHighAddress, INT64 pOutBuffer);
def HD驱动_申请内存(进程PID: int, 内存大小: int, 内存保护属性: int, 是否高位内存: bool, 输出缓冲区: int) -> int:
    """
    驱动申请内存
    
    Args:
        进程PID: 进程ID
        内存大小: 申请大小
        内存保护属性: 内存保护属性，例如0x40（64）可读可写可执行
        是否高位内存: 是否申请高位内存
        输出缓冲区: 缓冲区指针（存申请返回的地址）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryAllocate
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int, ctypes.c_bool, ctypes.c_int64]
    
    v2 = ctypes.cast(输出缓冲区, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(进程PID, 内存大小, 内存保护属性, 是否高位内存, v3)

# INT64 __stdcall HCHD_MemoryAllocateEx(int pid, INT64 memoryAddr, INT64 memorySize, int memoryProtect, BOOL bHighAddress, INT64 pOutBuffer);
def HD驱动_申请内存Ex(进程PID: int, 内存地址: int, 内存大小: int, 内存保护属性: int, 是否高位内存: bool, 输出缓冲区: int) -> int:
    """
    驱动申请内存（扩展版本）
    
    Args:
        进程PID: 进程ID
        内存地址: 指定的内存地址或者为NULL（0）
        内存大小: 申请大小
        内存保护属性: 内存保护属性
        是否高位内存: 是否申请高位内存
        输出缓冲区: 缓冲区指针（存申请返回的地址）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryAllocateEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int, ctypes.c_bool, ctypes.c_int64]
    
    v2 = ctypes.cast(输出缓冲区, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(进程PID, 内存地址, 内存大小, 内存保护属性, 是否高位内存, v3)

# INT64 __stdcall HCHD_MemoryFree(int pid, INT64 memoryAddress);
def HD驱动_内存释放(进程PID: int, 内存地址: int) -> int:
    """
    驱动内存释放
    
    Args:
        进程PID: 进程ID
        内存地址: 需要释放的内存地址
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryFree
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64]
    
    return func(进程PID, 内存地址)

# INT64 __stdcall HCHD_MemoryProtect(int pid, INT64 memoryAddress, INT64 memoryOfBytes, int newProtect);
def HD驱动_修改内存保护(进程PID: int, 内存地址: int, 内存字节数: int, 新保护值: int) -> int:
    """
    驱动修改内存保护属性
    
    Args:
        进程PID: 进程ID
        内存地址: 内存地址
        内存字节数: 内存大小
        新保护值: 新保护值
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryProtect
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int]
    
    return func(进程PID, 内存地址, 内存字节数, 新保护值)

# INT64 __stdcall HCHD_MemoryHide(int pid, INT64 memoryAddress, INT64 memoryOfBytes);
def HD驱动_内存隐藏(进程PID: int, 内存地址: int, 内存字节数: int) -> int:
    """
    驱动内存隐藏
    
    Args:
        进程PID: 进程ID
        内存地址: 内存地址
        内存字节数: 内存大小
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryHide
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64]
    
    return func(进程PID, 内存地址, 内存字节数)

# INT64 __stdcall HCHD_MemoryQuery(int pid, INT64 memoryAddress, PVOID pOutBuffer);
def HD驱动_内存查询(进程PID: int, 内存地址: int, 输出缓冲区: int) -> int:
    """
    驱动内存查询
    
    Args:
        进程PID: 进程ID
        内存地址: 内存地址
        输出缓冲区: 缓冲区指针（这里固定使用的是64位的MEMORY_BASIC_INFORMATION结构体，结构体大小48字节）
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryQuery
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_void_p]
    
    v2 = ctypes.cast(输出缓冲区, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(进程PID, 内存地址, ctypes.c_void_p(v3))

# __int64 __stdcall HCHD_MemoryFindCode(__int32 pid, __int64 address, __int64 siginCode, __int32 siginCodeSize, __int32 iProtect, __int64 outBuffer);
def HD驱动_特征码查找地址(pid: int, address: int, siginCode: int, siginCodeSize: int, iProtect: int, outBuffer: int) -> int:
    """
    驱动特征码查找地址
    
    Args:
        pid: 进程ID
        address: 起始搜索地址
        siginCode: 特征码(二进制缓冲区不是字符串)
        siginCodeSize: 特征码长度(字节单位)
        iProtect: 要搜索的内存保护属性
        outBuffer: 缓冲区(存地址)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_MemoryFindCode
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_int, ctypes.c_int, ctypes.c_int64]
    
    v2 = ctypes.cast(outBuffer, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(pid, address, siginCode, siginCodeSize, iProtect, v3)

# __int64 __stdcall HCHD_GetMainModuleBase(__int32 pid, __int64 outBuffer);
def HD驱动_获取主模块地址(pid: int, outBuffer: int) -> int:
    """
    获取主模块地址
    
    Args:
        pid: 进程ID
        outBuffer: 缓冲区(存地址)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_GetMainModuleBase
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64]
    
    v2 = ctypes.cast(outBuffer, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(pid, v3)

# __int64 __stdcall HCHD_GetModuleBase(__int32 pid, char* moduleName, __int64 outBuffer);
def HD驱动_获取模块地址(pid: int, moduleName: str, outBuffer: int) -> int:
    """
    获取模块地址
    
    Args:
        pid: 进程ID
        moduleName: 模块名(Ascii字符串)
        outBuffer: 缓冲区(存地址)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_GetModuleBase
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int64]
    
    v2 = ctypes.cast(outBuffer, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(pid, auto_encode(moduleName), v3)

# __int64  __stdcall HCHD_GetModuleCallAddr(__int32 pid, char* moduleName, char* callName, __int64 outBuffer);
def HD驱动_获取模块函数地址(pid: int, moduleName: str, callName: str, outBuffer: int) -> int:
    """
    获取模块函数地址
    
    Args:
        pid: 进程ID
        moduleName: 模块名(Ascii字符串)
        callName: 函数名(Ascii字符串)
        outBuffer: 缓冲区(存地址)
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_GetModuleCallAddr
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64]
    
    v2 = ctypes.cast(outBuffer, ctypes.c_void_p)
    v3 = int(v2.value)
    
    return func(pid, auto_encode(moduleName), auto_encode(callName), v3)

# __int64 __stdcall HCHD_NTNCaptureScreen(__int64 hWnd, BOOL Enable);
def HD驱动_反截图(hWnd: int, Enable: bool) -> int:
    """
    反截图功能
    
    Args:
        hWnd: 窗口句柄
        Enable: 是否启用
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_NTNCaptureScreen
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64, ctypes.c_bool]
    
    return func(hWnd, Enable)

# __int64 __stdcall HCHD_NTThreadRunCall(__int32 pid, __int64 callAddress);
def HD驱动_远线程执行CALL(pid: int, callAddress: int) -> int:
    """
    远线程执行CALL
    
    Args:
        pid: 进程ID
        callAddress: 函数地址
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_NTThreadRunCall
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int, ctypes.c_int64]
    
    return func(pid, callAddress)

# __int64 __stdcall HCHD_ChangeMachineKey(__int32 type);
def HD驱动_修改机器码(type: int) -> int:
    """
    修改机器码
    
    Args:
        type: 参数类型
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_ChangeMachineKey
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]

    return func(type)

# INT64 __stdcall HCHD_ClearInject();
def HD驱动_清除注入缓存() -> int:
    """
    驱动清除注入缓存(全局插件缓存,DLL缓存)
    
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_ClearInject
    func.restype = ctypes.c_int64
    func.argtypes = []
    
    return func()

# INT64 __stdcall HCHD_PcrocessRoot(int pid);
def HD驱动_进程提权(pid: int) -> int:
    """
    驱动进程提权
    
    Args:
        pid: 进程ID
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_PcrocessRoot
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int]
    
    return func(pid)

# INT64 __stdcall HCHD_PcrocessRootEx(INT64 handle);
def HD驱动_进程提权Ex(handle: int) -> int:
    """
    进程提权（扩展版本）
    
    Args:
        handle: 句柄
        
    Returns:
        int: 返回值代码（查看HD返回值表）
    """
    hd = Config.get_hd()
    
    func = hd.HCHD_PcrocessRootEx
    func.restype = ctypes.c_int64
    func.argtypes = [ctypes.c_int64]
    
    return func(handle)

