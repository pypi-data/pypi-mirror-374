from .config import Config, ctypes
from .config import auto_encode

#HDHOOK send HOOK回调
#typedef __int32(__stdcall *HandleCallBackFunType_Send)(__int32 窗口序号, __int32 插件序号, __int64 rcxOrl1, __int64 rdxOrl2, __int64 r8Orl3, __int64 r9Orl4, __int64 rbp, __int64 rsp, __int64 rip, char*buffer, __int32 bufferMaxSize, __int32 bufferRealSize, __int64 lparam);//返回1表示要修改
HD_HandleCallBackFunTypeSend_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64)

#HDHOOK sendto HOOK回调
#typedef __int32(__stdcall *HandleCallBackFunType_SendTo)(__int32 窗口序号, __int32 插件序号, __int64 rcxOrl1, __int64 rdxOrl2, __int64 r8Orl3, __int64 r9Orl4,  __int64 l5, __int64 l6, __int64 rbp, __int64 rsp, __int64 rip, char*buffer, __int32 bufferMaxSize, __int32 bufferRealSize, __int64 lparam);//返回1表示要修改
HD_HandleCallBackFunTypeSendTo_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64)

#HDHOOK recv HOOK回调
#typedef __int32(__stdcall *HandleCallBackFunType_Recv)(__int32 窗口序号, __int32 插件序号, __int64 rcxOrl1, __int64 rdxOrl2, __int64 r8Orl3, __int64 r9Orl4, __int64 rbp, __int64 rsp, __int64 rip, char*buffer, __int32 bufferMaxSize, __int32 bufferRealSize, __int64 lparam);//返回1表示要修改
HD_HandleCallBackFunTypeRecv_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64)

#HDHOOK recvFrom HOOK回调
#typedef __int32(__stdcall *HandleCallBackFunType_RecvFrom)(__int32 窗口序号, __int32 插件序号, __int64 rcxOrl1, __int64 rdxOrl2, __int64 r8Orl3, __int64 r9Orl4,  __int64 l5, __int64 l6, __int64 rbp, __int64 rsp, __int64 rip, char*buffer, __int32 bufferMaxSize, __int32 bufferRealSize, __int64 lparam);//返回1表示要修改
HD_HandleCallBackFunTypeRecvFrom_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64)


#HDHOOK 任意点HOOK回调
#typedef __int64(__stdcall *HandleCallBackFunType)(__int32 窗口序号, __int32 插件序号,__int64 raxOreax, __int64 rbxOrebx,__int64 rcxOrecx, __int64 rdxOredx,__int64 rbpOrebp, __int64 rspOresp,__int64 rsiOresi, __int64 rdiOredi,__int64 r8, __int64 r9, __int64 r10, __int64 r11, __int64 r12, __int64 r13, __int64 r14, __int64 r15,__int64 lparam);
HD_HandleCallBackFunTypeHook_stdcall = ctypes.WINFUNCTYPE(ctypes.c_int64,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64)


