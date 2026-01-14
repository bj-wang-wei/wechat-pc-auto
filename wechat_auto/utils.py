import pyperclip
import os
import ctypes
from ctypes import wintypes, windll
from .logger import log

def set_clipboard(text: str):
    """将文本放入剪贴板（支持换行）"""
    pyperclip.copy(text)


def set_clipboard_files(paths: list[str]):
    """
    将一个或多个文件路径放入剪贴板，用于模拟“复制文件 → Ctrl+V”发送
    支持图片、文档、视频等所有微信支持的类型
    已彻底修复 64 位 OverflowError
    """
    if not paths:
        return False

    # 转为绝对路径并过滤不存在的文件
    abs_paths = [os.path.abspath(p) for p in paths if os.path.exists(p)]
    if not abs_paths:
        log.error("[utils] 文件路径不存在")
        return False

    # ==================== 关键修复：完整定义所有相关 API 的类型 ====================
    kernel32 = windll.kernel32
    user32 = windll.user32

    # GlobalAlloc
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

    # GlobalLock - 必须返回 c_void_p，否则指针会被当成 int 导致溢出！
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    # GlobalUnlock
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    # GlobalFree（失败时释放内存用）
    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.restype = wintypes.HGLOBAL

    # OpenClipboard / CloseClipboard / EmptyClipboard
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.argtypes = ()
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.argtypes = ()
    user32.CloseClipboard.restype = wintypes.BOOL

    # SetClipboardData
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    # ==============================================================================

    # DROPFILES 结构
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", wintypes.DWORD),
            ("pt", wintypes.POINT),
            ("fNC", wintypes.BOOL),
            ("fWide", wintypes.BOOL),
        ]

    # 构建文件路径数据（宽字符，双 null 结尾）
    file_data = "".join(p + "\0" for p in abs_paths) + "\0"
    raw_data = file_data.encode("utf-16le")

    total_size = ctypes.sizeof(DROPFILES) + len(raw_data)

    # 分配内存（使用标准标志 0x0042 = GMEM_MOVEABLE | GMEM_ZEROINIT）
    hglobal = kernel32.GlobalAlloc(0x0042, total_size)
    if not hglobal:
        log.error("[utils] GlobalAlloc 失败")
        return False

    locked_mem = kernel32.GlobalLock(hglobal)
    if not locked_mem:
        log.error("[utils] GlobalLock 失败")
        kernel32.GlobalFree(hglobal)
        return False

    try:
        dropfiles = DROPFILES()
        dropfiles.pFiles = ctypes.sizeof(DROPFILES)
        dropfiles.pt = wintypes.POINT(0, 0)  # 可选：设置坐标
        dropfiles.fNC = False
        dropfiles.fWide = True

        # 写入内存：先写结构体，再写路径数据
        ctypes.memmove(locked_mem, ctypes.byref(dropfiles), ctypes.sizeof(dropfiles))
        ctypes.memmove(locked_mem + ctypes.sizeof(dropfiles), raw_data, len(raw_data))

    finally:
        kernel32.GlobalUnlock(hglobal)

    # 放入剪贴板
    success = False
    if user32.OpenClipboard(None):
        user32.EmptyClipboard()
        if user32.SetClipboardData(15, hglobal):  # 15 = CF_HDROP
            success = True
        user32.CloseClipboard()

    if not success:
        kernel32.GlobalFree(hglobal)
        log.error("[utils] 放入剪贴板失败")
        return False

    return True
