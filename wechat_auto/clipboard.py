# wx_auto/clipboard.py
import ctypes
from ctypes import wintypes
import os
from .logger import log

# Windows API 常量
CF_HDROP = 15
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040


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
    """
    将文件路径复制到剪贴板（支持 Unicode 路径，兼容 64 位 Python）
    """
    valid_paths = [os.path.abspath(p) for p in file_paths if os.path.exists(p)]
    if not valid_paths:
        log("没有有效的文件路径")
        return False

    # 使用 utf-16le 编码（现代 Windows 更推荐，支持完整 Unicode）
    # 以 null 字符分隔，最后再加一个 null
    file_data_str = "\0".join(valid_paths) + "\0"
    file_data = file_data_str.encode("utf-16le")

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # ── 非常重要：设置函数类型签名，防止 64 位指针溢出 ──
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL

    user32.EmptyClipboard.restype = wintypes.BOOL

    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE

    user32.CloseClipboard.restype = wintypes.BOOL

    dropfiles_size = ctypes.sizeof(DROPFILES)
    total_size = dropfiles_size + len(file_data)

    hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, total_size)
    if not hglobal:
        log("GlobalAlloc 失败")
        return False

    try:
        locked_mem = kernel32.GlobalLock(hglobal)
        if not locked_mem:
            log("GlobalLock 失败")
            return False

        # 准备 DROPFILES 结构体
        df = DROPFILES()
        df.pFiles = dropfiles_size
        df.pt.x = 0
        df.pt.y = 0
        df.fNC = False
        df.fWide = True  # 重要：使用宽字符（utf-16）

        # 写入结构体头部
        ctypes.memmove(locked_mem, ctypes.byref(df), dropfiles_size)

        # 写入文件路径数据（从结构体后开始）
        ctypes.memmove(locked_mem + dropfiles_size, file_data, len(file_data))

        kernel32.GlobalUnlock(hglobal)

        # 放入剪贴板
        if not user32.OpenClipboard(None):
            log("无法打开剪贴板")
            return False

        try:
            user32.EmptyClipboard()
            if not user32.SetClipboardData(CF_HDROP, hglobal):
                log("SetClipboardData 失败")
                return False
            log(f"成功复制 {len(valid_paths)} 个文件到剪贴板")
            return True

        finally:
            user32.CloseClipboard()

    except Exception as e:
        log(f"复制文件到剪贴板异常：{e}")
        return False

    # 注意：成功时不要 GlobalFree，剪贴板会拥有这个内存块