# INT64 __stdcall HDHK_InterceptApi(int 窗口序号, char* 模块名字, char* 拦截接口名字, int 破坏字节数, INT64 回调地址, INT64 附加参数, BOOL 是否主线程调用);
def HDHOOK_拦截API(窗口序号: int, 模块名字: str, 拦截接口名字: str, 破坏字节数: int, 回调地址: HD_HandleCallBackFunTypeSend_stdcall, 附加参数: int, 是否主线程调用: bool = False) -> int:
    """
    设置拦截API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 接口所在的dll模块名字
    :param 拦截接口名字: 接口名字 如:send sendto recv recvfrom 注意是小写字母！
    :param 破坏字节数: [ X86->send recv sendto recvfrom是5 ] [ X64->send recv是5 sendto recvfrom是7]
    :param 回调地址: 遵循下面回调函数类型
    :param 附加参数: 自定义参数,此参数会传递给回调函数
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_InterceptApi = hd.HDHK_InterceptApi
    HDHK_InterceptApi.restype = ctypes.c_int64

    # 使用auto_encode自动转换编码
    module_bytes = auto_encode(模块名字)
    interface_bytes = auto_encode(拦截接口名字)
    #判断 走不同的回调
    if 拦截接口名字 == "send" or 拦截接口名字 == "recv":
        HDHK_InterceptApi.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_char_p,  # 模块名字
            ctypes.c_char_p,  # 拦截接口名字
            ctypes.c_int32,  # 破坏字节数
            ctypes.c_int64,  # 回调地址 send recv一样
            ctypes.c_int64,  # 附加参数
            ctypes.c_bool  # 是否主线程调用
        ]
        #
        回调地址Fun = HD_HandleCallBackFunTypeSend_stdcall(回调地址)
        # 正确获取回调函数的地址并转换为64位整数：使用ctypes.cast将回调对象转换为c_void_p，然后获取其数值并转为c_int64。
        回调地址Fun_ptr = ctypes.c_int64(ctypes.cast(回调地址Fun, ctypes.c_void_p).value) if 回调地址Fun else ctypes.c_int64(0)

        # 调用C函数
        return HDHK_InterceptApi(
            ctypes.c_int32(窗口序号),
            module_bytes,
            interface_bytes,
            ctypes.c_int32(破坏字节数),
            回调地址Fun_ptr,
            ctypes.c_int64(附加参数),
            ctypes.c_bool(是否主线程调用)
        )
    elif 拦截接口名字 == "sendto" or 拦截接口名字 == "recvfrom":
        HDHK_InterceptApi.argtypes = [
            ctypes.c_int32,  # 窗口序号
            ctypes.c_char_p,  # 模块名字
            ctypes.c_char_p,  # 拦截接口名字
            ctypes.c_int32,  # 破坏字节数
            ctypes.c_int64,  # 回调地址 send recv一样
            ctypes.c_int64,  # 附加参数
            ctypes.c_bool  # 是否主线程调用
        ]
        #
        回调地址Fun = HD_HandleCallBackFunTypeSendTo_stdcall(回调地址)
        # 正确获取回调函数的地址并转换为64位整数：使用ctypes.cast将回调对象转换为c_void_p，然后获取其数值并转为c_int64。
        回调地址Fun_ptr = ctypes.c_int64(ctypes.cast(回调地址Fun, ctypes.c_void_p).value) if 回调地址Fun else ctypes.c_int64(0)
        # 调用C函数
        return HDHK_InterceptApi(
          ctypes.c_int32(窗口序号),
          module_bytes,
          interface_bytes,
          ctypes.c_int32(破坏字节数),
            回调地址Fun_ptr,
          ctypes.c_int64(附加参数),
          ctypes.c_bool(是否主线程调用)
        )
    else:
        return 0

# INT64 __stdcall HDHK_PauseInterceptApi(int 窗口序号, char* 模块名字, char* 拦截接口名字, BOOL 是否主线程调用);
def HDHOOK_暂停拦截API(窗口序号: int, 模块名字: str, 拦截接口名字: str, 是否主线程调用: bool = False) -> int:
    """
    暂停拦截API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 接口所在的dll模块名字
    :param 拦截接口名字: 接口名字 如:send sendto recv recvfrom 注意是小写字母！
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_PauseInterceptApi = hd.HDHK_PauseInterceptApi
    HDHK_PauseInterceptApi.restype = ctypes.c_int64
    HDHK_PauseInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    module_bytes = auto_encode(模块名字)
    interface_bytes = auto_encode(拦截接口名字)

    ret = HDHK_PauseInterceptApi(
        ctypes.c_int32(窗口序号),
        module_bytes,
        interface_bytes,
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_RecoverInterceptApi(int 窗口序号, char* 模块名字, char* 拦截接口名字, BOOL 是否主线程调用);
def HDHOOK_恢复拦截API(窗口序号: int, 模块名字: str, 拦截接口名字: str, 是否主线程调用: bool = False) -> int:
    """
    恢复拦截API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 接口所在的dll模块名字
    :param 拦截接口名字: 接口名字 如:send sendto recv recvfrom 注意是小写字母！
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_RecoverInterceptApi = hd.HDHK_RecoverInterceptApi
    HDHK_RecoverInterceptApi.restype = ctypes.c_int64
    HDHK_RecoverInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    module_bytes = auto_encode(模块名字)
    interface_bytes = auto_encode(拦截接口名字)

    ret = HDHK_RecoverInterceptApi(
        ctypes.c_int32(窗口序号),
        module_bytes,
        interface_bytes,
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_UnInterceptApi(int 窗口序号, char* 模块名字, char* 拦截接口名字, BOOL 是否主线程调用);
def HDHOOK_卸载拦截API(窗口序号: int, 模块名字: str, 拦截接口名字: str, 是否主线程调用: bool = False) -> int:
    """
    卸载拦截API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 接口所在的dll模块名字
    :param 拦截接口名字: 接口名字 如:send sendto recv recvfrom 注意是小写字母！
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_UnInterceptApi = hd.HDHK_UnInterceptApi
    HDHK_UnInterceptApi.restype = ctypes.c_int64
    HDHK_UnInterceptApi.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]

    # 使用auto_encode自动转换编码
    module_bytes = auto_encode(模块名字)
    interface_bytes = auto_encode(拦截接口名字)

    ret = HDHK_UnInterceptApi(
        ctypes.c_int32(窗口序号),
        module_bytes,
        interface_bytes,
        ctypes.c_bool(是否主线程调用)
    )

    return ret

