import pyperclip
import os
import ctypes
from ctypes import wintypes, windll


def set_clipboard(text: str):
    """将文本放入剪贴板（支持换行）"""
    pyperclip.copy(text)


def set_clipboard_files(paths: list[str]):
    """
    将一个或多个文件路径放入剪贴板，用于模拟“复制文件 → Ctrl+V”发送
    支持图片、文档、视频等所有微信支持的类型
    """
    if not paths:
        return False

    # 转为绝对路径并过滤不存在的文件
    abs_paths = [os.path.abspath(p) for p in paths if os.path.exists(p)]
    if not abs_paths:
        print("[utils] 文件路径不存在")
        return False

    # DROPFILES 结构
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", wintypes.DWORD),
            ("pt", wintypes.POINT),
            ("fNC", wintypes.BOOL),
            ("fWide", wintypes.BOOL),
        ]

    # 构建宽字符路径列表（双 null 结尾）
    file_data = "".join(p + "\0" for p in abs_paths) + "\0"
    raw_data = file_data.encode("utf-16le")

    total_size = ctypes.sizeof(DROPFILES) + len(raw_data)

    hglobal = windll.kernel32.GlobalAlloc(
        0x2042, total_size
    )  # GMEM_MOVEABLE | GMEM_ZEROINIT | GMEM_DDESHARE
    if not hglobal:
        return False

    locked_mem = windll.kernel32.GlobalLock(hglobal)
    if not locked_mem:
        windll.kernel32.GlobalFree(hglobal)
        return False

    dropfiles = DROPFILES()
    dropfiles.pFiles = ctypes.sizeof(DROPFILES)
    dropfiles.fWide = True

    ctypes.memmove(locked_mem, ctypes.byref(dropfiles), ctypes.sizeof(dropfiles))
    ctypes.memmove(locked_mem + ctypes.sizeof(dropfiles), raw_data, len(raw_data))

    windll.kernel32.GlobalUnlock(hglobal)

    # 放入剪贴板
    if windll.user32.OpenClipboard(None):
        windll.user32.EmptyClipboard()
        windll.user32.SetClipboardData(15, hglobal)  # 15 = CF_HDROP
        windll.user32.CloseClipboard()
        return True
    else:
        windll.kernel32.GlobalFree(hglobal)
        return False
