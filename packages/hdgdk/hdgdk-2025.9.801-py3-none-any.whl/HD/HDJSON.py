from .config import Config, ctypes
from .config import auto_encode

# JSON_HANDLE __stdcall HDJSON_Create();
def HDJSON_Create() -> int:
    """
    创建JSON对象
    
    Returns:
        int: 64位整数句柄，映射一个JSON对象
    """
    hd = Config.get_hd()
    
    HDJSON_Create = hd.HDJSON_Create
    HDJSON_Create.restype = ctypes.c_int64
    HDJSON_Create.argtypes = []
    
    ret = HDJSON_Create()
    return ret

# BOOL __stdcall HDJSON_Parse(JSON_HANDLE hJson, const char* str);
def HDJSON_Parse(JSON句柄: int, JSON字符串: str) -> bool:
    """
    JSON字符串解析（支持中文）
    
    Args:
        JSON句柄: JSON对象句柄
        JSON字符串: JSON字符串
    
    Returns:
        bool: 解析结果（见HD返回值表）
    """
    hd = Config.get_hd()
    
    HDJSON_Parse = hd.HDJSON_Parse
    HDJSON_Parse.restype = ctypes.c_bool
    HDJSON_Parse.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    
    ret = HDJSON_Parse(ctypes.c_int64(JSON句柄), auto_encode(JSON字符串))
    return ret

