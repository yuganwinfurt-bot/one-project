"""商城运营扩展；独立新表，保留现有商品、用户与订单数据。"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MallContent(Base):
    __tablename__ = 'mall_contents'
    kind: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(120))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class MallSetting(Base):
    __tablename__ = 'mall_settings'
    key: Mapped[str] = mapped_column(String(40), unique=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class CustomerActivity(Base):
    __tablename__ = 'mall_customer_activities'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey('products.id'), nullable=True)
    keyword: Mapped[str | None] = mapped_column(String(100), nullable=True)


class MallFeedback(Base):
    __tablename__ = 'mall_feedback'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    contact: Mapped[str] = mapped_column(String(120), default='')
    reply: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(20), default='pending')


class ProductCatalog(Base):
    __tablename__ = 'mall_product_catalog'
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), unique=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey('mall_contents.id'), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey('mall_contents.id'), nullable=True)


class CouponClaim(Base):
    __tablename__ = 'mall_coupon_claims'
    __table_args__ = (UniqueConstraint('user_id', 'coupon_id', name='uq_mall_user_coupon'),)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey('mall_contents.id'), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    terms: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='领取时的优惠规则快照')
    reserved_checkout_id: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='待付款结算占用')


class CouponStock(Base):
    __tablename__ = 'mall_coupon_stock'
    coupon_id: Mapped[int] = mapped_column(ForeignKey('mall_contents.id'), unique=True)
    issued: Mapped[int] = mapped_column(default=0)


class OrderPromotion(Base):
    __tablename__ = 'mall_order_promotions'
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), unique=True)
    coupon_claim_id: Mapped[int | None] = mapped_column(ForeignKey('mall_coupon_claims.id'), nullable=True)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    shipping_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)


class GroupPurchase(Base):
    __tablename__ = 'mall_group_purchases'
    rule_id: Mapped[int] = mapped_column(ForeignKey('mall_contents.id'), index=True)
    leader_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(20), default='forming', index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    target_size: Mapped[int] = mapped_column()
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))


class GroupMember(Base):
    __tablename__ = 'mall_group_members'
    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='uq_mall_group_member'),)
    group_id: Mapped[int] = mapped_column(ForeignKey('mall_group_purchases.id'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), unique=True)


class StaffPermission(Base):
    __tablename__ = 'mall_staff_permissions'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('mall_contents.id'))
