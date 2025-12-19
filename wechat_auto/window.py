# wx_auto/window.py
import uiautomation as auto
import time
from .logger import log


class WeChatWindow:
    def __init__(self):
        self.window = None

    def load(self) -> bool:
        """激活并获取微信主窗口（自动适配不同版本的 ClassName）"""
        log("发送 Ctrl+Alt+W 激活微信窗口...")
        auto.SendKeys("{Ctrl}{Alt}w")
        time.sleep(3.0)  # 多等一点，确保微信完全响应

        # 尝试常见的几种 ClassName
        possible_classes = [
            "WeChatMainWndForPC",  # 3.9.x 新版最常见
            "WeChatMainWnd",
            "WeChatLoginWndForPC",  # 登录窗口（万一没登录）
        ]

        for cls in possible_classes:
            self.window = auto.WindowControl(searchDepth=1, ClassName=cls)
            if self.window.Exists():
                log(f"找到微信窗口，ClassName = '{cls}'")
                break

        # 如果上面都没找到，用标题包含“微信”兜底
        if not self.window or not self.window.Exists():
            log("常见 ClassName 未匹配，使用标题查找...")
            self.window = auto.WindowControl(searchDepth=1, NameContains="微信")
            if self.window.Exists():
                actual_class = self.window.ClassName or "未知"
                log(f"通过标题找到微信窗口，ClassName = '{actual_class}'")

        # 最终检查
        if not self.window or not self.window.Exists():
            log("最终仍未找到微信主窗口，请手动打开微信并确保已登录")
            return False

        # 恢复最小化窗口
        if self.window.IsMinimize():  
            log("检测到微信最小化，正在恢复窗口...")
            self.window.Restore()

        self.window.SwitchToThisWindow()
        log("微信窗口已成功激活并置于前台")
        return True

    def get_current_sessions(self) -> list:
        """获取当前会话列表（前20个）"""
        if not self.window or not self.window.Exists():
            return []

        self.window.SwitchToThisWindow()
        time.sleep(0.5)

        session_list = self.window.ListControl(Name="会话")
        if not session_list.Exists():
            return []

        items = session_list.GetChildren()
        names = []
        for item in items[:20]:
            name = item.Name.strip()
            if name and name not in names:
                names.append(name)

        log(f"获取到 {len(names)} 个会话")
        return names

    def get_window(self):
        return self.window