#INT64 HDHK_SendApi(int 窗口序号, int socket, BYTE *buffer, int bufferSize, int flag, BOOL 是否主线程调用 = FALSE);
# INT64 __stdcall HDHK_SendApi(int 窗口序号, int socket, BYTE *buffer, int bufferSize, int flag, BOOL 是否主线程调用);
def HDHOOK_Send发包(窗口序号: int, socket: int, buffer: bytes, bufferSize: int, flag: int, 是否主线程调用: bool = False) -> int:
    """
    发送API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param socket: 套接字
    :param buffer: 数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
    :param bufferSize: 缓冲区大小
    :param flag: 标志
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_SendApi = hd.HDHK_SendApi
    HDHK_SendApi.restype = ctypes.c_int64
    HDHK_SendApi.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_bool
    ]

    buffer_array = (ctypes.c_ubyte * bufferSize)(*buffer)

    ret = HDHK_SendApi(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(socket),
        buffer_array,
        ctypes.c_int32(bufferSize),
        ctypes.c_int32(flag),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_SendToApi(int 窗口序号, int socket, BYTE *buffer, int bufferSize, int flag, int port, int ip, BOOL 是否主线程调用);
def HDHOOK_SendTo发包(窗口序号: int, socket: int, buffer: bytes, bufferSize: int, flag: int, port: int, ip: int, 是否主线程调用: bool = False) -> int:
    """
    发送到API(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param socket: 套接字
    :param buffer: 数据缓冲区 (bytes) - 字节数组，如：b'\x01\x02\x03' 或 bytes([1, 2, 3])
    :param bufferSize: 缓冲区大小
    :param flag: 标志
    :param port: 目标端口
    :param ip: 目标IP地址
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_SendToApi = hd.HDHK_SendToApi
    HDHK_SendToApi.restype = ctypes.c_int64
    HDHK_SendToApi.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_bool
    ]

    buffer_array = (ctypes.c_ubyte * bufferSize)(*buffer)

    ret = HDHK_SendToApi(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(socket),
        buffer_array,
        ctypes.c_int32(bufferSize),
        ctypes.c_int32(flag),
        ctypes.c_int32(port),
        ctypes.c_int32(ip),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_SetProcessCallBackLparamSendX86(int 窗口序号, int l1, int l2, int l3, int l4, int ebp, int esp, int eip, int mark);
def HDHOOK_设置拦截Send返回参数X86(窗口序号: int, l1: int = None, l2: int = None, l3: int = None, l4: int = None, ebp: int = None, esp: int = None, eip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（Send API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param l1: 参数1
    :param l2: 参数2
    :param l3: 参数3
    :param l4: 参数4
    :param ebp: EBP寄存器值
    :param esp: ESP寄存器值
    :param eip: EIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数) (默认0)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_SetProcessCallBackLparamSendX86 = hd.HDHK_SetProcessCallBackLparamSendX86
    HDHK_SetProcessCallBackLparamSendX86.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamSendX86.argtypes = [
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_int32
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        l1 = l1 if l1 is not None else 0
    else:
        l1 = 0

    if mark & 2:
        l2 = l2 if l2 is not None else 0
    else:
        l2 = 0

    if mark & 4:
        l3 = l3 if l3 is not None else 0
    else:
        l3 = 0

    if mark & 8:
        l4 = l4 if l4 is not None else 0
    else:
        l4 = 0

    if mark & 16:
        ebp = ebp if ebp is not None else 0
    else:
        ebp = 0

    if mark & 32:
        esp = esp if esp is not None else 0
    else:
        esp = 0

    if mark & 64:
        eip = eip if eip is not None else 0
    else:
        eip = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamSendX86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(l1),
        ctypes.c_int32(l2),
        ctypes.c_int32(l3),
        ctypes.c_int32(l4),
        ctypes.c_int32(ebp),
        ctypes.c_int32(esp),
        ctypes.c_int32(eip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 HDHK_SetProcessCallBackLparamRecvX86(int 窗口序号, int l1, int l2, int l3, int l4, int ebp, int esp, int eip, int mark );
def HDHOOK_设置拦截Recv返回参数X86(窗口序号: int, l1: int = None, l2: int = None, l3: int = None, l4: int = None, ebp: int = None, esp: int = None, eip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（Recv API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param l1: 参数1
    :param l2: 参数2
    :param l3: 参数3
    :param l4: 参数4
    :param ebp: EBP寄存器值
    :param esp: ESP寄存器值
    :param eip: EIP寄存器值
    :param mark: 整数型的网络字节序 如:"127.0.0.1"  那么就需要写成:0x0100007F
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamRecvX86 = hd.HDHK_SetProcessCallBackLparamRecvX86
    HDHK_SetProcessCallBackLparamRecvX86.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamRecvX86.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int32,       # l1
        ctypes.c_int32,       # l2
        ctypes.c_int32,       # l3
        ctypes.c_int32,       # l4
        ctypes.c_int32,       # ebp
        ctypes.c_int32,       # esp
        ctypes.c_int32,       # eip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        l1 = l1 if l1 is not None else 0
    else:
        l1 = 0

    if mark & 2:
        l2 = l2 if l2 is not None else 0
    else:
        l2 = 0

    if mark & 4:
        l3 = l3 if l3 is not None else 0
    else:
        l3 = 0

    if mark & 8:
        l4 = l4 if l4 is not None else 0
    else:
        l4 = 0

    if mark & 16:
        ebp = ebp if ebp is not None else 0
    else:
        ebp = 0

    if mark & 32:
        esp = esp if esp is not None else 0
    else:
        esp = 0

    if mark & 64:
        eip = eip if eip is not None else 0
    else:
        eip = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamRecvX86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(l1),
        ctypes.c_int32(l2),
        ctypes.c_int32(l3),
        ctypes.c_int32(l4),
        ctypes.c_int32(ebp),
        ctypes.c_int32(esp),
        ctypes.c_int32(eip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 HDHK_SetProcessCallBackLparamSendToX86(int 窗口序号, int l1, int l2, int l3, int l4, int l5, int l6, int ebp, int esp, int eip, int mark);
def HDHOOK_设置拦截SendTo返回参数X86(窗口序号: int, l1: int = None, l2: int = None, l3: int = None, l4: int = None, l5: int = None, l6: int = None, ebp: int = None, esp: int = None, eip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（SendTo API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param l1: 参数1
    :param l2: 参数2
    :param l3: 参数3
    :param l4: 参数4
    :param l5: 参数5 (端口)
    :param l6: 参数6 (IP地址)
    :param ebp: EBP寄存器值
    :param esp: ESP寄存器值
    :param eip: EIP寄存器值
    :param mark: 整数型的网络字节序 如:"127.0.0.1"  那么就需要写成:0x0100007F
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamSendToX86 = hd.HDHK_SetProcessCallBackLparamSendToX86
    HDHK_SetProcessCallBackLparamSendToX86.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamSendToX86.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int32,       # l1
        ctypes.c_int32,       # l2
        ctypes.c_int32,       # l3
        ctypes.c_int32,       # l4
        ctypes.c_int32,       # l5
        ctypes.c_int32,       # l6
        ctypes.c_int32,       # ebp
        ctypes.c_int32,       # esp
        ctypes.c_int32,       # eip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        l1 = l1 if l1 is not None else 0
    else:
        l1 = 0

    if mark & 2:
        l2 = l2 if l2 is not None else 0
    else:
        l2 = 0

    if mark & 4:
        l3 = l3 if l3 is not None else 0
    else:
        l3 = 0

    if mark & 8:
        l4 = l4 if l4 is not None else 0
    else:
        l4 = 0

    if mark & 16:
        ebp = ebp if ebp is not None else 0
    else:
        ebp = 0

    if mark & 32:
        esp = esp if esp is not None else 0
    else:
        esp = 0

    if mark & 64:
        eip = eip if eip is not None else 0
    else:
        eip = 0

    if mark & 128:
        l5 = l5 if l5 is not None else 0
    else:
        l5 = 0

    if mark & 256:
        l6 = l6 if l6 is not None else 0
    else:
        l6 = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamSendToX86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(l1),
        ctypes.c_int32(l2),
        ctypes.c_int32(l3),
        ctypes.c_int32(l4),
        ctypes.c_int32(l5),
        ctypes.c_int32(l6),
        ctypes.c_int32(ebp),
        ctypes.c_int32(esp),
        ctypes.c_int32(eip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 SetProcessCallBackLparamRecvFromX86(int 窗口序号, int l1, int l2, int l3, int l4, int l5, int l6, int ebp, int esp, int eip, int mark);
def HDHOOK_设置拦截RecvFrom返回参数X86(窗口序号: int, l1: int = None, l2: int = None, l3: int = None, l4: int = None, l5: int = None, l6: int = None, ebp: int = None, esp: int = None, eip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（RecvFrom API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param l1: 参数1
    :param l2: 参数2
    :param l3: 参数3
    :param l4: 参数4
    :param l5: 参数5 (端口)
    :param l6: 参数6 (IP地址)
    :param ebp: EBP寄存器值
    :param esp: ESP寄存器值
    :param eip: EIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数)
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamRecvFromX86 = hd.HDHK_SetProcessCallBackLparamRecvFromX86
    HDHK_SetProcessCallBackLparamRecvFromX86.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamRecvFromX86.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int32,       # l1
        ctypes.c_int32,       # l2
        ctypes.c_int32,       # l3
        ctypes.c_int32,       # l4
        ctypes.c_int32,       # l5
        ctypes.c_int32,       # l6
        ctypes.c_int32,       # ebp
        ctypes.c_int32,       # esp
        ctypes.c_int32,       # eip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        l1 = l1 if l1 is not None else 0
    else:
        l1 = 0

    if mark & 2:
        l2 = l2 if l2 is not None else 0
    else:
        l2 = 0

    if mark & 4:
        l3 = l3 if l3 is not None else 0
    else:
        l3 = 0

    if mark & 8:
        l4 = l4 if l4 is not None else 0
    else:
        l4 = 0

    if mark & 16:
        ebp = ebp if ebp is not None else 0
    else:
        ebp = 0

    if mark & 32:
        esp = esp if esp is not None else 0
    else:
        esp = 0

    if mark & 64:
        eip = eip if eip is not None else 0
    else:
        eip = 0

    if mark & 128:
        l5 = l5 if l5 is not None else 0
    else:
        l5 = 0

    if mark & 256:
        l6 = l6 if l6 is not None else 0
    else:
        l6 = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamRecvFromX86(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(l1),
        ctypes.c_int32(l2),
        ctypes.c_int32(l3),
        ctypes.c_int32(l4),
        ctypes.c_int32(l5),
        ctypes.c_int32(l6),
        ctypes.c_int32(ebp),
        ctypes.c_int32(esp),
        ctypes.c_int32(eip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 HDHK_SetProcessCallBackLparamSendX64(int 窗口序号, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 rbp, INT64 rsp, INT64 rip, int mark);
def HDHOOK_设置拦截Send返回参数X64(窗口序号: int, rcx: int = None, rdx: int = None, r8: int = None, r9: int = None, rbp: int = None, rsp: int = None, rip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（Send API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param rcx: 参数1
    :param rdx: 参数2
    :param r8: 参数3
    :param r9: 参数4
    :param rbp: RBP寄存器值
    :param rsp: RSP寄存器值
    :param rip: RIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数)
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamSendX64 = hd.HDHK_SetProcessCallBackLparamSendX64
    HDHK_SetProcessCallBackLparamSendX64.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamSendX64.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int64,       # rcx
        ctypes.c_int64,       # rdx
        ctypes.c_int64,       # r8
        ctypes.c_int64,       # r9
        ctypes.c_int64,       # rbp
        ctypes.c_int64,       # rsp
        ctypes.c_int64,       # rip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        rcx = rcx if rcx is not None else 0
    else:
        rcx = 0

    if mark & 2:
        rdx = rdx if rdx is not None else 0
    else:
        rdx = 0

    if mark & 4:
        r8 = r8 if r8 is not None else 0
    else:
        r8 = 0

    if mark & 8:
        r9 = r9 if r9 is not None else 0
    else:
        r9 = 0

    if mark & 16:
        rbp = rbp if rbp is not None else 0
    else:
        rbp = 0

    if mark & 32:
        rsp = rsp if rsp is not None else 0
    else:
        rsp = 0

    if mark & 64:
        rip = rip if rip is not None else 0
    else:
        rip = 0



    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamSendX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(rbp),
        ctypes.c_int64(rsp),
        ctypes.c_int64(rip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 HDHK_SetProcessCallBackLparamRecvX64(int 窗口序号, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 rbp, INT64 rsp, INT64 rip, int mark);
def HDHOOK_设置拦截Recv返回参数X64(窗口序号: int, rcx: int = None, rdx: int = None, r8: int = None, r9: int = None, rbp: int = None, rsp: int = None, rip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（Recv API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param rcx: 参数1
    :param rdx: 参数2
    :param r8: 参数3
    :param r9: 参数4
    :param rbp: RBP寄存器值
    :param rsp: RSP寄存器值
    :param rip: RIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数)
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamRecvX64 = hd.HDHK_SetProcessCallBackLparamRecvX64
    HDHK_SetProcessCallBackLparamRecvX64.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamRecvX64.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int64,       # rcx
        ctypes.c_int64,       # rdx
        ctypes.c_int64,       # r8
        ctypes.c_int64,       # r9
        ctypes.c_int64,       # rbp
        ctypes.c_int64,       # rsp
        ctypes.c_int64,       # rip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        rcx = rcx if rcx is not None else 0
    else:
        rcx = 0

    if mark & 2:
        rdx = rdx if rdx is not None else 0
    else:
        rdx = 0

    if mark & 4:
        r8 = r8 if r8 is not None else 0
    else:
        r8 = 0

    if mark & 8:
        r9 = r9 if r9 is not None else 0
    else:
        r9 = 0

    if mark & 16:
        rbp = rbp if rbp is not None else 0
    else:
        rbp = 0

    if mark & 32:
        rsp = rsp if rsp is not None else 0
    else:
        rsp = 0

    if mark & 64:
        rip = rip if rip is not None else 0
    else:
        rip = 0



    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamRecvX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(rbp),
        ctypes.c_int64(rsp),
        ctypes.c_int64(rip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 SetProcessCallBackLparamSendToX64(int 窗口序号, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, INT64 rbp, INT64 rsp, INT64 rip, int mark);
def HDHOOK_设置拦截SendTo返回参数X64(窗口序号: int, rcx: int = None, rdx: int = None, r8: int = None, r9: int = None, l5: int = None, l6: int = None, rbp: int = None, rsp: int = None, rip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（SendTo API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param rcx: 参数1
    :param rdx: 参数2
    :param r8: 参数3
    :param r9: 参数4
    :param l5: 参数5 (端口)
    :param l6: 参数6 (IP地址)
    :param rbp: RBP寄存器值
    :param rsp: RSP寄存器值
    :param rip: RIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数)
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamSendToX64 = hd.HDHK_SetProcessCallBackLparamSendToX64
    HDHK_SetProcessCallBackLparamSendToX64.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamSendToX64.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int64,       # rcx
        ctypes.c_int64,       # rdx
        ctypes.c_int64,       # r8
        ctypes.c_int64,       # r9
        ctypes.c_int64,       # l5
        ctypes.c_int64,       # l6
        ctypes.c_int64,       # rbp
        ctypes.c_int64,       # rsp
        ctypes.c_int64,       # rip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        rcx = rcx if rcx is not None else 0
    else:
        rcx = 0

    if mark & 2:
        rdx = rdx if rdx is not None else 0
    else:
        rdx = 0

    if mark & 4:
        r8 = r8 if r8 is not None else 0
    else:
        r8 = 0

    if mark & 8:
        r9 = r9 if r9 is not None else 0
    else:
        r9 = 0

    if mark & 16:
        rbp = rbp if rbp is not None else 0
    else:
        rbp = 0

    if mark & 32:
        rsp = rsp if rsp is not None else 0
    else:
        rsp = 0

    if mark & 64:
        rip = rip if rip is not None else 0
    else:
        rip = 0

    if mark & 128:
        l5 = l5 if l5 is not None else 0
    else:
        l5 = 0

    if mark & 256:
        l6 = l6 if l6 is not None else 0
    else:
        l6 = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamSendToX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        ctypes.c_int64(rbp),
        ctypes.c_int64(rsp),
        ctypes.c_int64(rip),
        ctypes.c_int32(mark)
    )

    return ret

#INT64 HDHK_SetProcessCallBackLparamRecvFromX64(int 窗口序号, INT64 rcx, INT64 rdx, INT64 r8, INT64 r9, INT64 l5, INT64 l6, INT64 rbp, INT64 rsp, INT64 rip, int mark);
def HDHOOK_设置拦截RecvFrom返回参数X64(窗口序号: int, rcx: int = None, rdx: int = None, r8: int = None, r9: int = None, l5: int = None, l6: int = None, rbp: int = None, rsp: int = None, rip: int = None, mark: int = 0) -> int:
    """
    设置回调函数返回值给目标进程（RecvFrom API）
    :param 窗口序号: 窗口序号 (从1开始)
    :param rcx: 参数1
    :param rdx: 参数2
    :param r8: 参数3
    :param r9: 参数4
    :param l5: 参数5 (端口)
    :param l6: 参数6 (IP地址)
    :param rbp: RBP寄存器值
    :param rsp: RSP寄存器值
    :param rip: RIP寄存器值
    :param mark: 修改相关寄存器值和其他值的掩码值(2的倍数)
    :return:
    """
    hd = Config.get_hd()

    # 定义函数指针类型
    HDHK_SetProcessCallBackLparamRecvFromX64 = hd.HDHK_SetProcessCallBackLparamRecvFromX64
    HDHK_SetProcessCallBackLparamRecvFromX64.restype = ctypes.c_int64
    HDHK_SetProcessCallBackLparamRecvFromX64.argtypes = [
        ctypes.c_int32,       # 窗口序号
        ctypes.c_int64,       # rcx
        ctypes.c_int64,       # rdx
        ctypes.c_int64,       # r8
        ctypes.c_int64,       # r9
        ctypes.c_int64,       # l5
        ctypes.c_int64,       # l6
        ctypes.c_int64,       # rbp
        ctypes.c_int64,       # rsp
        ctypes.c_int64,       # rip
        ctypes.c_int32        # mark
    ]

    # 根据mark值设置需要修改的参数
    if mark & 1:
        rcx = rcx if rcx is not None else 0
    else:
        rcx = 0

    if mark & 2:
        rdx = rdx if rdx is not None else 0
    else:
        rdx = 0

    if mark & 4:
        r8 = r8 if r8 is not None else 0
    else:
        r8 = 0

    if mark & 8:
        r9 = r9 if r9 is not None else 0
    else:
        r9 = 0

    if mark & 16:
        rbp = rbp if rbp is not None else 0
    else:
        rbp = 0

    if mark & 32:
        rsp = rsp if rsp is not None else 0
    else:
        rsp = 0

    if mark & 64:
        rip = rip if rip is not None else 0
    else:
        rip = 0

    if mark & 128:
        l5 = l5 if l5 is not None else 0
    else:
        l5 = 0

    if mark & 256:
        l6 = l6 if l6 is not None else 0
    else:
        l6 = 0

    # 调用C函数
    ret = HDHK_SetProcessCallBackLparamRecvFromX64(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(rcx),
        ctypes.c_int64(rdx),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(l5),
        ctypes.c_int64(l6),
        ctypes.c_int64(rbp),
        ctypes.c_int64(rsp),
        ctypes.c_int64(rip),
        ctypes.c_int32(mark)
    )

    return ret

# INT64 __stdcall HDHK_Hook(int 窗口序号, INT64 hook地址, int 破坏字节, INT64 回调地址, INT64 附加参数, BOOL 是否主线程调用);
def HDHOOK_挂钩(窗口序号: int, hook地址: int, 破坏字节: int, 回调地址: HD_HandleCallBackFunTypeHook_stdcall, 附加参数: int, 是否主线程调用: bool = False) -> int:
    """
    任意HOOK(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param hook地址: 当前HOOK的目标地址
    :param 破坏字节: 涉及到的汇编字节数
    :param 回调地址: 请查询手册将写好的函数填进来
    :param 附加参数: 自定义参数,此参数会传递给回调函数
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_Hook = hd.HDHK_Hook
    HDHK_Hook.restype = ctypes.c_int64
    HDHK_Hook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]

    HandleCallBackFunTypeHook_stdcall = HD_HandleCallBackFunTypeHook_stdcall(回调地址)
    HandleCallBackFunTypeHook_stdcall_ptr = ctypes.c_int64(ctypes.cast(HandleCallBackFunTypeHook_stdcall, ctypes.c_void_p).value) if HandleCallBackFunTypeHook_stdcall else ctypes.c_int64(0)

    ret = HDHK_Hook(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(hook地址),
        ctypes.c_int32(破坏字节),
        HandleCallBackFunTypeHook_stdcall_ptr,
        ctypes.c_int64(附加参数),
        ctypes.c_bool(是否主线程调用)
    )

    return ret


# INT64 __stdcall HDHK_HookEx (__int32 窗口序号, char *所属模块名字, __int64 hook地址, __int32 破坏字节, __int64 回调地址, __int64 附加参数, BOOL 是否主线程调用 = FALSE);
def HDHOOK_挂钩Ex(窗口序号: int,模块名字:str, hook地址: int, 破坏字节: int, 回调地址: HD_HandleCallBackFunTypeHook_stdcall, 附加参数: int, 是否主线程调用: bool = False) -> int:
    """
    任意HOOK(内置插件)X64 扩展版本1
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 当前HOOK地址所属那个模块  当前HOOK地址所属那个模块  可以不指定 为0就行 但是建议指定
    :param hook地址: 当前HOOK的目标地址
    :param 破坏字节: 涉及到的汇编字节数
    :param 回调地址: 请查询手册将写好的函数填进来
    :param 附加参数: 自定义参数,此参数会传递给回调函数
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_HookEx = hd.HDHK_HookEx
    HDHK_HookEx.restype = ctypes.c_int64
    HDHK_HookEx.argtypes = [ctypes.c_int32,ctypes.c_char_p, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]

    HandleCallBackFunTypeHook_stdcall = HD_HandleCallBackFunTypeHook_stdcall(回调地址)
    HandleCallBackFunTypeHook_stdcall_ptr = ctypes.c_int64(ctypes.cast(HandleCallBackFunTypeHook_stdcall, ctypes.c_void_p).value) if HandleCallBackFunTypeHook_stdcall else ctypes.c_int64(0)

    ret = HDHK_HookEx(
        ctypes.c_int32(窗口序号),
        auto_encode(模块名字),
        ctypes.c_int64(hook地址),
        ctypes.c_int32(破坏字节),
        HandleCallBackFunTypeHook_stdcall_ptr,
        ctypes.c_int64(附加参数),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_HookExx(__int32 窗口序号, char *所属模块名字, __int64 模块首地址, __int32 模块大小, __int64 hook地址, __int32 破坏字节, __int64 回调地址, __int64 附加参数, BOOL 是否主线程调用 = FALSE);
def HDHOOK_挂钩Exx(窗口序号: int,模块名字:str, 模块首地址: int, 模块大小: int, hook地址: int, 破坏字节: int, 回调地址: HD_HandleCallBackFunTypeHook_stdcall, 附加参数: int, 是否主线程调用: bool = False) -> int:
    """
    任意HOOK(内置插件)X64 扩展版本2
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 当前HOOK地址所属那个模块  当前HOOK地址所属那个模块  可以不指定 为0就行 但是建议指定
    :param 模块首地址:HOOK地址所属模块的模块基地址
    :param 模块大小:HOOK地址所属模块的模块大小字节
    :param hook地址: 当前HOOK的目标地址
    :param 破坏字节: 涉及到的汇编字节数
    :param 回调地址: 请查询手册将写好的函数填进来
    :param 附加参数: 自定义参数,此参数会传递给回调函数
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_HookExx = hd.HDHK_HookExx
    HDHK_HookExx.restype = ctypes.c_int64
    HDHK_HookExx.argtypes = [ctypes.c_int32,ctypes.c_char_p,ctypes.c_int64,ctypes.c_int32, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]

    HandleCallBackFunTypeHook_stdcall = HD_HandleCallBackFunTypeHook_stdcall(回调地址)
    HandleCallBackFunTypeHook_stdcall_ptr = ctypes.c_int64(ctypes.cast(HandleCallBackFunTypeHook_stdcall, ctypes.c_void_p).value) if HandleCallBackFunTypeHook_stdcall else ctypes.c_int64(0)

    ret = HDHK_HookExx(
        ctypes.c_int32(窗口序号),
        auto_encode(模块名字),
        ctypes.c_int64(模块首地址),
        ctypes.c_int32(模块大小),
        ctypes.c_int64(hook地址),
        ctypes.c_int32(破坏字节),
        HandleCallBackFunTypeHook_stdcall_ptr,
        ctypes.c_int64(附加参数),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_HookExxx(__int32 窗口序号, __int64 hook地址, char *所属模块名字, __int64 jmp13空白地址, __int64 保留汇编地址, __int32 破坏字节, __int64 回调地址, __int64 附加参数, BOOL 是否主线程调用 = FALSE);
def HDHOOK_挂钩Exxx(窗口序号: int,模块名字:str, jmp13空白地址: int, 保留汇编地址: int, hook地址: int, 破坏字节: int, 回调地址: HD_HandleCallBackFunTypeHook_stdcall, 附加参数: int, 是否主线程调用: bool = False) -> int:
    """
    任意HOOK(内置插件)X64 扩展版本3
    :param 窗口序号: 窗口序号 (从1开始)
    :param 模块名字: 当前HOOK地址所属那个模块  当前HOOK地址所属那个模块  可以不指定 为0就行 但是建议指定
    :param jmp13空白地址:在当前模块的代码地址找一个空白空间 大小为13字节 用于存储jmp一些指令
    :param 保留汇编地址:用来存储破坏字节数量 +5 字节大小的空白空间的首地址 一般这个地址位于当前所属模块代码空白空间
    :param hook地址: 当前HOOK的目标地址
    :param 破坏字节: 涉及到的汇编字节数
    :param 回调地址: 请查询手册将写好的函数填进来
    :param 附加参数: 自定义参数,此参数会传递给回调函数
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_HookExxx = hd.HDHK_HookExxx
    HDHK_HookExxx.restype = ctypes.c_int64
    HDHK_HookExxx.argtypes = [ctypes.c_int32,ctypes.c_char_p,ctypes.c_int64,ctypes.c_int64, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64, ctypes.c_bool]

    HandleCallBackFunTypeHook_stdcall = HD_HandleCallBackFunTypeHook_stdcall(回调地址)
    HandleCallBackFunTypeHook_stdcall_ptr = ctypes.c_int64(ctypes.cast(HandleCallBackFunTypeHook_stdcall, ctypes.c_void_p).value) if HandleCallBackFunTypeHook_stdcall else ctypes.c_int64(0)

    ret = HDHK_HookExxx(
        ctypes.c_int32(窗口序号),
        auto_encode(模块名字),
        ctypes.c_int64(jmp13空白地址),
        ctypes.c_int64(保留汇编地址),
        ctypes.c_int64(hook地址),
        ctypes.c_int32(破坏字节),
        HandleCallBackFunTypeHook_stdcall_ptr,
        ctypes.c_int64(附加参数),
        ctypes.c_bool(是否主线程调用)
    )

    return ret


# INT64 __stdcall HDHK_PauseHook(int 窗口序号, INT64 hook地址, BOOL 是否主线程调用);
def HDHOOK_暂停挂钩(窗口序号: int, hook地址: int, 是否主线程调用: bool = False) -> int:
    """
    暂停任意HOOK(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param hook地址: 当前HOOK的目标地址
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_PauseHook = hd.HDHK_PauseHook
    HDHK_PauseHook.restype = ctypes.c_int64
    HDHK_PauseHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]

    ret = HDHK_PauseHook(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(hook地址),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_RecoverHook(int 窗口序号, INT64 hook地址, BOOL 是否主线程调用);
def HDHOOK_恢复挂钩(窗口序号: int, hook地址: int, 是否主线程调用: bool = False) -> int:
    """
    恢复任意HOOK(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param hook地址: 当前HOOK的目标地址
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_ResumeHook = hd.HDHK_RecoverHook
    HDHK_ResumeHook.restype = ctypes.c_int64
    HDHK_ResumeHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]

    ret = HDHK_ResumeHook(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(hook地址),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_UnHook(int 窗口序号, INT64 hook地址, BOOL 是否主线程调用);
def HDHOOK_卸载挂钩(窗口序号: int, hook地址: int, 是否主线程调用: bool = False) -> int:
    """
    卸载任意HOOK(内置插件)X86X64
    :param 窗口序号: 窗口序号 (从1开始)
    :param hook地址: 当前HOOK的目标地址
    :param 是否主线程调用: 需要开启才开启,一般默认就行 (默认False)
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_UnHook = hd.HDHK_UnHook
    HDHK_UnHook.restype = ctypes.c_int64
    HDHK_UnHook.argtypes = [ctypes.c_int32, ctypes.c_int64, ctypes.c_bool]

    ret = HDHK_UnHook(
        ctypes.c_int32(窗口序号),
        ctypes.c_int64(hook地址),
        ctypes.c_bool(是否主线程调用)
    )

    return ret

# INT64 __stdcall HDHK_SetProcessHookCallBackLparam(int 窗口序号, int 插件序号, INT64 raxOreax, INT64 rbxOrebx, INT64 rcxOrecx, INT64 rdxOredx, INT64 rbpOrebp, INT64 rspOresp, INT64 rsiOresi, INT64 rdiOredi, INT64 r8, INT64 r9, INT64 r10, INT64 r11, INT64 r12, INT64 r13, INT64 r14, INT64 r15, INT64 rip, int mark);
def HDHOOK_设置挂钩返回参数(窗口序号: int, 插件序号: int, raxOreax: int, rbxOrebx: int, rcxOrecx: int, rdxOredx: int, rbpOrebp: int, rspOresp: int, rsiOresi: int, rdiOredi: int, r8: int, r9: int, r10: int, r11: int, r12: int, r13: int, r14: int, r15: int, rip: int, mark: int) -> int:
    """
    设置HOOK返回参数
    :param 窗口序号: 窗口序号 (从1开始)
    :param 插件序号: 内部自动传递
    :param raxOreax: RAX/EAX寄存器值
    :param rbxOrebx: RBX/EBX寄存器值
    :param rcxOrecx: RCX/ECX寄存器值
    :param rdxOredx: RDX/EDX寄存器值
    :param rbpOrebp: RBP/EBP寄存器值
    :param rspOresp: RSP/ESP寄存器值
    :param rsiOresi: RSI/ESI寄存器值
    :param rdiOredi: RDI/EDI寄存器值
    :param r8: R8寄存器值
    :param r9: R9寄存器值
    :param r10: R10寄存器值
    :param r11: R11寄存器值
    :param r12: R12寄存器值
    :param r13: R13寄存器值
    :param r14: R14寄存器值
    :param r15: R15寄存器值
    :param rip: RIP寄存器值
    :param mark: 标记值
    :return: 返回值代码 (查看HD返回值表)
    """
    hd = Config.get_hd()

    HDHK_SetProcessHookCallBackLparam = hd.HDHK_SetProcessHookCallBackLparam
    HDHK_SetProcessHookCallBackLparam.restype = ctypes.c_int64
    HDHK_SetProcessHookCallBackLparam.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int64, ctypes.c_int64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int32
    ]

    ret = HDHK_SetProcessHookCallBackLparam(
        ctypes.c_int32(窗口序号),
        ctypes.c_int32(插件序号),
        ctypes.c_int64(raxOreax),
        ctypes.c_int64(rbxOrebx),
        ctypes.c_int64(rcxOrecx),
        ctypes.c_int64(rdxOredx),
        ctypes.c_int64(rbpOrebp),
        ctypes.c_int64(rspOresp),
        ctypes.c_int64(rsiOresi),
        ctypes.c_int64(rdiOredi),
        ctypes.c_int64(r8),
        ctypes.c_int64(r9),
        ctypes.c_int64(r10),
        ctypes.c_int64(r11),
        ctypes.c_int64(r12),
        ctypes.c_int64(r13),
        ctypes.c_int64(r14),
        ctypes.c_int64(r15),
        ctypes.c_int64(rip),
        ctypes.c_int32(mark)
    )

    return ret