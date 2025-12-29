# wx_auto/core.py
from .chat import open_chat 
from .window import WeChatWindow
from .chat import open_chat
from .sender import send_message, send_files
from .listener import get_unread_chats, get_last_message
import time
from .logger import log


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

    def listen(self, callback, interval: float = 2):
        """
        开始监听新消息并自动回复
        :param callback: def callback(name: str, content: str) -> str | None
        :param interval: 检查间隔（秒）
        """
        self._running = True  # 开始运行
        log("开始监听新消息...")

        last_processed_msg = {}  # 去重缓存：{hash: timestamp}

        while self._running:
            try:
                window = self._window_manager.window
                if not window or not window.Exists():
                    time.sleep(interval)
                    continue

                # 1. 获取所有有未读消息的会话
                unread_names = get_unread_chats(window)
                for name in unread_names:
                    # 简单去重（每分钟只处理一次该联系人）
                    minute_key = f"{name}_{int(time.time() // 60)}"
                    if minute_key in last_processed_msg:
                        continue

                    # 2. 打开聊天窗口（调用 chat.py 中的独立函数）
                    if not open_chat(window, name):
                        log(f"打开 [{name}] 聊天失败，跳过")
                        continue

                    time.sleep(1.2)

                    # 3. 读取最新消息
                    content = get_last_message(window)
                    if not content:
                        continue

                    # 精确去重
                    content_key = f"{name}_{content}"
                    if content_key in last_processed_msg:
                        continue

                    log(f"收到来自 [{name}] 的新消息: {content}")

                    # 4. 调用用户回调获取回复内容
                    reply = callback(name, content, self)
                    if reply:
                        # 如果你有独立的 send_message 函数：
                        send_message(window, reply)

                        # 或者如果你实现了 self.send_msg：
                        # self.send_msg(reply)

                        log(f"已自动回复 [{name}]: {reply}")

                    # 记录已处理
                    last_processed_msg[minute_key] = time.time()
                    last_processed_msg[content_key] = time.time()

                # 清理过旧缓存
                if len(last_processed_msg) > 200:
                    last_processed_msg.clear()

                if not self._running:
                    break

            except Exception as e:
                log(f"监听运行中出错: {e}")

            time.sleep(interval)

    def stop_listening(self):
        """外部调用此方法可停止监听"""
        log("正在请求停止监听...")
        self._running = False
