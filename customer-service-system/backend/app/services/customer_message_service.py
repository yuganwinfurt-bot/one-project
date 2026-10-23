"""创建普通用户可见的收藏商品降价提醒。"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.shopping import CustomerMessage, FavoriteProduct


def notify_favorited_customers_of_price_drop(
    db: Session, product: Product, previous_price: Decimal | None
) -> None:
    """商品售价确实降低时，为当前收藏该商品的用户各建一条消息。"""
    if previous_price is None:
        return

    old_price = Decimal(str(previous_price))
    new_price = Decimal(str(product.price))
    if new_price >= old_price:
        return

    user_ids = (
        db.query(FavoriteProduct.user_id)
        .filter(FavoriteProduct.product_id == product.id)
        .all()
    )
    db.add_all(
        CustomerMessage(
            user_id=user_id,
            product_id=product.id,
            product_name=product.name,
            previous_price=old_price,
            current_price=new_price,
        )
        for (user_id,) in user_ids
    )
