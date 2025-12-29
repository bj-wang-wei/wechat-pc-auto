# wx_auto/listener.py
import uiautomation as auto
import time
from .logger import log
import re


def extract_wechat_name(raw_name):
    """
    清洗微信会话名称
    输入: "信息助手1条新消息" 或 "张三\n2条新消息"
    输出: "信息助手" 或 "张三"
    """
    # 1. 如果有换行符，通常第一行才是真正的名字
    name = raw_name.split("\n")[0]

    # 2. 去掉 "条新消息" 关键字
    name = name.replace("条新消息", "")

    # 3. 去掉结尾的数字 (1, 2, 99+ 等)
    # [ \t]* 表示匹配空格，\d+ 表示匹配数字，[+]? 表示匹配可能存在的加号
    name = re.sub(r"[ \t]*\d+[+]?$", "", name)

    return name.strip()

def get_unread_chats(window):
    """获取所有有未读消息的联系人名称"""
    unread_chats = []
    session_list = window.ListControl(Name="会话")
    if not session_list.Exists(0):
        return []

    # 找到所有带有“未读消息”标识的项目
    # 微信的未读标记通常在 ListItemControl 的子控件中
    items = session_list.GetChildren()
    for item in items:
        # 逻辑：如果这个项目里包含数字（未读数），或者有特定的未读描述
        # 简单处理：检查 Name 中是否包含未读文字信息，或者通过子控件红点判断
        if item.TextControl(searchDepth=2).Exists(0):  # 某些版本未读数在 Text 里
            # 这里可以根据具体的 UI 树微调
            pass

        # 常用方案：直接根据 Name 查找
        # 注意：微信未读消息在 UI 树中通常表现为特定的 Name 属性
        if "未读" in item.Name or "条新消息" in item.Name:
            unread_chats.append(extract_wechat_name(item.Name))  # 提取联系人名字

    return unread_chats

def get_last_message(window):
    """获取当前聊天窗口的最后一条消息内容"""
    try:
        # 消息列表控件
        msg_list = window.ListControl(Name="消息")
        if not msg_list.Exists(0):
            return None

        # 获取最后一条消息
        all_msgs = msg_list.GetChildren()
        if not all_msgs:
            return None

        last_msg_item = all_msgs[-1]
        # 返回文本内容（排除时间等干扰）
        content = last_msg_item.Name
        return content
    except Exception as e:
        log(f"读取消息失败: {e}")
        return None