def HDJSON_Free(hJson: int):
    """
    接口说明:
        释放JSON对象
    函数原型：
        void __stdcall HDJSON_Free(JSON_HANDLE h);
    参数定义:
        hJson: JSON对象句柄
    返回值:
        无
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_Free = hd.HDJSON_Free
    HDJSON_Free.restype = None
    HDJSON_Free.argtypes = [ctypes.c_int64]
    HDJSON_Free(ctypes.c_int64(hJson))

def HDJSON_GetString(hJson: int, key: str) -> str:
    """
    接口说明:
        通过键从JSON对象中获取字符串值-支持中文
    函数原型：
        const char* __stdcall HDJSON_GetString(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        str: 字符串值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetString = hd.HDJSON_GetString
    HDJSON_GetString.restype = ctypes.c_char_p
    HDJSON_GetString.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    result = HDJSON_GetString(ctypes.c_int64(hJson), key_bytes)
    return result.decode('utf-8') if result else None

def HDJSON_GetInt(hJson: int, key: str) -> int:
    """
    接口说明:
        通过键从JSON对象中获取4字节整数值
    函数原型：
        int __stdcall HDJSON_GetInt(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        int: 4字节整数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetInt = hd.HDJSON_GetInt
    HDJSON_GetInt.restype = ctypes.c_int32
    HDJSON_GetInt.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetInt(ctypes.c_int64(hJson), key_bytes)

def HDJSON_GetInt64(hJson: int, key: str) -> int:
    """
    接口说明:
        通过键从JSON对象中获取8字节整数值
    函数原型：
        __int64 __stdcall HDJSON_GetInt64(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        int: 8字节整数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetInt64 = hd.HDJSON_GetInt64
    HDJSON_GetInt64.restype = ctypes.c_int64
    HDJSON_GetInt64.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetInt64(ctypes.c_int64(hJson), key_bytes)

def HDJSON_GetFloat(hJson: int, key: str) -> float:
    """
    接口说明:
        通过键从JSON对象中获取4字节浮点数值
    函数原型：
        float __stdcall HDJSON_GetFloat(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        float: 4字节浮点数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetFloat = hd.HDJSON_GetFloat
    HDJSON_GetFloat.restype = ctypes.c_float
    HDJSON_GetFloat.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetFloat(ctypes.c_int64(hJson), key_bytes)

def HDJSON_GetDouble(hJson: int, key: str) -> float:
    """
    接口说明:
        通过键从JSON对象中获取8字节浮点数值
    函数原型：
        double __stdcall HDJSON_GetDouble(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        float: 8字节浮点数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetDouble = hd.HDJSON_GetDouble
    HDJSON_GetDouble.restype = ctypes.c_double
    HDJSON_GetDouble.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetDouble(ctypes.c_int64(hJson), key_bytes)

def HDJSON_GetBool(hJson: int, key: str) -> bool:
    """
    接口说明:
        通过键从JSON对象中获取4字节逻辑型数值
    函数原型：
        BOOL __stdcall HDJSON_GetBool (JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        bool: 4字节逻辑型数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetBool = hd.HDJSON_GetBool
    HDJSON_GetBool.restype = ctypes.c_bool
    HDJSON_GetBool.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetBool(ctypes.c_int64(hJson), key_bytes)

def HDJSON_GetArray(hJson: int, key: str) -> int:
    """
    接口说明:
        通过键从JSON对象中获取JSON数组对象
    函数原型：
        JSON_HANDLE __stdcall HDJSON_GetArray(JSON_HANDLE hJson, const char* key);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
    返回值:
        JSON_HANDLE: 64位整数句柄,映射一个JSON对象
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetArray = hd.HDJSON_GetArray
    HDJSON_GetArray.restype = ctypes.c_int64
    HDJSON_GetArray.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    return HDJSON_GetArray(ctypes.c_int64(hJson), key_bytes)

def HDJSON_CreateArray() -> int:
    """
    接口说明:
        创建json数组对象
    函数原型：
        JSON_HANDLE __stdcall HDJSON_CreateArray ();
    参数定义:
        无
    返回值:
        JSON_HANDLE: 64位整数句柄,映射一个JSON对象
    备注:
        见HD返回值表
    """
    hd = Config.get_hd()
    HDJSON_CreateArray = hd.HDJSON_CreateArray
    HDJSON_CreateArray.restype = ctypes.c_int64
    HDJSON_CreateArray.argtypes = []
    return HDJSON_CreateArray()

def HDJSON_ArraySize(hArray: int) -> int:
    """
    接口说明:
        获取JSON数组对象的元素大小
    函数原型：
        int __stdcall HDJSON_ArraySize(JSON_HANDLE hArray);
    参数定义:
        hArray: JSON对象句柄
    返回值:
        int: 元素数量
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArraySize = hd.HDJSON_ArraySize
    HDJSON_ArraySize.restype = ctypes.c_int32
    HDJSON_ArraySize.argtypes = [ctypes.c_int64]
    return HDJSON_ArraySize(ctypes.c_int64(hArray))

def HDJSON_ArrayGetInt(hArray: int, index: int) -> int:
    """
    接口说明:
        通过键从JSON数组对象中获取4字节整数值
    函数原型：
        int __stdcall HDJSON_ArrayGetInt (JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        int: 4字节整数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetInt = hd.HDJSON_ArrayGetInt
    HDJSON_ArrayGetInt.restype = ctypes.c_int32
    HDJSON_ArrayGetInt.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetInt(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_ArrayGetInt64(hArray: int, index: int) -> int:
    """
    接口说明:
        通过键从JSON数组对象中获取8字节整数值
    函数原型：
        __int64 __stdcall HDJSON_ArrayGetInt64(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        int: 8字节整数值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetInt64 = hd.HDJSON_ArrayGetInt64
    HDJSON_ArrayGetInt64.restype = ctypes.c_int64
    HDJSON_ArrayGetInt64.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetInt64(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_ArrayGetString(hArray: int, index: int) -> str:
    """
    接口说明:
        通过键从JSON数组对象中获取字符串值 -支持中文
    函数原型：
        const char* __stdcall HDJSON_ArrayGetString(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        str: 字符串值
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetString = hd.HDJSON_ArrayGetString
    HDJSON_ArrayGetString.restype = ctypes.c_char_p
    HDJSON_ArrayGetString.argtypes = [ctypes.c_int64, ctypes.c_int32]
    result = HDJSON_ArrayGetString(ctypes.c_int64(hArray), ctypes.c_int32(index))
    return result.decode('utf-8') if result else None

def HDJSON_ArrayGetFloat(hArray: int, index: int) -> float:
    """
    接口说明:
        通过键从JSON数组对象中获取4字节浮点数值
    函数原型：
        float __stdcall HDJSON_ArrayGetFloat(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        float: 4字节浮点数
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetFloat = hd.HDJSON_ArrayGetFloat
    HDJSON_ArrayGetFloat.restype = ctypes.c_float
    HDJSON_ArrayGetFloat.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetFloat(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_ArrayGetDouble(hArray: int, index: int) -> float:
    """
    接口说明:
        通过键从JSON数组对象中获取8节浮点数值
    函数原型：
        double __stdcall HDJSON_ArrayGetDouble(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        float: 8字节浮点数
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetDouble = hd.HDJSON_ArrayGetDouble
    HDJSON_ArrayGetDouble.restype = ctypes.c_double
    HDJSON_ArrayGetDouble.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetDouble(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_ArrayGetBool(hArray: int, index: int) -> bool:
    """
    接口说明:
        通过键从JSON数组对象中获取逻辑性值
    函数原型：
        BOOL __stdcall HDJSON_ArrayGetBool(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        bool: 4字节逻辑型
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetBool = hd.HDJSON_ArrayGetBool
    HDJSON_ArrayGetBool.restype = ctypes.c_bool
    HDJSON_ArrayGetBool.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetBool(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_ArrayGetObject(hArray: int, index: int) -> int:
    """
    接口说明:
        通过键从JSON数组对象中获取json对象
    函数原型：
        JSON_HANDLE __stdcall HDJSON_ArrayGetObject(JSON_HANDLE hArray, int index);
    参数定义:
        hArray: JSON对象句柄
        index: 元素索引 从0开始
    返回值:
        JSON_HANDLE: 64位整数句柄,映射一个JSON对象
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayGetObject = hd.HDJSON_ArrayGetObject
    HDJSON_ArrayGetObject.restype = ctypes.c_int64
    HDJSON_ArrayGetObject.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayGetObject(ctypes.c_int64(hArray), ctypes.c_int32(index))

def HDJSON_SetString(hJson: int, key: str, value: str) -> bool:
    """
    接口说明:
        向JSON对象中插入一个字符串类型的键值对-支持中文
    函数原型：
        BOOL __stdcall HDJSON_SetString(JSON_HANDLE hJson, const char* key, const char* value);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        value: 字符串 ascii编码 支持中文
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetString = hd.HDJSON_SetString
    HDJSON_SetString.restype = ctypes.c_bool
    HDJSON_SetString.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_char_p]
    key_bytes = auto_encode(key)
    value_bytes = auto_encode(value)
    return HDJSON_SetString(ctypes.c_int64(hJson), key_bytes, value_bytes)

def HDJSON_SetInt(hJson: int, key: str, value: int) -> bool:
    """
    接口说明:
        向JSON对象中插入一个4字节整数类型的键值对
    函数原型：
        BOOL __stdcall HDJSON_SetInt(JSON_HANDLE hJson, const char* key, int value);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        value: 4字节整数值
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetInt = hd.HDJSON_SetInt
    HDJSON_SetInt.restype = ctypes.c_bool
    HDJSON_SetInt.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32]
    key_bytes = auto_encode(key)
    return HDJSON_SetInt(ctypes.c_int64(hJson), key_bytes, ctypes.c_int32(value))

def HDJSON_SetInt64(hJson: int, key: str, value: int) -> bool:
    """
    接口说明:
        向JSON对象中插入一个8字节整数类型的键值对
    函数原型：
        BOOL __stdcall HDJSON_SetInt64(JSON_HANDLE hJson, const char* key, __int64 value);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        value: 8字节整数值
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetInt64 = hd.HDJSON_SetInt64
    HDJSON_SetInt64.restype = ctypes.c_bool
    HDJSON_SetInt64.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64]
    key_bytes = auto_encode(key)
    return HDJSON_SetInt64(ctypes.c_int64(hJson), key_bytes, ctypes.c_int64(value))

def HDJSON_SetDouble(hJson: int, key: str, value: float) -> bool:
    """
    接口说明:
        向JSON对象中插入一个8字节浮点数类型的键值对
    函数原型：
        BOOL __stdcall HDJSON_SetDouble(JSON_HANDLE hJson, const char* key, double value);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        value: 8字节浮点数值
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetDouble = hd.HDJSON_SetDouble
    HDJSON_SetDouble.restype = ctypes.c_bool
    HDJSON_SetDouble.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_double]
    key_bytes = auto_encode(key)
    return HDJSON_SetDouble(ctypes.c_int64(hJson), key_bytes, ctypes.c_double(value))

def HDJSON_SetBool(hJson: int, key: str, value: bool) -> bool:
    """
    接口说明:
        向JSON对象中插入一个4字节逻辑型类型的键值对
    函数原型：
        BOOL __stdcall HDJSON_SetBool(JSON_HANDLE hJson, const char* key, BOOL value);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        value: 4字节逻辑型值
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetBool = hd.HDJSON_SetBool
    HDJSON_SetBool.restype = ctypes.c_bool
    HDJSON_SetBool.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_bool]
    key_bytes = auto_encode(key)
    return HDJSON_SetBool(ctypes.c_int64(hJson), key_bytes, ctypes.c_bool(value))

def HDJSON_SetArray(hJson: int, key: str, hArray: int) -> bool:
    """
    接口说明:
        向JSON对象中插入一个json数组对象类型的键值对
    函数原型：
        BOOL __stdcall HDJSON_SetArray(JSON_HANDLE hJson, const char* key, JSON_HANDLE hArray);
    参数定义:
        hJson: JSON对象句柄
        key: 键名 不支持中文
        hArray: json数组对象句柄
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_SetArray = hd.HDJSON_SetArray
    HDJSON_SetArray.restype = ctypes.c_bool
    HDJSON_SetArray.argtypes = [ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64]
    key_bytes = auto_encode(key)
    return HDJSON_SetArray(ctypes.c_int64(hJson), key_bytes, ctypes.c_int64(hArray))

def HDJSON_ArrayAddString(hArray: int, value: str) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个字符串的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddString(JSON_HANDLE hArray, const char* value);
    参数定义:
        hArray: JSON对象句柄
        value: 字符串元素 支持中文
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddString = hd.HDJSON_ArrayAddString
    HDJSON_ArrayAddString.restype = ctypes.c_bool
    HDJSON_ArrayAddString.argtypes = [ctypes.c_int64, ctypes.c_char_p]
    value_bytes = auto_encode(value)
    return HDJSON_ArrayAddString(ctypes.c_int64(hArray), value_bytes)

def HDJSON_ArrayAddInt(hArray: int, value: int) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个4字节整数的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddInt(JSON_HANDLE hArray, int value);
    参数定义:
        hArray: JSON对象句柄
        value: 4字节整数值
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddInt = hd.HDJSON_ArrayAddInt
    HDJSON_ArrayAddInt.restype = ctypes.c_bool
    HDJSON_ArrayAddInt.argtypes = [ctypes.c_int64, ctypes.c_int32]
    return HDJSON_ArrayAddInt(ctypes.c_int64(hArray), ctypes.c_int32(value))

def HDJSON_ArrayAddDouble(hArray: int, value: float) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个8字节浮点数的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddDouble(JSON_HANDLE hArray, double value);
    参数定义:
        hArray: JSON对象句柄
        value: 8字节浮点数
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddDouble = hd.HDJSON_ArrayAddDouble
    HDJSON_ArrayAddDouble.restype = ctypes.c_bool
    HDJSON_ArrayAddDouble.argtypes = [ctypes.c_int64, ctypes.c_double]
    return HDJSON_ArrayAddDouble(ctypes.c_int64(hArray), ctypes.c_double(value))

def HDJSON_ArrayAddFloat(hArray: int, value: float) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个4字节浮点数的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddFloat(JSON_HANDLE hArray, float value);
    参数定义 :
        hArray: JSON对象句柄
        value: 4字节浮点数
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddFloat = hd.HDJSON_ArrayAddFloat
    HDJSON_ArrayAddFloat.restype = ctypes.c_bool
    HDJSON_ArrayAddFloat.argtypes = [ctypes.c_int64, ctypes.c_float]
    return HDJSON_ArrayAddFloat(ctypes.c_int64(hArray), ctypes.c_float(value))

def HDJSON_ArrayAddInt64(hArray: int, value: int) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个8字节整数的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddInt64(JSON_HANDLE hArray, __int64 value);
    参数定义 :
        hArray: JSON对象句柄
        value: 8字节整数
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddInt64 = hd.HDJSON_ArrayAddInt64
    HDJSON_ArrayAddInt64.restype = ctypes.c_bool
    HDJSON_ArrayAddInt64.argtypes = [ctypes.c_int64, ctypes.c_int64]
    return HDJSON_ArrayAddInt64(ctypes.c_int64(hArray), ctypes.c_int64(value))

def HDJSON_ArrayAddBool(hArray: int, value: bool) -> bool:
    """
    接口说明:
        向JSON数组对象中插入一个4字节逻辑型的元素
    函数原型：
        BOOL __stdcall HDJSON_ArrayAddBool(JSON_HANDLE hArray, BOOL value);
    参数定义 :
        hArray: JSON对象句柄
        value: 4字节逻辑型
    返回值:
        bool: 见HD返回值表
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ArrayAddBool = hd.HDJSON_ArrayAddBool
    HDJSON_ArrayAddBool.restype = ctypes.c_bool
    HDJSON_ArrayAddBool.argtypes = [ctypes.c_int64, ctypes.c_bool]
    return HDJSON_ArrayAddBool(ctypes.c_int64(hArray), ctypes.c_bool(value))

def HDJSON_ToString(hJson: int) -> str:
    """
    接口说明:
        通过JSON对象返回字符串形式的JSON字符串
    函数原型：
        const char* __stdcall HDJSON_ToString(JSON_HANDLE hJson);
    参数定义 :
        hJson: JSON对象句柄
    返回值:
        str: JSON字符串
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_ToString = hd.HDJSON_ToString
    HDJSON_ToString.restype = ctypes.c_char_p
    HDJSON_ToString.argtypes = [ctypes.c_int64]
    result = HDJSON_ToString(ctypes.c_int64(hJson))
    return result.decode('utf-8') if result else None

def HDJSON_GetLastError() -> str:
    """
    接口说明:
        获取当前线程最近调用json接口的错误返回值
    函数原型：
        const char* __stdcall HDJSON_GetLastError();
    参数定义 :
        无
    返回值:
        str: 错误字符串
    备注:
        JSON_HANDLE 是一个64位整数句柄,映射一个JSON对象
    """
    hd = Config.get_hd()
    HDJSON_GetLastError = hd.HDJSON_GetLastError
    HDJSON_GetLastError.restype = ctypes.c_char_p
    HDJSON_GetLastError.argtypes = []
    result = HDJSON_GetLastError()
    return result.decode('utf-8') if result else None