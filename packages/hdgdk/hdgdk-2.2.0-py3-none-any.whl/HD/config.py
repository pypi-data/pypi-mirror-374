import ctypes
from enum import Enum

class HD配置(Enum):
    HD缓冲区大小 = 1024 * 200
    HD多开数量 = 62

class Config:
    _hd = None

    @staticmethod
    def load_dll(dll_path):
        try:
            Config._hd = ctypes.windll.LoadLibrary(dll_path)
        except Exception as e:
            print(f"加载DLL失败: {e}")

    @staticmethod
    def get_hd():
        return Config._hd


# ============================================自动转码
def auto_encode(text: str) -> bytes:
    """
    自动编码函数，根据文本内容选择合适的编码方式
    Args:
        text: 要编码的字符串
    Returns:
        bytes: 编码后的字节数组
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")
    
    try:
        # 检查是否包含中文字符
        if any('\u4e00' <= ch <= '\u9fff' for ch in text):
            return text.encode('gbk')
        else:
            return text.encode('utf-8')
    except UnicodeEncodeError:
        # 如果GBK编码失败，尝试UTF-8
        try:
            return text.encode('utf-8')
        except UnicodeEncodeError:
            # 如果UTF-8也失败，使用错误替换策略
            return text.encode('utf-8', errors='replace')