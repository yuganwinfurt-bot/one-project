"""Graphical entrypoint for the existing local project launcher."""
from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser

import start_local_projects as core
from local_admin_dialog import AdminAccountsDialog

TITLE = '我的项目 · 本地启动器'
SERVICES = {item.name: item for item in core.SERVICES}
LABELS = {
    'ollama': 'Ollama 本地模型', 'rag': 'RAG 知识库服务', 'rag_ui': 'RAG 网页',
    'agent': 'Agent 智能体', 'ecom_backend': '电商后台服务', 'ecom_ui': '电商网页', 'hub': '项目主页',
    'support_backend': '客服工单后台', 'support_ui': '客服工单网页',
}
APPLICATIONS = (
    ('项目主页', ('hub',), 'http://127.0.0.1:8030/'),
    ('电商平台', ('ecom_backend', 'ecom_ui'), f"http://127.0.0.1:{SERVICES['ecom_ui'].port}/"),
    ('客服工单系统', ('ecom_backend', 'support_backend', 'support_ui'), 'http://127.0.0.1:3000/'),
    ('Agent 智能体', ('agent',), 'http://127.0.0.1:8020/'),
    ('RAG 知识库', ('rag', 'rag_ui'), 'http://127.0.0.1:4173/'),
    ('Ollama 本地模型', ('ollama',), ''),
)
STOP_ORDER = ('hub', 'support_ui', 'support_backend', 'ecom_ui', 'ecom_backend', 'agent', 'rag_ui', 'rag', 'ollama')
LOG_KEYS = {'客服工单系统': 'support_backend', '电商平台': 'ecom_backend', 'Agent 智能体': 'agent', 'RAG 知识库': 'rag', '项目主页': 'hub', 'Ollama 本地模型': 'ollama'}


class LogWriter:
    def __init__(self, emit):
        self.emit, self.buffer = emit, ''

    def write(self, text):
        self.buffer += text
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            if line.strip():
                self.emit(line.rstrip())
        return len(text)

    def flush(self):
        if self.buffer.strip():
            self.emit(self.buffer.rstrip())
            self.buffer = ''


def describe(text):
    for key in sorted(LABELS, key=len, reverse=True):
        text = text.replace(key + ':', LABELS[key] + '：')
    text = text.replace('already running at', '已在运行：').replace('ready at', '已就绪：')
    text = text.replace('source changed; restarting the owned process', '代码有更新，正在重启本项目服务')
    text = text.replace('existing startup is still running; waiting', '已有服务正在加载，继续等待')
    text = text.replace('process already stopped', '服务已停止').replace('PID was reused; leaving that process untouched', '进程已发生变化，保留当前进程')
    return text


class ProjectWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(TITLE)
        self.window.geometry('1080x760')
        self.window.minsize(960, 650)
        self.window.configure(background='#f4f7f5')
        self.events = queue.Queue()
        self.progress_lines = deque(maxlen=1500)
        self.cancel = threading.Event()
        self.closing = threading.Event()
        self.busy = False
        self.pending_stop = set()
        self.close_requested = False
        self.shutdown_failures = set()
        self.operation = ''
        self.stopping_keys = ()
        self.started_at = None
        self.ready = {}
        self.active_service = ''
        self.log_fingerprint = None
        self.accounts_dialog = None
        style = ttk.Style(self.window)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('.', font=('Microsoft YaHei UI', 10))
        style.configure('TFrame', background='#f4f7f5')
        style.configure('TLabel', background='#f4f7f5', foreground='#19342e')
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 20, 'bold'))
        style.configure('Muted.TLabel', foreground='#78877f')
        style.configure('Ready.TLabel', foreground='#168265')
        style.configure('Error.TLabel', foreground='#b35b42')
        style.configure('TButton', padding=(14, 8))
        style.configure('Primary.TButton', background='#daf0e4', foreground='#125c46')
        style.configure('TProgressbar', background='#239c77')

        header = ttk.Frame(self.window, padding=(22, 18, 22, 12))
        header.pack(fill='x')
        ttk.Label(header, text='我的本地项目', style='Title.TLabel').pack(anchor='w')
        ttk.Label(header, text='电商平台 · 客服工单系统 · Agent 智能体 · RAG 知识库 · 项目主页', style='Muted.TLabel').pack(anchor='w', pady=(6, 0))
        controls = ttk.Frame(self.window, padding=(22, 0, 22, 12))
        controls.pack(fill='x')
        self.start_button = ttk.Button(controls, text='启动全部', style='Primary.TButton', command=self.start)
        self.start_button.pack(side='left', padx=(0, 10))
        self.stop_button = ttk.Button(controls, text='停止全部', command=self.request_stop)
        self.stop_button.pack(side='left', padx=(0, 10))
        ttk.Button(controls, text='打开项目文件夹', command=lambda: os.startfile(core.ROOT)).pack(side='left', padx=(0, 10))
        ttk.Button(controls, text='打开日志文件夹', command=self.open_logs).pack(side='left')
        self.accounts_button = ttk.Button(controls, text='管理员账号', command=self.open_accounts)
        self.accounts_button.pack(side='left', padx=(10, 0))
        self.status = tk.StringVar(value='正在读取当前项目状态…')
        self.elapsed = tk.StringVar(value='')
        status_row = ttk.Frame(self.window, padding=(22, 0, 22, 6))
        status_row.pack(fill='x')
        ttk.Label(status_row, textvariable=self.status).pack(side='left')
        ttk.Label(status_row, textvariable=self.elapsed, style='Muted.TLabel').pack(side='right')
        self.progress = ttk.Progressbar(self.window, maximum=len(SERVICES))
        self.progress.pack(fill='x', padx=22, pady=(0, 10))

        apps = ttk.Frame(self.window, padding=(22, 0, 22, 8))
        apps.pack(fill='x')
        apps.columnconfigure(1, weight=1)
        self.app_labels = {}
        self.row_buttons = []
        for index, (name, keys, url) in enumerate(APPLICATIONS):
            ttk.Label(apps, text=name, font=('Microsoft YaHei UI', 10, 'bold')).grid(row=index, column=0, sticky='w', pady=7, padx=(0, 18))
            ttk.Label(apps, text=url or '供本地模型调用使用', style='Muted.TLabel').grid(row=index, column=1, sticky='w')
            label = ttk.Label(apps, text='读取中', width=16, anchor='center', style='Muted.TLabel')
            label.grid(row=index, column=2, padx=12)
            self.app_labels[name] = label
            start_button = ttk.Button(apps, text='启动', width=5, command=lambda name=name: self.start(name))
            start_button.grid(row=index, column=3, padx=(0, 6))
            stop_button = ttk.Button(apps, text='停止', width=5, command=lambda name=name: self.request_stop(name))
            stop_button.grid(row=index, column=4, padx=(0, 6))
            self.row_buttons.extend((start_button, stop_button))
            if url:
                ttk.Button(apps, text='打开网页', width=7, command=lambda name=name, keys=keys, url=url: self.open_page(name, keys, url)).grid(row=index, column=5)

        log_bar = ttk.Frame(self.window, padding=(22, 0, 22, 7))
        log_bar.pack(fill='x')
        ttk.Label(log_bar, text='查看日志').pack(side='left', padx=(0, 10))
        self.log_choice = tk.StringVar(value='启动进度')
        picker = ttk.Combobox(log_bar, textvariable=self.log_choice, values=['启动进度', *LOG_KEYS], state='readonly', width=20)
        picker.pack(side='left')
        picker.bind('<<ComboboxSelected>>', self.select_log)
        ttk.Label(log_bar, text='关闭窗口会停止全部项目；每行可单独启动、停止。', style='Muted.TLabel').pack(side='right')
        self.output = ScrolledText(self.window, state='disabled', wrap='word', font=('Consolas', 10), background='#ffffff', foreground='#273a32', relief='flat', borderwidth=1)
        self.output.pack(fill='both', expand=True, padx=22, pady=(0, 18))
        self.log('双击“启动本地项目.bat”会打开此窗口并启动全部项目。')
        self.log('已有项目正在运行时会直接使用，不会重复占用端口。')
        self.log('关闭窗口或“停止全部”会停止管理的服务及子进程；MySQL 继续运行。')
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.after(150, self.drain)
        threading.Thread(target=self.monitor, daemon=True).start()
        if '--start' in sys.argv:
            self.window.after(500, self.start)
        if '--admin-accounts' in sys.argv:
            self.window.after(600, self.open_accounts)

    def log(self, text):
        line = time.strftime('%H:%M:%S ') + describe(str(text))
        self.events.put(('log', line))
        try:
            core.RUN.mkdir(parents=True, exist_ok=True)
            with (core.RUN / 'launcher-gui.log').open('a', encoding='utf-8') as stream:
                stream.write(line.rstrip() + '\n')
        except OSError:
            pass

    def write_view(self, content, *, replace=False):
        self.output.configure(state='normal')
        if replace:
            self.output.delete('1.0', 'end')
        self.output.insert('end', content)
        if int(self.output.index('end-1c').split('.')[0]) > 1800:
            self.output.delete('1.0', '500.0')
        self.output.see('end')
        self.output.configure(state='disabled')

    def drain(self):
        try:
            for _ in range(150):
                kind, value = self.events.get_nowait()
                if kind == 'log':
                    self.progress_lines.append(value)
                    if self.log_choice.get() == '启动进度':
                        self.write_view(value + '\n')
                elif kind == 'status':
                    self.status.set(value)
                elif kind == 'active':
                    self.active_service = value
                elif kind == 'health':
                    self.ready = value
                    self.progress['value'] = sum(v == 'ready' for v in value.values())
                    for name, keys, _ in APPLICATIONS:
                        states = [value.get(key, 'stopped') for key in keys]
                        if all(state == 'ready' for state in states):
                            label, style = '已运行', 'Ready.TLabel'
                        elif self.busy and self.operation == 'stop' and any(key in self.stopping_keys for key in keys):
                            label, style = '正在停止', 'Muted.TLabel'
                        elif self.busy and any(key == self.active_service for key in keys):
                            label, style = '正在启动', 'Muted.TLabel'
                        elif 'conflict' in states:
                            label, style = '端口占用 / 未就绪', 'Error.TLabel'
                        elif 'missing' in states:
                            label, style = '缺少启动文件', 'Error.TLabel'
                        elif 'ready' in states:
                            if len(keys) == 2:
                                label = '网页未启动' if states[0] == 'ready' else '后台未启动'
                            else:
                                label = '部分已运行'
                            style = 'Error.TLabel'
                        else:
                            label, style = '未启动', 'Muted.TLabel'
                        self.app_labels[name].configure(text=label, style=style)
                    if not self.busy:
                        count = sum(v == 'ready' for v in value.values())
                        self.status.set(f'当前有 {count} / {len(SERVICES)} 个服务已就绪。')
                elif kind == 'done':
                    self.busy = False
                    self.started_at = None
                    self.active_service = ''
                    self.status.set(value['message'])
                    self.elapsed.set('')
                    if self.operation == 'stop':
                        self.pending_stop.difference_update(self.stopping_keys)
                        if self.close_requested:
                            self.shutdown_failures.update(value.get('failed', ()))
                    self.operation = ''
                    self.stopping_keys = ()
                    if self.pending_stop:
                        self.begin_stop()
                    elif self.close_requested:
                        if self.shutdown_failures:
                            self.close_requested = False
                            self.set_controls(False)
                            self.status.set('部分项目未能停止，已保留窗口。请查看日志后重试关闭。')
                        else:
                            self.log('全部管理的项目已停止，关闭启动器。')
                            self.closing.set()
                            self.window.destroy()
                            return
                    else:
                        self.set_controls(False)
                elif kind == 'open-page' and not self.close_requested and not self.cancel.is_set():
                    webbrowser.open(value)
        except queue.Empty:
            pass
        if self.busy and self.started_at:
            self.elapsed.set(f'已用时 {int(time.monotonic() - self.started_at)} 秒')
        self.refresh_selected_log()
        self.window.after(200, self.drain)

    def monitor(self):
        def inspect(service):
            if core.health_ok(service):
                return service.name, 'ready'
            if not service.executable.is_file():
                return service.name, 'missing'
            return service.name, 'conflict' if core.port_open(service.port) else 'stopped'
        with ThreadPoolExecutor(max_workers=4) as pool:
            while not self.closing.is_set():
                try:
                    self.events.put(('health', dict(pool.map(inspect, core.SERVICES))))
                except Exception as exc:
                    self.log('读取运行状态时遇到问题：' + str(exc))
                self.closing.wait(3)

    def set_controls(self, busy):
        state = 'disabled' if busy or self.close_requested else 'normal'
        self.start_button.configure(state=state)
        self.accounts_button.configure(state=state)
        for button in self.row_buttons:
            button.configure(state=state)
        self.stop_button.configure(state='disabled' if self.close_requested or self.operation == 'stop' else 'normal')

    def begin(self, status, operation):
        self.busy = True
        self.operation = operation
        self.started_at = time.monotonic()
        self.set_controls(True)
        self.status.set(status)

    def start(self, app_name=None):
        if self.busy or self.close_requested:
            return
        self.cancel.clear()
        keys = tuple(SERVICES)
        url = 'http://127.0.0.1:8030/'
        if app_name:
            _, keys, url = next(app for app in APPLICATIONS if app[0] == app_name)
            if app_name == 'RAG 知识库':
                keys = ('ollama', *keys)
        self.begin('正在启动' + (app_name or '全部项目') + '，请查看下方进度…', 'start')
        self.log_choice.set('启动进度')
        self.select_log()
        threading.Thread(target=self.start_worker, args=(keys, url), daemon=True).start()

    def start_worker(self, keys, url):
        outcome = '启动完成，可以点击对应项目的“打开网页”。'
        writer = LogWriter(self.log)
        try:
            self.log('准备启动：' + '、'.join(LABELS[key] for key in keys))
            with core.operation_lock(cancel_event=self.cancel):
                state = core.load_state()
                with redirect_stdout(writer), redirect_stderr(writer):
                    errors = []
                    for key in keys:
                        if self.cancel.is_set():
                            break
                        self.events.put(('active', key))
                        self.events.put(('status', '正在准备：' + LABELS[key]))
                        try:
                            core.start_service(SERVICES[key], state, cancel_event=self.cancel)
                        except Exception as exc:
                            if self.cancel.is_set():
                                break
                            errors.append(key)
                            self.log(LABELS[key] + ' 启动未完成：' + str(exc))
                    if errors:
                        outcome = '部分项目启动未完成；请在日志下拉框中选择对应项目查看原因。'
                    elif self.cancel.is_set():
                        outcome = '已取消启动，正在处理停止请求。'
                    elif url:
                        self.events.put(('open-page', url))
        except Exception as exc:
            self.log('启动提示：' + str(exc))
            outcome = '启动已取消。' if self.cancel.is_set() else '启动未完成，请查看日志。'
        finally:
            writer.flush()
            self.events.put(('done', {'message': outcome}))

    def request_stop(self, app_name=None):
        keys = tuple(SERVICES) if not app_name else next(app[1] for app in APPLICATIONS if app[0] == app_name)
        if app_name == '客服工单系统':
            keys = tuple(key for key in keys if key != 'ecom_backend')
        self.pending_stop.update(keys)
        if self.busy:
            self.cancel.set()
            self.status.set('正在结束当前操作，随后停止项目…')
            return
        self.begin_stop()

    def begin_stop(self):
        self.stopping_keys = tuple(key for key in STOP_ORDER if key in self.pending_stop)
        self.begin('正在停止全部项目并关闭窗口…' if self.close_requested else '正在停止所选项目…', 'stop')
        threading.Thread(target=self.stop_worker, args=(self.stopping_keys,), daemon=True).start()

    def stop_worker(self, keys):
        failed = []
        writer = LogWriter(self.log)
        try:
            with core.operation_lock():
                state = core.load_state()
                with redirect_stdout(writer), redirect_stderr(writer):
                    for name in keys:
                        try:
                            core.stop_service(SERVICES[name], state)
                        except Exception as exc:
                            failed.append(name)
                            self.log(LABELS[name] + ' 停止未完成：' + str(exc))
        except Exception as exc:
            failed = list(keys)
            self.log('停止未完成：' + str(exc))
        finally:
            writer.flush()
        result = '部分项目停止失败，请查看日志。' if failed else '所选项目已停止；可单独启动或点击“启动全部”。'
        self.events.put(('done', {'message': result, 'failed': failed}))

    def open_page(self, name, keys, url):
        if not all(self.ready.get(key) == 'ready' for key in keys):
            messagebox.showinfo(name, '项目还未就绪，请先启动并等待状态变成“已运行”。', parent=self.window)
            return
        webbrowser.open(url)

    def open_logs(self):
        core.RUN.mkdir(parents=True, exist_ok=True)
        os.startfile(core.RUN)

    def open_accounts(self):
        if self.busy or self.close_requested:
            return
        if self.accounts_dialog is not None:
            self.accounts_dialog.window.deiconify()
            self.accounts_dialog.window.lift()
            return
        self.accounts_dialog = AdminAccountsDialog(self, LogWriter)

    def select_log(self, _event=None):
        self.log_fingerprint = None
        if self.log_choice.get() == '启动进度':
            self.write_view('\n'.join(self.progress_lines) + '\n', replace=True)
        else:
            self.refresh_selected_log()

    def refresh_selected_log(self):
        key = LOG_KEYS.get(self.log_choice.get())
        if not key:
            return
        paths = [core.RUN / f'{key}.out.log', core.RUN / f'{key}.err.log']
        try:
            fingerprint = tuple((path.stat().st_size, path.stat().st_mtime_ns) if path.exists() else None for path in paths)
            if self.log_fingerprint == (key, fingerprint):
                return
            self.log_fingerprint = (key, fingerprint)
            parts = []
            for path in paths:
                if path.exists():
                    with path.open('rb') as stream:
                        stream.seek(max(0, path.stat().st_size - 24000))
                        parts.append(path.name + '\n' + stream.read().decode('utf-8', errors='replace'))
            self.write_view('\n\n'.join(parts) or '此项目尚未产生运行日志。\n', replace=True)
        except OSError:
            pass

    def close(self):
        if self.close_requested:
            return
        self.close_requested = True
        self.shutdown_failures.clear()
        self.cancel.set()
        self.pending_stop.update(SERVICES)
        self.set_controls(True)
        self.log_choice.set('启动进度')
        self.select_log()
        self.log('收到关闭请求，停止全部项目后退出。')
        self.status.set('正在停止全部项目，请稍候…')
        if not self.busy:
            self.begin_stop()

    def run(self):
        self.window.mainloop()


def acquire_window():
    """Keep one window per project directory; bring it forward on a second click."""
    kernel = core.KERNEL32
    kernel.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    name = 'Local\\ProjectLauncherWindow-' + hashlib.sha256(str(core.ROOT).lower().encode()).hexdigest()[:20]
    ctypes.set_last_error(0)
    handle = kernel.CreateMutexW(None, False, name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == 183:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        user32.FindWindowW.restype = wintypes.HWND
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        window = user32.FindWindowW(None, TITLE)
        if window:
            user32.ShowWindow(window, 9)
            user32.SetForegroundWindow(window)
        kernel.CloseHandle(handle)
        return None
    return handle


if __name__ == '__main__':
    instance = None
    try:
        instance = acquire_window()
        if instance:
            ProjectWindow().run()
    except Exception as exc:
        core.RUN.mkdir(parents=True, exist_ok=True)
        (core.RUN / 'launcher-gui-error.log').write_text(str(exc), encoding='utf-8')
        ctypes.windll.user32.MessageBoxW(None, '启动窗口未能打开：' + str(exc), TITLE, 0x10)
        raise SystemExit(1)
    finally:
        if instance:
            core.KERNEL32.CloseHandle(instance)
