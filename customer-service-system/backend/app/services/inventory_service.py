"""库存变化在业务事务内触发缺货预警和收藏到货提醒。"""
from app.models import Product, ProductInventoryState, CustomerRestockMessage, FavoriteProduct, AlertNotification, StaffInboxEvent, User


def sync_product_inventory(db, product_id, actor_id=None):
    product = db.query(Product).filter_by(id=product_id).with_for_update().first()
    if not product:
        return
    db.flush()
    state = db.query(ProductInventoryState).filter_by(product_id=product_id).with_for_update().first()
    available = product.stock > 0 and product.shelf_status == "on_sale" and product.review_status == "normal"
    if product.stock <= 0:
        if state is None or state.stock > 0:
            content = f"商品【{product.name}】库存已为0，请及时补货；缺货不影响已发货订单申请退款或退货退款。"
            alert = AlertNotification(title="商品缺货预警", content=content, level="warning", product_id=product.id, created_by=actor_id)
            db.add(alert)
            db.flush()
            db.add(StaffInboxEvent(event_type="alert", target_id=alert.id, title=alert.title, content=content))
        db.query(FavoriteProduct).filter_by(product_id=product.id).update(
            {FavoriteProduct.restock_waiting: True}, synchronize_session="fetch"
        )
    if available:
        subscriptions = db.query(FavoriteProduct).join(User, User.id == FavoriteProduct.user_id).filter(
            FavoriteProduct.product_id == product.id, FavoriteProduct.restock_waiting.is_(True),
            User.role == "customer", User.status == 1,
        ).with_for_update().all()
        for favorite in subscriptions:
            db.add(CustomerRestockMessage(user_id=favorite.user_id, product_id=product.id, product_name=product.name, stock=product.stock))
            favorite.restock_waiting = False
    if state is None:
        state = ProductInventoryState(product_id=product.id)
        db.add(state)
    state.stock, state.available = product.stock, available
    db.flush()


def sync_all_inventory(db):
    for (product_id,) in db.query(Product.id).order_by(Product.id).all():
        sync_product_inventory(db, product_id)
