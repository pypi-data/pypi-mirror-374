"""
Telegram Code Sender - 一个简单的工具，用于将Python代码文件自动发送到Telegram机器人

这个库提供了多种方式来自动发送Python代码文件到Telegram：
- 装饰器方式：@send_code_on_run
- 上下文管理器方式：with TelegramCodeSender():
- 手动调用方式：TelegramCodeSender().send_current_file()

使用示例：
    from telegram_code_sender import send_code_on_run, TelegramCodeSender
    
    @send_code_on_run
    def main():
        print("Hello World")
    
    # 或者
    with TelegramCodeSender():
        print("Hello World")
"""

from .telegram_code_sender import (
    TelegramCodeSender,
    send_code_on_run,
    send_current_code,
    send_code_file,
    auto_send,
    CodeSender,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "TelegramCodeSender",
    "send_code_on_run",
    "send_current_code", 
    "send_code_file",
    "auto_send",
    "CodeSender",
    "__version__",
]
