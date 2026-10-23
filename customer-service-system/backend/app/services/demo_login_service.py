"""维护演示平台公开登录凭据，按现存账号顺序选取展示对象。"""

from sqlalchemy.orm import Session

from app.models.demo_login import DemoLoginCredential
from app.models.user import User
from app.utils.password import hash_password, verify_password


def remember_demo_password(db: Session, user: User, plain_password: str | None = None):
    """与账号写入使用同一事务；普通客户不保存展示密码。"""
    db.query(User.id).filter(User.id == user.id).with_for_update().first()
    credential = (
        db.query(DemoLoginCredential).filter_by(user_id=user.id)
        .with_for_update().first()
    )
    customer_demo = user.role == "customer" and credential is not None and credential.is_customer_demo
    if user.role not in {"admin", "user"} and not customer_demo:
        if credential is not None:
            db.delete(credential)
        return
    if credential is not None and user.role != "customer":
        credential.is_customer_demo = False
    if plain_password is not None:
        if credential is None:
            credential = DemoLoginCredential(user_id=user.id)
            db.add(credential)
        credential.display_password = plain_password
        credential.password_hash = user.password
        credential.is_customer_demo = user.role == "customer"
    elif credential is not None and credential.password_hash != user.password:
        db.delete(credential)


def initialize_demo_credentials(db: Session):
    """只兼容原有演示口令；不能还原未知密码，也不会重设账号密码。"""
    for username, plain_password in (("admin", "admin"), ("aaa", "123"), ("bbb", "123")):
        user = db.query(User).filter(User.username == username).first()
        if user is None or user.role not in {"admin", "user"}:
            continue
        credential = db.query(DemoLoginCredential).filter_by(user_id=user.id).first()
        if credential is not None and credential.password_hash == user.password:
            continue
        try:
            matches = verify_password(plain_password, user.password)
        except (ValueError, TypeError):
            matches = False
        if matches:
            remember_demo_password(db, user, plain_password)

    # 单独创建一个体验买家，不公开已有普通客户的密码。
    customer_demo = (
        db.query(DemoLoginCredential)
        .join(User, User.id == DemoLoginCredential.user_id)
        .filter(DemoLoginCredential.is_customer_demo.is_(True), User.role == "customer")
        .first()
    )
    if customer_demo is None:
        username = "demo_customer"
        suffix = 1
        while db.query(User.id).filter(User.username == username).first():
            suffix += 1
            username = f"demo_customer_{suffix}"
        plain_password = "demo123456"
        user = User(
            username=username, name="演示买家", role="customer", status=1,
            password=hash_password(plain_password),
        )
        db.add(user)
        db.flush()
        db.add(DemoLoginCredential(
            user_id=user.id, display_password=plain_password,
            password_hash=user.password, is_customer_demo=True,
        ))


def list_demo_accounts(db: Session, mode: str = "backend") -> list[dict]:
    if mode == "user":
        customer = (
            db.query(User).join(DemoLoginCredential, DemoLoginCredential.user_id == User.id)
            .filter(User.role == "customer", User.status == 1, DemoLoginCredential.is_customer_demo.is_(True))
            .order_by(User.id.asc()).first()
        )
        credential = db.query(DemoLoginCredential).filter_by(user_id=customer.id).first() if customer else None
        if customer is None:
            return []
        available = credential is not None and credential.password_hash == customer.password
        return [{
            "id": customer.id, "label": "演示用户", "username": customer.username,
            "password": credential.display_password if available else None, "role": "customer",
        }]
    # 排名每次从现存、启用的账号计算；删除、停用或改变角色后立即补位。
    administrator = (
        db.query(User).filter(User.role == "admin", User.status == 1)
        .order_by(User.id.asc()).first()
    )
    operators = (
        db.query(User).filter(User.role == "user", User.status == 1)
        .order_by(User.id.asc()).limit(2).all()
    )
    selected = ([administrator] if administrator else []) + operators
    if not selected:
        return []
    credentials = {
        row.user_id: row for row in db.query(DemoLoginCredential).filter(
            DemoLoginCredential.user_id.in_([user.id for user in selected])
        )
    }
    result = []
    for user in selected:
        credential = credentials.get(user.id)
        available = credential is not None and credential.password_hash == user.password
        operator_number = operators.index(user) + 1 if user.role == "user" else None
        result.append({
            "id": user.id,
            "label": f"运营账号 {operator_number}" if operator_number else "后台管理员",
            "username": user.username,
            "password": credential.display_password if available else None,
            "role": user.role,
        })
    return result
