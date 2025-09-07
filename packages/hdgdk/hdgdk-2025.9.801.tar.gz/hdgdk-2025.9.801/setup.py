#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HD-Python模块安装脚本

此脚本用于将HD-Python模块(HD目录)打包发布到PyPI或本地安装。
"""

from setuptools import setup, find_packages

# 主setup配置
setup(
    # 包元数据
    name="hdgdk",
    version="2025.9.801",
    description="HD引擎Python调用模块",
    long_description="HD引擎Python调用模块",
    long_description_content_type="text/markdown",
    author="zhangsan",
    author_email="3258856837@qq.com",
    maintainer="zhangsan",
    maintainer_email="3258856837@qq.com",
    url="https://github.com/zhangsan-ai/hd-python",
    license="MIT",
    
    # 包配置
    packages=['HD'],
    include_package_data=False,
    zip_safe=False,
    
    # Python版本要求
    python_requires=">=3.6",
)