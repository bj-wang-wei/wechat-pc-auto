# wx_auto/logger.py
from datetime import datetime


def log(msg: str, prefix="[wx_auto]"):
    """统一日志输出，带时间戳"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{prefix} {timestamp} | {msg}")
