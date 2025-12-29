# wechat_auto/__init__.py
from .core import WxAuto
from .chat import open_chat
from .sender import send_message, send_files

# 可选：如果你想直接导入 listener 相关
# from .listener import get_unread_sessions, get_latest_message

__version__ = "1.1.0"
__author__ = "wangwei"
__all__ = ["WxAuto"]
