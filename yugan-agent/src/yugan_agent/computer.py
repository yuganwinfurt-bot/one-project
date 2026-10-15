"""受本机确认保护的 Windows 桌面工具。"""

import ctypes
import os
import subprocess
import time
import webbrowser
from ctypes import wintypes
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field

from .tools import ToolRegistry, tool


def _require_windows() -> None:
    if os.name != "nt":
        raise RuntimeError("电脑控制工具目前只支持 Windows")


def _visible_windows() -> list[tuple[int, str, int]]:
    _require_windows()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    windows: list[tuple[int, str, int]] = []

    def collect(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        title = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title, length + 1)
        if title.value.strip():
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            windows.append((hwnd, title.value.strip(), pid.value))
        return len(windows) < 100

    user32.EnumWindows(callback_type(collect), 0)
    return windows


def _activate_window(title_contains: str) -> tuple[object, str]:
    matches = [
        item for item in _visible_windows() if title_contains.casefold() in item[1].casefold()
    ]
    if not matches:
        raise ValueError("没有找到匹配的可见窗口")
    if len(matches) > 1:
        titles = "、".join(item[1][:80] for item in matches[:5])
        raise ValueError(f"匹配到多个窗口，请提供更具体的标题：{titles}")
    hwnd, title, _ = matches[0]
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    if not user32.SetForegroundWindow(hwnd):
        raise PermissionError("Windows 未允许切换前台窗口；请先手动点一下目标窗口")
    time.sleep(0.15)
    return hwnd, title


@tool(side_effect=True, always_confirm=True)
def desktop_list_windows() -> list[dict[str, str | int]]:
    """读取桌面上可见窗口的标题和进程号，供用户确认后交给智能体判断下一步。"""
    return [{"title": title[:160], "process_id": pid} for _, title, pid in _visible_windows()[:50]]


@tool(side_effect=True, always_confirm=True)
def desktop_open_app(
    app: Literal["notepad", "calculator", "explorer", "browser"],
) -> str:
    """打开记事本、计算器、文件资源管理器或默认浏览器；不接受任意程序路径。"""
    _require_windows()
    executables = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "explorer": ["explorer.exe"],
    }
    if app == "browser":
        opened = webbrowser.open("about:blank", new=2)
        if not opened:
            raise RuntimeError("无法打开默认浏览器")
    else:
        subprocess.Popen(executables[app], close_fds=True)
    return f"已请求打开 {app}"


@tool(side_effect=True, always_confirm=True)
def desktop_open_url(url: Annotated[str, Field(min_length=8, max_length=2048)]) -> str:
    """在默认浏览器打开 HTTP/HTTPS 网页；用户会先看到完整网址并确认。"""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("只允许打开完整的 HTTP 或 HTTPS 网址")
    if parsed.username or parsed.password:
        raise ValueError("网址中不能包含用户名或密码")
    if not webbrowser.open(url, new=2):
        raise RuntimeError("无法打开默认浏览器")
    return "已请求在默认浏览器打开网页"


@tool(side_effect=True, always_confirm=True)
def desktop_focus_window(
    title_contains: Annotated[str, Field(min_length=1, max_length=100)],
) -> str:
    """按窗口标题的一部分切换到已打开窗口；匹配不唯一时会返回候选标题。"""
    _, title = _activate_window(title_contains)
    return f"已切换到窗口：{title[:160]}"


class _KeyboardInput(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _InputUnion(ctypes.Union):
    _fields_ = [("ki", _KeyboardInput)]


class _Input(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD), ("union", _InputUnion)]


def _keyboard_event(virtual_key: int, scan_code: int, flags: int) -> _Input:
    keyboard = _KeyboardInput(virtual_key, scan_code, flags, 0, 0)
    return _Input(1, _InputUnion(keyboard))


def _send_keys(inputs: list[_Input]) -> None:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(_Input), ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    array_type = _Input * len(inputs)
    array = array_type(*inputs)
    sent = user32.SendInput(len(inputs), array, ctypes.sizeof(_Input))
    if sent != len(inputs):
        raise OSError(ctypes.get_last_error(), "Windows 未能发送全部键盘输入")


