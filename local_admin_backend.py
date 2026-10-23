"""Local stdin/stdout bridge. Invoked only by the desktop launcher, never over HTTP."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ECOM = ROOT / 'customer-service-system' / 'customer-service-system' / 'backend'
ENV_FILES = (ROOT / 'yugan-agent' / '.env', ROOT / 'rag-assistant' / 'backend' / '.env')
AUTH_KEYS = ('YUGAN_ADMIN_USERNAME', 'YUGAN_ADMIN_PASSWORD_HASH', 'YUGAN_AUTH_SIGNING_SECRET')


class AccountError(Exception):
    pass


def fingerprint(values):
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def shared_values():
    from dotenv import dotenv_values
    return [{key: str(value.get(key) or '') for key in AUTH_KEYS}
            for value in (dotenv_values(path, interpolate=False) for path in ENV_FILES)]


def shared_account():
    values = shared_values()
    common = values[0] == values[1]
    return {
        'id': 'shared', 'label': '项目主页 / Agent / RAG（共用）',
        'username': values[0][AUTH_KEYS[0]], 'fingerprint': fingerprint(values),
        'password': None,
        'note': ('旧密码仅保存了不可逆的摘要，无法还原；设置新密码后可在这里查看。' if common
                 else 'Agent 与 RAG 配置不一致；保存时会统一这三个项目的登录账号。'),
    }


def ecommerce_accounts():
    from app.database import SessionLocal
    from app.models import User, DemoLoginCredential
    from app.utils.password import verify_password
    with SessionLocal() as db:
        result = []
        for user in db.query(User).filter_by(role='admin').order_by(User.id):
            credential = db.query(DemoLoginCredential).filter_by(user_id=user.id).first()
            plain = None
            if credential and credential.password_hash == user.password:
                try:
                    if verify_password(credential.display_password, user.password):
                        plain = credential.display_password
                except (ValueError, TypeError):
                    pass
            result.append({
                'id': f'ecommerce:{user.id}', 'label': f'电商平台 · {user.username}',
                'username': user.username, 'password': plain,
                'fingerprint': fingerprint([user.id, user.username, user.password]),
                'note': '本机电商管理员账号。' if plain else '旧密码未保存明文，可设置新密码。',
            })
        return result


def validate(values):
    username = str(values.get('username') or '').strip()
    password = values.get('password') or ''
    if not re.fullmatch(r'[A-Za-z0-9_\u4e00-\u9fff.@-]{1,50}', username):
        raise AccountError('账号需为 1～50 位字母、数字、中文或 _ . @ -，不能包含空格。')
    if not isinstance(password, str) or (password and not 6 <= len(password) <= 64):
        raise AccountError('新密码长度须为 6～64 位；留空表示保留原密码。')
    if len(password.encode('utf-8')) > 72:
        raise AccountError('新密码的 UTF-8 长度不能超过 72 字节，请减少中文或表情。')
    return username, password


def atomic_write(path, content):
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def update_env(original, values):
    text = original.decode('utf-8-sig')
    newline = '\r\n' if '\r\n' in text else '\n'
    text = text.replace('\r\n', '\n')
    for key, value in values.items():
        line = key + '=' + json.dumps(value, ensure_ascii=False)
        pattern = rf'(?m)^\s*(?:export\s+)?{re.escape(key)}[^\S\n]*=[^\n]*$'
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _match: line, text)
        else:
            text = text.rstrip('\n') + '\n' + line + '\n'
    encoding = 'utf-8-sig' if original.startswith(b'\xef\xbb\xbf') else 'utf-8'
    return text.replace('\n', newline).encode(encoding)


def save_shared(request, username, password):
    values = shared_values()
    if request.get('fingerprint') != fingerprint(values):
        raise AccountError('账号配置已被其他操作修改，请刷新后再保存。')
    if not password and (not values[0][AUTH_KEYS[1]] or values[0][AUTH_KEYS[1]] != values[1][AUTH_KEYS[1]]):
        raise AccountError('尚未配置统一密码，请填写新密码。')
    changed = bool(password) or any(value[AUTH_KEYS[0]] != username for value in values)
    if not changed:
        return {'account': shared_account(), 'changed': False, 'restart': []}
    encoded = values[0][AUTH_KEYS[1]]
    if password:
        salt = base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('=')
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 310000)
        encoded = f'pbkdf2_sha256$310000${salt}$' + base64.urlsafe_b64encode(digest).decode().rstrip('=')
    updated = dict(zip(AUTH_KEYS, (username, encoded, secrets.token_urlsafe(48))))
    originals = [path.read_bytes() for path in ENV_FILES]
    from io import StringIO
    from dotenv import dotenv_values
    original_values = [{key: str(value.get(key) or '') for key in AUTH_KEYS}
                       for value in (dotenv_values(stream=StringIO(raw.decode('utf-8-sig')), interpolate=False)
                                     for raw in originals)]
    if fingerprint(original_values) != request.get('fingerprint'):
        raise AccountError('账号配置已被其他操作修改，请刷新后再保存。')
    prepared = [update_env(original, updated) for original in originals]
    written = []
    try:
        for index, path in enumerate(ENV_FILES):
            if path.read_bytes() != originals[index]:
                raise AccountError('配置文件发生变化，请刷新后重试。')
            atomic_write(path, prepared[index])
            written.append(index)
    except Exception:
        for index in reversed(written):
            if ENV_FILES[index].read_bytes() == prepared[index]:
                atomic_write(ENV_FILES[index], originals[index])
        raise
    return {'account': shared_account(), 'changed': True, 'restart': ['agent', 'rag']}


def save_ecommerce(request, username, password):
    from sqlalchemy.exc import IntegrityError
    from app.database import SessionLocal
    from app.models import User, DemoLoginCredential
    from app.services.platform_log_service import record_changes
    from app.utils.password import hash_password
    user_id = int(request['id'].split(':', 1)[1])
    with SessionLocal() as db:
        user = db.query(User).filter_by(id=user_id, role='admin').with_for_update().first()
        if not user:
            raise AccountError('该管理员账号已不存在，请刷新。')
        if request.get('fingerprint') != fingerprint([user.id, user.username, user.password]):
            raise AccountError('账号已被其他操作修改，请刷新后再保存。')
        if db.query(User).filter(User.username == username, User.id != user_id).first():
            raise AccountError('该账号名称已被使用，请更换。')
        changed = bool(password) or user.username != username
        if changed:
            old_username = user.username
            user.username = username
            changes = [('账号', old_username, username)]
            if password:
                user.password = hash_password(password)
                # 新管理员密码只在启动器的 Windows 加密存储中记住，不能放入公开体验凭据表。
                credential = db.query(DemoLoginCredential).filter_by(user_id=user.id).with_for_update().first()
                if credential:
                    db.delete(credential)
                changes.append(('登录密码', '内容不记录', '已更新（内容不记录）'))
            record_changes(db, user, '账号', old_username, changes, verb='通过本机启动器修改了')
            try:
                db.commit()
            except IntegrityError:
                raise AccountError('账号名称发生冲突，请刷新后重试。') from None
    account = next(row for row in ecommerce_accounts() if row['id'] == request['id'])
    return {'account': account, 'changed': changed, 'restart': []}


def main():
    sys.path.insert(0, str(ECOM))
    os.chdir(ECOM)
    request = json.load(sys.stdin)
    action = request.get('action')
    if action == 'verify':
        password = request.get('password')
        if not isinstance(password, str) or not password or len(password) > 4096:
            raise AccountError('请输入当前的网页登录密码。')
        if request.get('id') == 'shared':
            values = shared_values()
            if request.get('fingerprint') != fingerprint(values):
                raise AccountError('账号配置已发生变化，请先刷新账号。')
            if values[0] != values[1]:
                raise AccountError('Agent 与 RAG 的账号配置不一致，请先统一账号。')
            try:
                algorithm, rounds, salt, expected = values[0][AUTH_KEYS[1]].split('$', 3)
                iterations = int(rounds)
                if algorithm != 'pbkdf2_sha256' or not 1 <= iterations <= 5000000:
                    raise ValueError()
                digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
                actual = base64.urlsafe_b64encode(digest).decode().rstrip('=')
                valid = hmac.compare_digest(actual, expected)
            except (ValueError, TypeError):
                raise AccountError('当前密码摘要无法验证，请检查账号配置。') from None
            if not valid:
                raise AccountError('当前密码不正确，未保存，也未修改账号密码。')
            return {'account': shared_account()}
        if re.fullmatch(r'ecommerce:[1-9][0-9]*', str(request.get('id') or '')):
            from app.database import SessionLocal
            from app.models import User
            from app.utils.password import verify_password
            user_id = int(request['id'].split(':', 1)[1])
            with SessionLocal() as db:
                user = db.query(User).filter_by(id=user_id, role='admin').first()
                if not user or request.get('fingerprint') != fingerprint([user.id, user.username, user.password]):
                    raise AccountError('账号已发生变化，请先刷新账号。')
                try:
                    valid = verify_password(password, user.password)
                except (ValueError, TypeError):
                    valid = False
                if not valid:
                    raise AccountError('当前密码不正确，未保存，也未修改账号密码。')
            return {'account': next(row for row in ecommerce_accounts() if row['id'] == request['id'])}
        raise AccountError('不支持的管理员账号。')
    if action == 'list':
        accounts, warnings = [shared_account()], []
        try:
            accounts.extend(ecommerce_accounts())
        except Exception:
            warnings.append('电商账号暂时无法读取，请确认本机 MySQL 已启动。')
        return {'accounts': accounts, 'warnings': warnings}
    if action == 'save':
        username, password = validate(request)
        if request.get('id') == 'shared':
            return save_shared(request, username, password)
        if re.fullmatch(r'ecommerce:[1-9][0-9]*', str(request.get('id') or '')):
            return save_ecommerce(request, username, password)
    raise AccountError('不支持的管理员操作。')


if __name__ == '__main__':
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        response = {'ok': True, 'data': main()}
    except AccountError as exc:
        response = {'ok': False, 'error': str(exc)}
    except Exception:
        # 数据库异常可能含有参数，不能将原始错误或 traceback 写入启动器日志。
        response = {'ok': False, 'error': '读取或保存失败，请检查本机数据库及项目配置文件权限。'}
    print(json.dumps(response, ensure_ascii=False))
