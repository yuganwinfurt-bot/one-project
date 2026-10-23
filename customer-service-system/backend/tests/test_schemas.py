"""出参模型公共基类 RowItem 的单元测试。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Order, Product
from app.schemas.ecommerce import OrderItem


@pytest.fixture()
def order():
    """内存库里造一行订单，用于验证「ORM 行 → 出参」的转换。"""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=[Product.__table__, Order.__table__])
    try:
        with Session(engine) as db:
            product = Product(name="商品", category="类目", description="d", price=10, stock=1)
            db.add(product)
            db.flush()
            row = Order(
                order_no="EO1", product_id=product.id, buyer_name="买家", quantity=1, amount=10
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            yield row
    finally:
        engine.dispose()


def test_from_row_fills_join_columns(order):
    item = OrderItem.from_row(order, product_name="轻云运动跑鞋")
    assert item.order_no == "EO1"
    assert item.product_name == "轻云运动跑鞋"


def test_from_row_without_extra_columns_keeps_default(order):
    """没有 JOIN 额外列时，字段保持声明时的默认值。"""
    assert OrderItem.from_row(order).product_name is None


def test_from_row_rejects_unknown_column(order):
    """额外列名写错要立刻报错：model_copy 本身不校验，静默塞进对象更难查。"""
    with pytest.raises(ValueError, match="没有这些字段"):
        OrderItem.from_row(order, product_nmae="拼错的字段名")
