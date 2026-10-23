"""Desktop account management; passwords travel over pipes and are stored with user DPAPI."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import time

import start_local_projects as core


class AccountError(Exception):
    pass


class DataBlob(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]


def crypt(value, *, decrypt=False):
    if os.name != 'nt':
        raise AccountError('密码加密存储目前只支持 Windows。')
    crypt32 = ctypes.WinDLL('crypt32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL
    buffer = ctypes.create_string_buffer(value)
    entropy_buffer = ctypes.create_string_buffer(hashlib.sha256(str(core.ROOT).lower().encode()).digest())
    source = DataBlob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    entropy = DataBlob(32, ctypes.cast(entropy_buffer, ctypes.POINTER(ctypes.c_ubyte)))
    output = DataBlob()
    function = crypt32.CryptUnprotectData if decrypt else crypt32.CryptProtectData
    function.argtypes = [ctypes.POINTER(DataBlob), ctypes.c_void_p, ctypes.POINTER(DataBlob),
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DataBlob)]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, ctypes.byref(entropy), None, None, 1, ctypes.byref(output)):
        raise AccountError('Windows 无法读取或保存加密密码，请使用原 Windows 用户重试。')
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        kernel32.LocalFree(ctypes.cast(output.data, wintypes.HLOCAL))


def vault_path():
    identifier = hashlib.sha256(str(core.ROOT).lower().encode()).hexdigest()[:16]
    return Path(os.environ['LOCALAPPDATA']) / 'OneProjectLauncher' / identifier / 'admin-credentials.sqlite3'


def read_vault():
    path = vault_path()
    if not path.exists():
        legacy = path.with_name('admin-credentials.bin')
        encrypted = legacy.read_bytes() if legacy.exists() else None
    else:
        with sqlite3.connect(path, timeout=10) as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='credential_vault'").fetchone():
                return {}
            row = db.execute('SELECT encrypted FROM credential_vault WHERE id=1').fetchone()
            encrypted = bytes(row[0]) if row else None
    if encrypted is None:
        return {}
    value = json.loads(crypt(encrypted, decrypt=True).decode('utf-8'))
    if not isinstance(value, dict):
        raise AccountError('本机密码记录损坏，可重新设置密码后保存。')
    return value


def write_vault(value):
    encrypted = crypt(json.dumps(value, ensure_ascii=False).encode())
    path = vault_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # SQLite commits protect the previous encrypted record without renaming files.
    # os.replace on this machine returns ERROR_NOT_SAME_DEVICE even for this folder.
    with sqlite3.connect(path, timeout=10) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE IF NOT EXISTS credential_vault (id INTEGER PRIMARY KEY CHECK(id=1), encrypted BLOB NOT NULL)')
        db.execute('INSERT INTO credential_vault (id, encrypted) VALUES (1, ?) '
                   'ON CONFLICT(id) DO UPDATE SET encrypted=excluded.encrypted', (encrypted,))


def storage_error(exc):
    code = getattr(exc, 'winerror', None) or getattr(exc, 'sqlite_errorcode', None) or getattr(exc, 'errno', None)
    return f'错误代码 {code}' if code is not None else type(exc).__name__


def remember_verified(current, password):
    remembered = read_vault()
    remembered[current['id']] = {'username': current['username'], 'password': password,
                                'fingerprint': current['fingerprint']}
    write_vault(remembered)
    current['password'] = password
    current['note'] = '密码已自动加密保存，重新打开窗口会自动读取。'


def remember_account(account, password):
    with core.operation_lock():
        result = bridge({'action': 'verify', 'id': account['id'], 'fingerprint': account['fingerprint'],
                         'password': password})
        current = result['account']
        try:
            remember_verified(current, password)
        except Exception as exc:
            raise AccountError(f'密码验证成功，但本机保存失败（{storage_error(exc)}）。账号密码未修改。') from None
    return {'account': current, 'warnings': [], 'changed': False,
            'message': '已验证并加密记住当前密码；账号密码未修改。'}


def bridge(request):
    environment = os.environ.copy()
    environment['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        [str(core.ECOM_PYTHON), str(core.ROOT / 'local_admin_backend.py')],
        input=json.dumps(request, ensure_ascii=False), capture_output=True,
        encoding='utf-8', cwd=core.ECOM_BACKEND, env=environment,
        creationflags=subprocess.CREATE_NO_WINDOW, timeout=45,
    )
    try:
        response = json.loads(result.stdout)
    except (TypeError, ValueError):
        raise AccountError('管理员组件未能返回结果，请检查电商 Python 环境。') from None
    if not response.get('ok'):
        raise AccountError(response.get('error') or '管理员操作未完成。')
    return response['data']


def load_accounts():
    with core.operation_lock():
        return _load_accounts_locked()


def _load_accounts_locked():
    result = bridge({'action': 'list'})
    vault_available = True
    try:
        remembered = read_vault()
    except Exception:
        remembered = {}
        vault_available = False
        result['warnings'].append('本机加密密码暂时无法读取；账号仍可修改。')
    pending = False
    for row in result['accounts']:
        saved = remembered.get(row['id'], {})
        if saved.get('fingerprint') == row['fingerprint'] and saved.get('username') == row['username']:
            row['password'] = saved.get('password')
            row['note'] = '密码已自动加密保存，重新打开窗口会自动读取。'
        elif row.get('password') and vault_available:
            # 已由后台核验过的现有密码也自动记住，无需额外操作。
            remembered[row['id']] = {'username': row['username'], 'password': row['password'],
                                     'fingerprint': row['fingerprint']}
            pending = True
    if pending:
        try:
            write_vault(remembered)
            for row in result['accounts']:
                if row.get('password'):
                    row['note'] = '密码已自动加密保存，重新打开窗口会自动读取。'
        except Exception as exc:
            result['warnings'].append(f'当前密码可查看，但自动保存未完成（{storage_error(exc)}）。')
    return result


def save_account(account, username, password):
    warnings = []
    password_remembered = False
    with core.operation_lock():
        result = bridge({'action': 'save', 'id': account['id'], 'fingerprint': account['fingerprint'],
                         'username': username, 'password': password})
        current = result['account']
        known_password = password or account.get('password')
        if known_password:
            current['password'] = known_password
            current['note'] = '当前窗口可查看密码，尚未确认保存到本机。'
            try:
                remember_verified(current, known_password)
                password_remembered = True
            except Exception as exc:
                warnings.append(f'账号已保存，但密码自动保存未完成（{storage_error(exc)}）。当前窗口仍可查看密码。')
        try:
            state = core.load_state()
        except Exception:
            warnings.append('账号已保存，但无法读取启动器进程记录；请重新启动相关项目以应用配置。')
            return {'account': current, 'warnings': warnings, 'changed': result['changed']}
        for service in core.SERVICES:
            if service.name not in result['restart']:
                continue
            record = state.get(service.name)
            if not record:
                if core.port_open(service.port):
                    warnings.append(core_label(service.name) + '由其他程序启动，请手动重启以应用新账号。')
                continue
            try:
                if core.process_creation_ticks(record['pid']) != record['created']:
                    warnings.append(core_label(service.name) + '原服务已退出；下次启动时应用新账号。')
                    continue
                core.stop_owned(service.name, record)
                del state[service.name]
                core.save_state(state)
                for _ in range(50):
                    if not core.port_open(service.port):
                        break
                    time.sleep(0.1)
                core.start_service(service, state)
            except Exception:
                warnings.append(core_label(service.name) + '重新加载未完成；账号已保存，可在启动器重新启动该项目。')
    if password_remembered:
        message = '已保存并自动加密记住密码，下次打开会自动读取。'
        if result['changed']:
            message += ' 请使用更新后的账号密码重新登录网页。'
    else:
        message = '账号已保存；设置新密码后会自动加密记住。'
    return {'account': current, 'warnings': warnings, 'changed': result['changed'], 'message': message}


def core_label(name):
    return {'rag': 'RAG ', 'agent': 'Agent '}.get(name, name)
