# HD-Python模块

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

HD引擎的Python调用模块，提供丰富的Windows平台自动化控制功能，包括窗口操作、键鼠模拟、图像识别、内存读写等功能接口。

## 功能特性

HD-Python模块为Windows应用程序自动化提供了全面的功能支持：

- **环境管理**：DLL加载、调试模式设置、环境初始化
- **窗口操作**：窗口查找、窗口控制、多开管理
- **键鼠模拟**：键盘输入、鼠标控制、组合操作
- **图像识别**：截图、识图、识字、智能识图
- **内存操作**：内存读写、进程内存管理
- **系统功能**：HOOK、注入、汇编执行、多线程支持
- **网络功能**：IP操作、网络通讯
- **UI自动化**：内置浏览器控制、UI元素识别
- **高级功能**：YOLOV图像识别、黑屏模式、主板机控制

## 安装

### 使用pip安装（推荐）

```bash
pip install HD-Python
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/HD-Python.git
cd HD-Python

# 安装依赖
pip install -r requirements.txt

# 安装模块
pip install -e .
```

## 快速开始

以下是使用HD-Python模块的基本流程：

```python
from HD.HD登录 import HD_Path
from HD.HD环境 import HD环境_初始化
from HD.HD窗口 import HD窗口_获取句柄
from HD.HD键鼠 import HD键鼠_左键单击

# 1. 加载HD DLL（根据实际路径修改）
dll_path = r"./lib/"
# 加载普通版本
success = HD_Path(dll_path)
# 或加载调试版本
# success = HD_Path(dll_path, 是否调试=True)

if success:
    print("DLL加载成功")
    
    # 2. 初始化HD环境
    HD环境_初始化()
    print("HD环境初始化成功")
    
    # 3. 设置调试模式（如果需要）
    # from HD.HD环境 import HD环境_调试模式
    # HD环境_调试模式(True)  # 自动从Config获取调试模式
    
    # 4. 查找窗口
    window_handle = HD窗口_获取句柄("窗口标题")
    if window_handle:
        print(f"找到窗口，句柄: {window_handle}")
        
        # 5. 执行鼠标点击（示例坐标）
        HD键鼠_左键单击(window_handle, 100, 100)
        print("执行鼠标左键单击")
    else:
        print("未找到目标窗口")
else:
    print("DLL加载失败")
```

## 核心功能模块

### HD登录模块

提供DLL加载和登录验证功能：

```python
from HD.HD登录 import HD_Path, HD登录_登录

# 加载DLL
HD_Path("./lib/")

# 登录（如果需要）
result = HD登录_登录("账号", "密码", "应用名称", "应用参数", False, False)
print(f"登录结果: {result}")
```

### HD环境模块

管理HD运行环境：

```python
from HD.HD环境 import HD环境_初始化, HD环境_调试模式

# 初始化环境
HD环境_初始化()

# 设置调试模式（自动从Config获取）
HD环境_调试模式()
```

### HD窗口模块

窗口查找和管理：

```python
from HD.HD窗口 import HD窗口_获取句柄, HD窗口_获取标题, HD窗口_移动窗口

# 查找窗口
handle = HD窗口_获取句柄("窗口标题")

# 获取窗口标题
if handle:
    title = HD窗口_获取标题(handle)
    print(f"窗口标题: {title}")
    
    # 移动窗口
    HD窗口_移动窗口(handle, 0, 0)
```

### HD键鼠模块

键盘和鼠标操作：

```python
from HD.HD键鼠 import HD键鼠_左键单击, HD键鼠_输入文本

# 鼠标左键单击
HD键鼠_左键单击(window_handle, 100, 100)

# 输入文本
HD键鼠_输入文本("Hello, HD-Python!")
```

### HD识图模块

图像识别功能：

```python
from HD.HD识图 import HD识图_找图

# 在窗口中查找图片
x, y = HD识图_找图(window_handle, "目标图片.bmp", 0.8)
if x > -1 and y > -1:
    print(f"找到图片，位置: ({x}, {y})")
```

### HD内存模块

内存读写操作：

```python
from HD.HD内存 import HD内存_写字节集, HD内存_读字节集

# 写入内存
HD内存_写字节集(process_id, address, [0x01, 0x02, 0x03])

# 读取内存
bytes_data = HD内存_读字节集(process_id, address, 10)
```

## 高级功能

### YOLOV图像识别

```python
from HD.HDYOLOV import HDYOLOV_初始化, HDYOLOV_识别

# 初始化YOLOV模型
HDYOLOV_初始化("model_path")

# 进行识别
results = HDYOLOV_识别(window_handle)
```

### 多线程支持

```python
from HD.HD多线程 import HD多线程_创建, HD多线程_等待

# 创建多线程函数
def thread_func(param):
    # 线程执行的代码
    pass

# 创建并启动线程
thread_id = HD多线程_创建(thread_func, "参数")

# 等待线程完成
HD多线程_等待(thread_id)
```

### 黑屏模式

```python
from HD.HD黑屏 import HD黑屏_开启, HD黑屏_关闭

# 开启黑屏模式
HD黑屏_开启()

# 执行操作...

# 关闭黑屏模式
HD黑屏_关闭()
```

## API参考

完整的API文档请参考：
- [模块源码文档](HD/)
- [示例代码](demo.py)

## 注意事项

1. **DLL文件要求**：
   - 确保DLL文件（hd.dll、HDDebug.dll等）放置在正确的路径下
   - 64位系统请使用x64版本的DLL，32位系统使用x86版本

2. **调试模式**：
   - 使用HDDebug.dll时需要设置调试模式：`HD_Path(path, 是否调试=True)`
   - 调试模式下可以使用插件功能

3. **Python版本**：
   - 支持Python 3.7及以上版本
   - 在Windows平台上运行

4. **权限要求**：
   - 某些功能（如内存读写、注入等）需要管理员权限

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢所有为HD-Python模块开发和维护做出贡献的开发者！