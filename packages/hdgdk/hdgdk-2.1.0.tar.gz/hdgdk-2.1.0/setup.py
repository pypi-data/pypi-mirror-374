import setuptools
import os

# 读取README内容作为项目描述
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    # 如果没有README.md文件，使用简短描述
    long_description = "HDGDK是一个功能丰富的Python工具包，提供多种系统操作和开发工具。"

# 获取lib目录下的所有dll文件
dll_files = []
if os.path.exists("lib"):
    for file in os.listdir("lib"):
        if file.endswith(".dll"):
            dll_files.append(os.path.join("lib", file))

setuptools.setup(
    name="hdgdk",  # 包的名称
    version="2.1.0",  # 版本号
    author="zhangsan",  # 作者名称
    author_email="3258856837@example.com",  # 作者邮箱
    description="HDGDK - Python工具开发包",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhangsan/hdgdk",  # 项目URL
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
    package_data={
        'HD': ['*.py'],  # 包含HD包中的所有.py文件
    },
    # 对于DLL文件，我们使用data_files来确保它们被正确安装
    data_files=[
        ('lib', dll_files)  # 将DLL文件安装到Python的lib目录
    ],
    include_package_data=True,
)