@tool(side_effect=True, always_confirm=True)
def desktop_click(
    x: Annotated[int, Field(ge=0, le=10000)],
    y: Annotated[int, Field(ge=0, le=10000)],
    button: Literal["left", "right", "middle"] = "left",
) -> str:
    """在主屏幕指定像素位置单击；坐标和按键会先显示给用户确认。"""
    _require_windows()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    user32.SetCursorPos.restype = wintypes.BOOL
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if x >= width or y >= height:
        raise ValueError(f"坐标超出主屏幕范围（{width}×{height}）")
    if not user32.SetCursorPos(x, y):
        raise OSError(ctypes.get_last_error(), "无法移动鼠标指针")
    flags = {
        "left": (0x0002, 0x0004),
        "right": (0x0008, 0x0010),
        "middle": (0x0020, 0x0040),
    }[button]
    user32.mouse_event.argtypes = [
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_size_t,
    ]
    user32.mouse_event.restype = None
    user32.mouse_event(flags[0], 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(flags[1], 0, 0, 0, 0)
    return f"已在主屏幕坐标 ({x}, {y}) 执行 {button} 键单击"


@tool(side_effect=True, always_confirm=True)
def desktop_type_text(
    window_title_contains: Annotated[str, Field(min_length=1, max_length=100)],
    text: Annotated[str, Field(min_length=1, max_length=2000)],
) -> str:
    """先切换到指定标题的窗口，再输入文字；确认前请检查窗口和完整文字。"""
    _require_windows()
    _, title = _activate_window(window_title_contains)
    events: list[_Input] = []
    for character in text:
        encoded = character.encode("utf-16-le")
        for index in range(0, len(encoded), 2):
            code_unit = int.from_bytes(encoded[index : index + 2], "little")
            events.append(_keyboard_event(0, code_unit, 0x0004))
            events.append(_keyboard_event(0, code_unit, 0x0004 | 0x0002))
    _send_keys(events)
    return f"已向窗口“{title[:100]}”输入 {len(text)} 个字符"


@tool(side_effect=True, always_confirm=True)
def desktop_press_keys(
    window_title_contains: Annotated[str, Field(min_length=1, max_length=100)],
    chord: Annotated[str, Field(min_length=1, max_length=24)],
) -> str:
    """切换到指定标题的窗口，再发送有限的常用快捷键白名单。"""
    _require_windows()
    _, title = _activate_window(window_title_contains)
    allowed = {
        "ENTER": [0x0D],
        "TAB": [0x09],
        "ESC": [0x1B],
        "BACKSPACE": [0x08],
        "DELETE": [0x2E],
        "CTRL+A": [0x11, 0x41],
        "CTRL+C": [0x11, 0x43],
        "CTRL+V": [0x11, 0x56],
        "CTRL+S": [0x11, 0x53],
        "CTRL+L": [0x11, 0x4C],
        "CTRL+Z": [0x11, 0x5A],
        "CTRL+Y": [0x11, 0x59],
        "CTRL+SHIFT+S": [0x11, 0x10, 0x53],
        "ALT+TAB": [0x12, 0x09],
        "ALT+F4": [0x12, 0x73],
        "WIN+D": [0x5B, 0x44],
    }
    normalized = chord.strip().upper().replace(" ", "")
    virtual_keys = allowed.get(normalized)
    if virtual_keys is None:
        raise ValueError("快捷键不在允许列表中")
    events = [_keyboard_event(key, 0, 0) for key in virtual_keys]
    events.extend(_keyboard_event(key, 0, 0x0002) for key in reversed(virtual_keys))
    _send_keys(events)
    return f"已向窗口“{title[:100]}”发送快捷键 {normalized}"


def register_computer_tools(registry: ToolRegistry) -> None:
    if os.name != "nt":
        return
    for entry in (
        desktop_list_windows,
        desktop_open_app,
        desktop_open_url,
        desktop_focus_window,
        desktop_type_text,
        desktop_press_keys,
        desktop_click,
    ):
        registry.register(entry)
