# wechat-pc-auto

一个稳定、纯自动化、无需截图的 **微信 PC 版消息与文件发送工具**，基于 `uiautomation` 实现。

支持：
- 自动激活微信窗口（适配所有 3.9.x 版本）
- 智能打开聊天（优先点击最近会话 → 搜索回车兜底）
- 发送多行文本消息
- 发送任意类型文件（图片、视频、文档、压缩包等）
- 完全模拟手动操作，稳定可靠

适用于：定时汇报、日志推送、监控告警、文件自动传输等场景。

## 安装

```bash
git clone https://github.com/bj-wang-wei/wechat-pc-auto.git
cd wechat-pc-auto
pip install -r requirements.txt
```
## 快速开始

```python
from wechat_auto import WxAuto

wx = WxAuto()
wx.load_wechat()

wx.send_msg("你好，自动化测试成功！", who="文件传输助手")

wx.send_files([
    r"C:\test\report.pdf",
    r"C:\test\screenshot.png"
], who="文件传输助手")
```
查看完整示例：examples/demo_send_to_file_helper.py

## 注意事项

- 仅支持 Windows 系统 + 微信 PC 版
- 请确保微信已登录且未被最小化
- 首次运行可能需要管理员权限（uiautomation 需要）
- 不支持发送表情包（可发送文本中的emoji）

## 项目特点

- 无需截图识别，完全基于 UI 自动化
- 适配不同微信版本窗口类名
- 智能选择最快方式进入聊天
- 真正的文件剪贴板复制（非路径文本）
- 模块化设计，易于扩展（如后续可加接收消息、自动回复等）

## 开源协议

MIT License - 随意使用、修改、商用均可

## 致谢

感谢 uiautomation 作者 yinkaisheng，以及所有在调试过程中提供反馈的用户。

Star 支持一下吧，让更多人用上稳定的微信自动化工具


