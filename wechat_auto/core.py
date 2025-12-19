# wx_auto/core.py
from .window import WeChatWindow
from .chat import open_chat
from .sender import send_message, send_files


class WxAuto:
    def __init__(self):
        self._window_manager = WeChatWindow()
        self.window = None

    def load_wechat(self) -> bool:
        """加载微信窗口"""
        success = self._window_manager.load()
        if success:
            self.window = self._window_manager.get_window()
        return success

    def get_current_sessions(self) -> list:
        """获取当前会话列表"""
        return self._window_manager.get_current_sessions()

    def chat_with(self, name: str) -> bool:
        """打开聊天"""
        if not self.window:
            return False
        return open_chat(self.window, name)

    def send_msg(self, msg: str, who: str = None) -> bool:
        """发送文本消息"""
        if who and not self.chat_with(who):
            return False
        send_message(self.window, msg)
        return True

    def send_files(self, file_paths: list[str], who: str = None) -> bool:
        """发送文件"""
        if who and not self.chat_with(who):
            return False
        return send_files(self.window, file_paths)
