#!/usr/bin/env python3
"""
Setup script for telegram-code-sender
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取 requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["requests>=2.20.0"]

setup(
    name="telegram-code-sender",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个简单的工具，用于将Python代码文件自动发送到Telegram机器人",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",  # 可以填入你的项目主页
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    keywords="telegram, bot, code, sender, automation, developer-tools",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/telegram-code-sender/issues",
        "Source": "https://github.com/yourusername/telegram-code-sender",
    },
)
