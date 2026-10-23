"""Administrator account dialog for the local project launcher."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import queue
import threading
import tkinter as tk
from tkinter import ttk

import local_admin_accounts as accounts


class AdminAccountsDialog:
    def __init__(self, owner, writer_type):
        self.owner = owner
        self.writer_type = writer_type
        self.window = tk.Toplevel(owner.window)
        self.window.title('网页登录管理员账号')
        self.window.geometry('720x570')
        self.window.minsize(660, 530)
        self.window.configure(background='#f4f7f5')
        self.window.transient(owner.window)
        self.events = queue.Queue()
        self.rows = []
        self.loading = False
        self.saving = False
        self.selected = tk.StringVar()
        self.username = tk.StringVar()
        self.current_password = tk.StringVar()
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()
        self.show_password = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='正在读取管理员账号…')
        self.note = tk.StringVar()
        outer = ttk.Frame(self.window, padding=22)
        outer.pack(fill='both', expand=True)
        outer.columnconfigure(1, weight=1)
        ttk.Label(outer, text='网页登录管理员账号', font=('Microsoft YaHei UI', 17, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(outer, text='管理本机项目的登录账号；项目主页、Agent 和 RAG 共用一套。', style='Muted.TLabel', wraplength=630).grid(row=1, column=0, columnspan=2, sticky='w', pady=(8, 20))
        ttk.Label(outer, text='项目 / 管理员').grid(row=2, column=0, sticky='w', padx=(0, 16))
        self.picker = ttk.Combobox(outer, textvariable=self.selected, state='disabled')
        self.picker.grid(row=2, column=1, sticky='ew', pady=6)
        self.picker.bind('<<ComboboxSelected>>', self.select)
        ttk.Label(outer, text='登录账号').grid(row=3, column=0, sticky='w')
        self.username_entry = ttk.Entry(outer, textvariable=self.username)
        self.username_entry.grid(row=3, column=1, sticky='ew', pady=6)
        ttk.Label(outer, text='当前密码').grid(row=4, column=0, sticky='w')
        self.current_entry = ttk.Entry(outer, textvariable=self.current_password, show='●', state='readonly')
        self.current_entry.grid(row=4, column=1, sticky='ew', pady=6)
        ttk.Label(outer, textvariable=self.note, style='Muted.TLabel', wraplength=500).grid(row=5, column=1, sticky='w', pady=(0, 10))
        ttk.Label(outer, text='新密码').grid(row=6, column=0, sticky='w')
        self.new_entry = ttk.Entry(outer, textvariable=self.new_password, show='●')
        self.new_entry.grid(row=6, column=1, sticky='ew', pady=6)
        ttk.Label(outer, text='再次输入新密码').grid(row=7, column=0, sticky='w')
        self.confirm_entry = ttk.Entry(outer, textvariable=self.confirm_password, show='●')
        self.confirm_entry.grid(row=7, column=1, sticky='ew', pady=6)
        password_controls = ttk.Frame(outer)
        password_controls.grid(row=8, column=1, sticky='ew', pady=(4, 8))
        ttk.Checkbutton(password_controls, text='显示密码', variable=self.show_password, command=self.toggle_password).pack(side='left')
        ttk.Label(outer, text='新密码 6～64 位；两项留空只修改账号。保存时自动加密记住密码，下次打开自动读取。\n修改共用账号后会重新加载正在运行的 Agent、RAG，网页需重新登录。', style='Muted.TLabel', wraplength=630).grid(row=9, column=0, columnspan=2, sticky='w', pady=(6, 12))
        ttk.Label(outer, textvariable=self.status, wraplength=630).grid(row=10, column=0, columnspan=2, sticky='w', pady=8)
        controls = ttk.Frame(outer)
        controls.grid(row=11, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        self.refresh_button = ttk.Button(controls, text='刷新账号', command=self.refresh)
        self.refresh_button.pack(side='left')
        self.save_button = ttk.Button(controls, text='保存并应用', style='Primary.TButton', command=self.save, state='disabled')
        self.save_button.pack(side='right', padx=(8, 0))
        ttk.Button(controls, text='关闭', command=self.close).pack(side='right')
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.after(100, self.drain)
        self.refresh()

    def refresh(self):
        if self.saving or self.loading:
            return
        self.loading = True
        self.status.set('正在读取管理员账号…')
        self.save_button.configure(state='disabled')
        self.refresh_button.configure(state='disabled')
        self.picker.configure(state='disabled')
        self.current_password.set('')
        self.show_password.set(False)
        self.toggle_password()

        def worker():
            try:
                self.events.put(('loaded', accounts.load_accounts()))
            except Exception:
                self.events.put(('error', '账号读取失败，请确认项目目录和电商 Python 环境可用。'))
        threading.Thread(target=worker, daemon=True).start()

    def select(self, _event=None):
        row = self.current_account()
        if not row:
            return
        self.username.set(row['username'])
        self.current_password.set(row.get('password') or '')
        self.new_password.set('')
        self.confirm_password.set('')
        self.show_password.set(False)
        self.toggle_password()
        self.note.set(row.get('note') or '')

    def current_account(self):
        return next((row for row in self.rows if row['label'] == self.selected.get()), None)

    def toggle_password(self):
        mask = '' if self.show_password.get() else '●'
        for entry in (self.current_entry, self.new_entry, self.confirm_entry):
            entry.configure(show=mask)

    def save(self):
        row = self.current_account()
        if not row or self.saving:
            return
        if self.owner.busy or self.owner.close_requested:
            self.status.set('启动器正在处理项目，请稍后再保存。')
            return
        username, password = self.username.get().strip(), self.new_password.get()
        if password != self.confirm_password.get():
            self.status.set('两次输入的新密码不一致。')
            return
        if not username:
            self.status.set('登录账号不能为空。')
            return
        if password and (not 6 <= len(password) <= 64 or len(password.encode('utf-8')) > 72):
            self.status.set('新密码须为 6～64 位，UTF-8 长度不超过 72 字节。')
            return
        self.run_request(lambda: accounts.save_account(row, username, password), '正在保存并应用管理员账号…')

    def run_request(self, callback, status):
        self.saving = True
        for entry in (self.username_entry, self.new_entry, self.confirm_entry):
            entry.configure(state='disabled')
        self.picker.configure(state='disabled')
        self.save_button.configure(state='disabled')
        self.refresh_button.configure(state='disabled')
        self.status.set(status)
        self.owner.begin(status, 'accounts')

        def worker():
            try:
                # 服务重载日志中不包含账号表单、密码或原始异常。
                writer = self.writer_type(self.owner.log)
                with redirect_stdout(writer), redirect_stderr(writer):
                    result = callback()
                writer.flush()
                self.events.put(('saved', result))
                message = result.get('message') or ('管理员账号已保存。' if result['changed'] else '账号未变化。')
            except accounts.AccountError as exc:
                self.events.put(('error', str(exc)))
                message = '管理员账号保存未完成，请查看账号窗口提示。'
            except Exception:
                self.events.put(('error', '保存未完成，请刷新账号核对当前状态后重试。'))
                message = '管理员账号操作未完成，请查看账号窗口提示。'
            self.owner.events.put(('done', {'message': message}))
        threading.Thread(target=worker, daemon=True).start()

    def drain(self):
        if not self.window.winfo_exists():
            return
        try:
            for _ in range(20):
                kind, data = self.events.get_nowait()
                self.loading = False
                self.saving = False
                self.refresh_button.configure(state='normal')
                for entry in (self.username_entry, self.new_entry, self.confirm_entry):
                    entry.configure(state='normal')
                if kind == 'loaded':
                    previous_id = (self.current_account() or {}).get('id')
                    self.rows = data['accounts']
                    self.picker.configure(values=[row['label'] for row in self.rows])
                    if self.rows:
                        selected = next((row for row in self.rows if row['id'] == previous_id), self.rows[0])
                        self.selected.set(selected['label'])
                        self.select()
                    self.status.set('\n'.join(data['warnings']) or '已自动读取已保存的账号密码；修改后点击“保存并应用”会自动记住。')
                elif kind == 'saved':
                    current = data['account']
                    self.rows = [current if row['id'] == current['id'] else row for row in self.rows]
                    self.picker.configure(values=[row['label'] for row in self.rows])
                    self.selected.set(current['label'])
                    self.select()
                    self.status.set('\n'.join(data['warnings']) or data.get('message') or '已保存。请使用新账号密码重新登录网页。')
                elif kind == 'error':
                    self.status.set(data)
                self.picker.configure(state='readonly' if self.rows else 'disabled')
                self.save_button.configure(state='normal' if self.rows else 'disabled')
        except queue.Empty:
            pass
        self.window.after(150, self.drain)

    def close(self):
        if self.saving:
            self.status.set('正在保存配置，请等待完成后关闭。')
            return
        self.current_password.set('')
        self.new_password.set('')
        self.confirm_password.set('')
        for row in self.rows:
            row.pop('password', None)
        self.rows.clear()
        self.window.destroy()
        self.owner.accounts_dialog = None
