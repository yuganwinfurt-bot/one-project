"""Prepare an existing customer page; account credentials are never read or changed."""
import re
from app.models.user import User
from app.models.demo_login import DemoLoginCredential
from app.common.exceptions import BusinessException


def prepare_customer_page(db, editor, question):
    if editor.role != 'admin':
        return {'action': 'login_page', 'label': '用户登录页面', 'message': '在新标签页打开用户登录入口。'}
    customers = db.query(User).filter_by(role='customer', status=1).order_by(User.id).all()
    if not customers:
        return {'action': 'login_page', 'label': '用户登录页面', 'message': '在新标签页打开用户登录入口。'}
    matches = [user for user in customers if re.search(r'(?<![A-Za-z0-9_])'+re.escape(user.username)+r'(?![A-Za-z0-9_])', question)
               or user.name and len(user.name) > 1 and user.name in question]
    if len(matches) > 1:
        raise BusinessException('匹配到多个用户，请指定一个用户名')
    explicit = re.search(r'(?:账号|账户|用户ID|用户编号|买家编号|用户|买家)\s*[#：:]?\s*([A-Za-z0-9_@.-]+)', question)
    if not matches and explicit:
        value = explicit.group(1).rstrip('.-')
        matches = [user for user in customers if user.username == value or str(user.id) == value]
        if not matches:
            raise BusinessException('没有找到这个启用的用户账号，请核对用户名或用户编号')
    if not matches:
        demo_ids = {row[0] for row in db.query(DemoLoginCredential.user_id).filter_by(is_customer_demo=True).all()}
        matches = [user for user in customers if user.id in demo_ids] or customers[:1]
    target = matches[0]
    return {'action': 'login_as', 'label': target.name or target.username,
            'user': {'id': target.id, 'username': target.username, 'name': target.name, 'role': 'customer'},
            'message': '使用管理员已有的用户登录入口，在独立标签页打开该用户页面。'}
