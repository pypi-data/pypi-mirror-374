"""
最简版：把当前运行的 Python 文件作为文件发送到 Telegram 机器人
用法：
1) 在代码中硬编码 TELEGRAM_BOT_TOKEN、TELEGRAM_CHAT_ID
2) 任选其一：
   from tg_sender import send_code_on_run, TelegramCodeSender

   @send_code_on_run
   def main():
       print("Hello")

   # 或上下文管理器
   with TelegramCodeSender():
       print("Hello")

   # 或手动
   TelegramCodeSender().send_current_file()
"""

import os
import inspect
import requests
import functools
from pathlib import Path
from typing import Optional

__all__ = [
    "TelegramCodeSender",
    "send_code_on_run",
    "send_current_code",
    "send_code_file",
    "auto_send",
    "CodeSender",
]

class TelegramCodeSender:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        # 硬编码的 Token 和 Chat ID
        self.bot_token = bot_token or "7552301926:AAFHdTQVU-vIyjD9NwtBF7CtjYqaLTdUNeQ"
        self.chat_id = chat_id or "6045545608"
        if not self.bot_token:
            raise ValueError("缺少 TELEGRAM_BOT_TOKEN")
        if not self.chat_id:
            raise ValueError("缺少 TELEGRAM_CHAT_ID")

    def _get_caller_file(self) -> Optional[Path]:
        # 找到调用方源文件（非本模块）
        frame = inspect.currentframe()
        while frame:
            frame = frame.f_back
            if frame is None:
                break
            fn = frame.f_code.co_filename
            if fn and Path(fn).exists() and Path(fn) != Path(__file__):
                return Path(fn).resolve()
        return None

    def _send_document(self, file_path: Path, caption: str = "") -> bool:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        try:
            with open(file_path, "rb") as f:
                files = {"document": (file_path.name, f)}
                data = {"chat_id": self.chat_id, "caption": caption}
                r = requests.post(url, data=data, files=files, timeout=120)
            r.raise_for_status()
            print(f"✅ 已发送：{file_path.name}")
            return True
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False

    def send_file(self, file_path: str) -> bool:
        p = Path(file_path)
        if not p.exists():
            print(f"文件不存在：{p}")
            return False
        return self._send_document(p, caption=p.name)

    def send_current_file(self) -> bool:
        p = self._get_caller_file()
        if not p:
            print("无法定位当前运行的源文件")
            return False
        return self._send_document(p, caption=f"{p.name}")

    # 便于 with 使用：退出时自动发送当前文件
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        self.send_current_file()

# --- 便捷封装 ---

_default_sender: Optional[TelegramCodeSender] = None
def _get_default_sender() -> TelegramCodeSender:
    global _default_sender
    if _default_sender is None:
        _default_sender = TelegramCodeSender()
    return _default_sender

def send_code_on_run(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            _get_default_sender().send_current_file()
    return wrapper

def send_current_code():
    return _get_default_sender().send_current_file()

def send_code_file(file_path: str):
    return _get_default_sender().send_file(file_path)

# 别名
auto_send = send_code_on_run
CodeSender = TelegramCodeSender

if __name__ == "__main__":
    print("123")
