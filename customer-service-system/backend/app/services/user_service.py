from operator import or_
from datetime import datetime
from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.user import User
from app.models.community import DirectConversation, ReviewComment, ReviewReplyNotification
from app.models.inventory import CustomerRestockMessage
from app.services.platform_log_service import build_rollback_data, record_changes
from app.services.demo_login_service import remember_demo_password
from app.schemas.user import (
    PasswordUpdateRequest,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from sqlalchemy.orm import Session

from app.utils import password
from app.utils.password import hash_password, verify_password


def get_user_info(user: User) -> UserResponse:
    return UserResponse.from_user(user)


def update_user_info(db: Session, user: User, data: UserUpdateRequest):
    if user.role == "admin":
        raise BusinessException(message="管理员个人资料修改功能已下架", code=403)
    user_dict = data.model_dump(
        exclude_none=True, exclude={"role", "status", "password", "username"}
    )  # pydatic对象转换成字典
    labels = {"name": "名称", "email": "邮箱", "phone": "手机号", "avatar": "头像"}
    before = {field: getattr(user, field) for field in user_dict}
    for field, value in user_dict.items():
        setattr(user, field, value)
    record_changes(
        db,
        user,
        "账号",
        user.username,
        [(labels[field], before[field], getattr(user, field)) for field in user_dict],
        rollback_data=build_rollback_data(
            "user",
            user.id,
            {field: (before[field], getattr(user, field)) for field in user_dict},
        ),
    )
    db.commit()
    db.refresh(user)
    return UserResponse.from_user(user)


def heartbeat(db: Session, user: User):
    """记录已认证用户的在线心跳。"""
    user.last_seen_at = datetime.now()
    db.commit()


def logout(db: Session, user: User):
    """退出账号时立即清除在线心跳。"""
    user.last_seen_at = None
    db.commit()


def update_password(db: Session, user: User, data: PasswordUpdateRequest):
    """修改密码"""
    if user.role == "admin":
        raise BusinessException(message="管理员密码修改功能已下架", code=403)
    if not verify_password(data.old_password, user.password):
        raise BusinessException(message="原密码错误")
    if data.old_password == data.new_password:
        raise BusinessException(message="新密码不能跟原密码相同")
    user.password = hash_password(data.new_password)
    remember_demo_password(db, user, data.new_password)
    record_changes(
        db,
        user,
        "账号",
        user.username,
        [("登录密码", "未记录（敏感信息）", "已更新（内容不记录）")],
    )
    db.commit()


def get_user_page_list(
    db: Session, page: int, page_size: int, keywords: str | None = None
):
    """分页模糊查询用户列表"""
    # select * from user where username like '%张%' or name like '%张%';
    # 同时列出后台账号与注册用户，便于管理员查看和维护全部账号。
    query = db.query(User)
    if keywords:
        query = query.filter(
            or_(User.username.ilike(f"%{keywords}%"), User.name.ilike(f"%{keywords}%"))
        )
    total = query.count()
    items = (
        query.order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse(
        list=[UserResponse.from_user(item) for item in items], total=total
    )


def create_user(db: Session, data: UserCreateRequest, actor: User | None = None):
    """新增用户"""
    exist = db.query(User).filter(User.username == data.username).first()
    if exist:
        raise BusinessException(message="账号已存在")

    user = User(
        username=data.username,
        password=hash_password(data.password),
        # name 是数据库非空列：未填时与注册接口保持一致，用账号兜底
        name=data.name or data.username,
        email=data.email,
        phone=data.phone,
        avatar=data.avatar,
        status=data.status,
        role="user",
    )
    db.add(user)
    db.flush()
    remember_demo_password(db, user, data.password)
    record_changes(
        db,
        actor,
        "账号",
        user.username,
        [
            ("账号", None, user.username),
            ("名称", None, user.name),
            ("邮箱", None, user.email),
            ("手机号", None, user.phone),
            ("角色", None, user.role),
            ("状态", None, user.status),
        ],
        verb="新建了",
        rollback_data=build_rollback_data(
            "user",
            user.id,
            {
                "username": (None, user.username),
                "name": (None, user.name),
                "email": (None, user.email),
                "phone": (None, user.phone),
                "role": (None, user.role),
                "status": (None, user.status),
            },
            created=True,
        ),
    )
    db.commit()
    db.refresh(user)
    return UserResponse.from_user(user)


def get_user_for_update(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在")
    return user


def update_user(
    db: Session,
    user: User,
    data: UserUpdateRequest,
    *,
    actor: User | None = None,
):
    """更新用户"""
    if user.role == "admin":
        raise BusinessException(message="管理员账号资料与密码修改功能已下架", code=403)
    if data.role is not None:
        raise BusinessException(message="账号角色修改功能已下架", code=403)
    if data.username is not None:
        normalized_username = data.username.strip()
        if not normalized_username:
            raise BusinessException(message="账号不能为空")
        exists = db.query(User).filter(
            User.username == normalized_username, User.id != user.id
        ).first()
        if exists:
            raise BusinessException(message="账号已存在")
    else:
        normalized_username = None
    payload = data.model_dump(exclude_none=True, exclude={"password"})
    labels = {
        "username": "账号", "name": "名称", "email": "邮箱", "phone": "手机号",
        "avatar": "头像", "role": "角色", "status": "状态",
    }
    before = {field: getattr(user, field) for field in payload}
    if normalized_username is not None:
        payload["username"] = normalized_username
    for filed, value in payload.items():
        setattr(user, filed, value)
    if data.password:
        user.password = hash_password(data.password)
    remember_demo_password(db, user, data.password)
    changes = [
        (labels[field], before[field], getattr(user, field))
        for field in payload
    ]
    if data.password:
        changes.append(("登录密码", "未记录（敏感信息）", "已更新（内容不记录）"))
    record_changes(
        db,
        actor,
        "账号",
        str(before.get("username") or user.username),
        changes,
        rollback_data=(
            build_rollback_data(
                "user",
                user.id,
                {field: (before[field], getattr(user, field)) for field in payload},
            )
            if not data.password and set(payload).issubset(
                {"username", "name", "email", "phone", "avatar", "status"}
            )
            else None
        ),
    )
    db.commit()
    db.refresh(user)
    return UserResponse.from_user(user)


def delete_user(db: Session, user_id: int, currut_user: User):
    """删除用户"""
    if user_id == currut_user.id:
        raise BusinessException(message="不能删除当前登录的账号")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在")
    if user.role not in {"user", "customer"}:
        raise BusinessException(message="管理员账号受保护，不能在用户管理中删除", code=403)
    has_community_history = (
        db.query(DirectConversation.id).filter(or_(DirectConversation.staff_id == user.id, DirectConversation.customer_id == user.id)).first()
        or db.query(ReviewComment.id).filter(or_(ReviewComment.user_id == user.id, ReviewComment.reply_to_user_id == user.id)).first()
        or db.query(ReviewReplyNotification.id).filter_by(user_id=user.id).first()
        or db.query(CustomerRestockMessage.id).filter_by(user_id=user.id).first()
    )
    if has_community_history:
        raise BusinessException(message="该账号有关联私聊或评论记录，请停用账号以保留历史记录", code=400)
    record_changes(
        db,
        currut_user,
        "账号",
        f"{user.username}（{user.name}）",
        [("账号", user.username, "已删除")],
        verb="删除了",
    )
    db.delete(user)
    db.commit()


