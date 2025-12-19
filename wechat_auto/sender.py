# wx_auto/sender.py  

import pyperclip
import time
from .logger import log
from .clipboard import copy_files_to_clipboard  # 新增导入


def send_message(window, msg: str):
    """发送文本消息（保持不变）"""
    window.SwitchToThisWindow()
    time.sleep(0.8)

    pyperclip.copy(msg)
    window.SendKeys("{Ctrl}v")
    time.sleep(0.5)
    window.SendKeys("{Enter}")

    pyperclip.copy("")  # 清理
    log(f"文本消息已发送：{msg.replace(chr(10), '\\n')}")


def send_files(window, file_paths: list[str]):
    """发送文件（使用真正的文件剪贴板复制）"""
    window.SwitchToThisWindow()
    time.sleep(0.8)

    # 真正复制文件到剪贴板
    if not copy_files_to_clipboard(file_paths):
        return False

    # Ctrl+V 粘贴文件
    window.SendKeys("{Ctrl}v")
    time.sleep(2.0)  # 给微信更多时间识别文件（尤其是多个或大文件）

    # 按 Enter 发送
    window.SendKeys("{Enter}")

    log(f"文件发送完成：{file_paths}")
    return True
