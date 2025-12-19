# wx_auto/clipboard.py  
import ctypes
from ctypes import wintypes
import os
from .logger import log

# Windows API 常量
CF_HDROP = 15
GMEM_MOVEABLE = 0x0002


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


def copy_files_to_clipboard(file_paths: list[str]) -> bool:
    """真正将文件复制到剪贴板（修复 OverflowError）"""
    valid_paths = [os.path.abspath(p) for p in file_paths if os.path.isfile(p)]
    if not valid_paths:
        log("没有有效的文件路径")
        return False

    # 使用 GBK 编码路径（Windows 要求）
    files_str = "\0".join(valid_paths) + "\0\0"
    data = files_str.encode("gbk")

    dropfiles_size = ctypes.sizeof(DROPFILES)
    total_size = dropfiles_size + len(data)

    # 分配全局内存
    hglobal = ctypes.windll.kernel32.GlobalAlloc(GMEM_MOVEABLE, total_size)
    if not hglobal:
        log("GlobalAlloc 失败")
        return False

    try:
        locked = ctypes.windll.kernel32.GlobalLock(hglobal)
        if not locked:
            log("GlobalLock 失败")
            return False

        # 写入 DROPFILES 结构
        dropfiles = DROPFILES.from_address(locked)
        dropfiles.pFiles = dropfiles_size
        dropfiles.pt.x = 0
        dropfiles.pt.y = 0
        dropfiles.fNC = False
        dropfiles.fWide = False

        # 使用 Python 的 memmove（更安全，避免溢出）
        dest = locked + dropfiles_size
        ctypes.memmove(dest, data, len(data))

        ctypes.windll.kernel32.GlobalUnlock(hglobal)

        # 放入剪贴板
        if ctypes.windll.user32.OpenClipboard(0):
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(CF_HDROP, hglobal)
            ctypes.windll.user32.CloseClipboard()
            log(f"成功将 {len(valid_paths)} 个文件复制到剪贴板：{valid_paths}")
            return True
        else:
            log("无法打开剪贴板")
            return False

    except Exception as e:
        log(f"复制文件到剪贴板异常：{e}")
        return False
    finally:
        # 注意：不要 GlobalFree(hglobal)，剪贴板会接管所有权
        pass
