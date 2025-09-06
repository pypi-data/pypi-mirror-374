# Telegram Code Sender

一个简单易用的 Python 库，用于自动将代码文件发送到 Telegram 机器人。

## 特性

- 🚀 **简单易用**：只需几行代码即可开始使用
- 🎯 **多种使用方式**：支持装饰器、上下文管理器、手动调用
- 📁 **自动文件检测**：自动检测并发送当前运行的 Python 文件
- 🔧 **硬编码配置**：Token 和 Chat ID 直接写在代码中，无需环境变量

## 安装

### 从源码安装

```bash
git clone https://github.com/yourusername/telegram-code-sender.git
cd telegram-code-sender
pip install .
```

### 开发模式安装

```bash
git clone https://github.com/yourusername/telegram-code-sender.git
cd telegram-code-sender
pip install -e .
```

## 快速开始

### 1. 获取 Telegram Bot Token 和 Chat ID

1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 创建新机器人并获取 Bot Token
3. 获取你的 Chat ID（可以通过 [@userinfobot](https://t.me/userinfobot) 获取）

### 2. 使用库

库已经预配置了 Token 和 Chat ID，可以直接使用：

#### 方式一：装饰器（推荐）

```python
from telegram_code_sender import send_code_on_run

@send_code_on_run
def main():
    print("Hello, World!")
    # 你的代码逻辑
    
if __name__ == "__main__":
    main()  # 函数执行完后会自动发送当前文件到 Telegram
```

#### 方式二：上下文管理器

```python
from telegram_code_sender import TelegramCodeSender

with TelegramCodeSender():
    print("Hello, World!")
    # 你的代码逻辑
# 退出 with 块时会自动发送当前文件到 Telegram
```

#### 方式三：手动调用

```python
from telegram_code_sender import TelegramCodeSender

def main():
    print("Hello, World!")
    # 你的代码逻辑
    
    # 手动发送当前文件
    TelegramCodeSender().send_current_file()

if __name__ == "__main__":
    main()
```

#### 方式四：发送指定文件

```python
from telegram_code_sender import send_code_file

# 发送指定文件
send_code_file("path/to/your/file.py")
```

## API 参考

### TelegramCodeSender

主要的发送器类。

```python
class TelegramCodeSender:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None)
    def send_current_file(self) -> bool
    def send_file(self, file_path: str) -> bool
```

### 便捷函数

- `send_code_on_run(func)` - 装饰器，函数执行完后发送当前文件
- `send_current_code()` - 发送当前运行的文件
- `send_code_file(file_path)` - 发送指定文件
- `auto_send` - `send_code_on_run` 的别名
- `CodeSender` - `TelegramCodeSender` 的别名

## 配置

### 自定义 Token 和 Chat ID

如果你需要使用不同的 Token 和 Chat ID，可以在创建实例时传入：

```python
from telegram_code_sender import TelegramCodeSender

sender = TelegramCodeSender(
    bot_token="your_custom_token",
    chat_id="your_custom_chat_id"
)
sender.send_current_file()
```

## 常见问题

### Q: 如何获取 Chat ID？
A: 你可以：
1. 使用 [@userinfobot](https://t.me/userinfobot) 获取你的用户 ID
2. 或者将机器人添加到群组中，使用群组 ID

### Q: 文件发送失败怎么办？
A: 检查：
1. Bot Token 是否正确
2. Chat ID 是否正确
3. 网络连接是否正常
4. 机器人是否有发送消息的权限

### Q: 支持哪些文件类型？
A: 理论上支持所有文件类型，但主要设计用于发送 Python 代码文件。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始发布
- 支持多种使用方式
- 自动文件检测
- 硬编码配置支持

