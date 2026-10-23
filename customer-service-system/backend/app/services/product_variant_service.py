"""商品 SKU 选择与库存变更。"""

from app.common.exceptions import BusinessException


def get_variants(product) -> list[dict]:
    return [dict(item) for item in (product.variants or []) if isinstance(item, dict)]


def select_variant(product, variant_key: str | None = None) -> dict | None:
    variants = get_variants(product)
    if not variants:
        if variant_key:
            raise BusinessException(message="该商品没有可选规格，请刷新页面")
        return None
    if not variant_key:
        raise BusinessException(message="请先选择商品规格")
    variant = next((item for item in variants if item.get("key") == variant_key), None)
    if not variant:
        raise BusinessException(message="所选规格已下架或发生变化，请刷新后重新选择")
    return variant


def selected_variant_data(product, variant_key: str | None = None) -> dict | None:
    variant = select_variant(product, variant_key)
    if not variant:
        return None
    return {
        "key": variant["key"],
        "name": variant["name"],
        "variant_name": product.variant_name or "规格",
        "price": float(variant["price"]),
        "stock": int(variant["stock"]),
    }


def variant_snapshot(product, variant: dict | None) -> str | None:
    if not variant:
        return None
    return f"{product.variant_name or '规格'}：{variant['name']}"


def available_stock(product, variant: dict | None) -> int:
    return int(variant["stock"]) if variant else int(product.stock)


def ensure_product_available(product, quantity: int = 1, variant_key: str | None = None) -> dict | None:
    if product.shelf_status != "on_sale" or product.review_status != "normal":
        raise BusinessException(message="该商品当前不可购买")
    variant = select_variant(product, variant_key)
    stock = available_stock(product, variant)
    if stock < quantity:
        suffix = f"（{variant['name']}）" if variant else ""
        raise BusinessException(message=f"{product.name}{suffix}库存不足，当前剩余 {stock} 件")
    return variant


def adjust_product_stock(product, quantity: int, variant_key: str | None = None) -> None:
    """按 SKU 调整库存，并同步商品级汇总库存。quantity 可为负数。"""
    variant = select_variant(product, variant_key)
    if not variant:
        product.stock += quantity
        return
    variants = get_variants(product)
    updated = []
    for item in variants:
        if item.get("key") == variant["key"]:
            item["stock"] = int(item["stock"]) + quantity
            if item["stock"] < 0:
                raise BusinessException(message=f"{product.name}（{item['name']}）库存不足")
        updated.append(item)
    product.variants = updated
    product.stock = sum(int(item["stock"]) for item in updated)


def replace_variants(product, variant_name: str | None, variants: list[dict]) -> None:
    product.variant_name = variant_name if variants else None
    product.variants = variants or None
    if variants:
        product.price = min(float(item["price"]) for item in variants)
        product.stock = sum(int(item["stock"]) for item in variants)
