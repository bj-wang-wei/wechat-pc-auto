# wx_auto/chat.py
import uiautomation as auto
import time
from .logger import log


def open_chat(window, name: str) -> bool:
    """智能打开聊天：优先点击左侧会话列表，如果没有再搜索"""
    if not window.Exists():
        log("微信窗口无效")
        return False

    window.SwitchToThisWindow()
    time.sleep(0.5)

    # Step 1: 先尝试在左侧会话列表中直接查找并点击
    log(f"尝试在最近会话列表中查找：{name}")
    session_list = window.ListControl(Name="会话")
    if session_list.Exists():
        target_item = session_list.ListItemControl(Name=name)
        if target_item.Exists():
            target_item.Click(simulateMove=False)
            log(f"已在最近会话列表中找到并点击：{name}")

            # 等待聊天窗口加载
            time.sleep(4.0)
            log(f"成功通过最近会话进入聊天 → {name}")
            return True

    log(f"最近会话列表中未找到 {name}，准备使用搜索方式")

    # Step 2: 搜索框方式（原来的稳定逻辑）
    search_box = window.EditControl(Name="搜索")
    if not search_box.Exists():
        log("未找到搜索框")
        return False

    search_box.Click()
    time.sleep(0.5)

    log(f"正在搜索：{name}")
    search_box.SendKeys("{Ctrl}a")
    time.sleep(0.2)
    search_box.SendKeys(name)
    time.sleep(1.0)
    search_box.SendKeys("{Enter}")

    log("已按 Enter 进入搜索结果")

    # 等待聊天界面加载完成
    time.sleep(5.0)

    log(f"成功通过搜索进入聊天 → {name}（光标已就位，可直接发送）")
    return True
