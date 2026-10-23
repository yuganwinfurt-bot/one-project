"""导入电商示例数据（商品 / 订单 / 评价）。

用法（在 backend 目录、已激活虚拟环境）：
    python -m data.seed.seed_ecommerce

说明：
- 会清空商品 / 订单 / 评价及关联诊断报告、预警后重新写入
- 评价里含少量带图片路径的记录，供后续多模态章节使用
"""

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

# 保证以 python -m data.seed.seed_ecommerce 运行时能找到 app 包
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import SessionLocal, engine, Base
from app.models import AlertNotification, DiagnosisReport, Order, Product, Review
from app.observability.models import AgentFeedback, AgentRun, AgentRunStep


# ---------------------------------------------------------------------------
# 示例数据：某公司自营店，虚构类目与商品名
# ---------------------------------------------------------------------------

PRODUCTS = [
    {
        "name": "轻云运动跑鞋",
        "category": "鞋靴",
        "description": "轻量网面跑鞋，适合日常慢跑与通勤，鞋码偏大半码。",
        "price": Decimal("299.00"),
        "stock": 120,
    },
    {
        "name": "柔棉短袖T恤",
        "category": "服饰",
        "description": "100% 棉质短袖，多色可选，水洗后可能轻微缩水。",
        "price": Decimal("79.00"),
        "stock": 500,
    },
    {
        "name": "静音蓝牙耳机",
        "category": "数码",
        "description": "入耳式蓝牙耳机，支持降噪，续航约 6 小时。",
        "price": Decimal("199.00"),
        "stock": 80,
    },
    {
        "name": "保温杯 500ml",
        "category": "家居",
        "description": "不锈钢保温杯，保温 6 小时，杯盖可拆洗。",
        "price": Decimal("89.00"),
        "stock": 200,
    },
    {
        "name": "护脊书包",
        "category": "箱包",
        "description": "中学生护脊书包，分区收纳，肩带加宽。",
        "price": Decimal("159.00"),
        "stock": 60,
    },
    {
        "name": "厨房刀具套装",
        "category": "家居",
        "description": "三件套不锈钢刀具，含刀架，开刃出厂。",
        "price": Decimal("129.00"),
        "stock": 90,
    },
    {
        "name": "儿童益智积木",
        "category": "玩具",
        "description": "200 片积木，适合 3 岁以上，零件较小请家长看护。",
        "price": Decimal("99.00"),
        "stock": 150,
    },
    {
        "name": "洗衣液 2L",
        "category": "日用",
        "description": "浓缩洗衣液，低泡易漂，适合机洗。",
        "price": Decimal("39.90"),
        "stock": 300,
    },
    {
        "name": "防晒霜 SPF50",
        "category": "美妆",
        "description": "清爽防晒乳，适合油皮，防水防汗。",
        "price": Decimal("68.00"),
        "stock": 180,
    },
    {
        "name": "机械键盘青轴",
        "category": "数码",
        "description": "87 键机械键盘，青轴手感，支持键帽热插拔。",
        "price": Decimal("249.00"),
        "stock": 70,
    },
    {
        "name": "瑜伽垫 10mm",
        "category": "运动",
        "description": "加厚防滑瑜伽垫，附收纳绑带。",
        "price": Decimal("59.00"),
        "stock": 110,
    },
    {
        "name": "不锈钢炒锅 32cm",
        "category": "家居",
        "description": "无涂层炒锅，适合电磁炉与燃气灶。",
        "price": Decimal("189.00"),
        "stock": 45,
    },
    {
        "name": "速干运动短裤",
        "category": "服饰",
        "description": "透气速干面料，侧边口袋带拉链。",
        "price": Decimal("69.00"),
        "stock": 220,
    },
    {
        "name": "插座排插 6位",
        "category": "家电",
        "description": "六位插孔带独立开关，线长 1.8 米。",
        "price": Decimal("49.00"),
        "stock": 160,
    },
    {
        "name": "枕头慢回弹",
        "category": "家居",
        "description": "记忆棉枕头，透气外套可拆洗。",
        "price": Decimal("119.00"),
        "stock": 95,
    },
    {
        "name": "无线鼠标静音",
        "category": "数码",
        "description": "2.4G 无线鼠标，静音按键，续航约 12 个月。",
        "price": Decimal("59.00"),
        "stock": 140,
    },
    {
        "name": "帆布单肩包",
        "category": "箱包",
        "description": "日系帆布包，内含笔记本隔层。",
        "price": Decimal("89.00"),
        "stock": 75,
    },
    {
        "name": "电动牙刷套装",
        "category": "个护",
        "description": "声波电动牙刷，含 2 支刷头，续航约 30 天。",
        "price": Decimal("159.00"),
        "stock": 85,
    },
    {
        "name": "桌面小台灯",
        "category": "家居",
        "description": "三档亮度护眼台灯，USB 供电。",
        "price": Decimal("79.00"),
        "stock": 130,
    },
    {
        "name": "羽绒服轻薄款",
        "category": "服饰",
        "description": "90% 白鸭绒，可收纳成小袋，尺码偏小建议拍大一码。",
        "price": Decimal("399.00"),
        "stock": 55,
    },
]

BUYERS = [
    "小明",
    "阿花",
    "老王",
    "甜甜",
    "阿杰",
    "贝贝",
    "大伟",
    "圆圆",
    "小林",
    "静静",
]

# (product_index, rating, content, image_filename_or_None, days_ago)
REVIEW_SPECS = [
    (0, 5, "鞋子很轻，跑步不累脚，推荐。", None, 3),
    (0, 2, "尺码明显偏大，按平时码拍了结果松垮，客服让我自己垫鞋垫。", None, 5),
    (0, 1, "鞋底开胶了，穿了两周就这样，质量太差。", "shoe_glue-demo.jpg", 8),
    (0, 3, "外观还可以，但是鞋垫偏硬，走久了脚疼。", None, 12),
    (1, 5, "面料舒服，洗了不变形。", None, 2),
    (1, 2, "缩水严重，洗一次短了一截，差评。", None, 6),
    (1, 4, "颜色和图片差不多，性价比不错。", None, 10),
    (2, 1, "右耳没有声音，怀疑是次品。", "earphone_broken-demo.jpg", 4),
    (2, 2, "降噪一般，地铁里基本听不清。", None, 7),
    (2, 5, "音质超出预期，续航也够用。", None, 15),
    (3, 4, "保温效果可以，出门带水方便。", None, 1),
    (3, 1, "收到时杯盖裂了，包装也有压痕。", "broken_box-demo.jpg", 9),
    (4, 5, "背着挺舒服，孩子说分区好用。", None, 11),
    (4, 2, "拉链很容易卡住，质量一般。", None, 14),
    (5, 3, "刀还行，就是刀架塑料感太重。", None, 3),
    (5, 1, "刀刃有缺口，感觉是返修货。", None, 16),
    (6, 5, "孩子很喜欢，拼了好久。", None, 2),
    (6, 2, "少了好几块零件，联系客服补发很慢。", None, 8),
    (7, 4, "洗净效果不错，味道清淡。", None, 5),
    (7, 5, "比超市便宜，会回购。", None, 13),
    (8, 2, "涂完闷痘，油皮慎入。", None, 4),
    (8, 5, "不油腻，户外一天没有晒黑。", None, 18),
    (9, 1, "有好几个键失灵，退货中。", None, 6),
    (9, 4, "青轴清脆，打字爽。", None, 20),
    (10, 5, "厚度够，跪姿也不疼。", None, 7),
    (10, 3, "味道有点大，晾了两天才好。", None, 9),
    (11, 2, "手柄焊接处有毛刺，割手。", None, 11),
    (11, 5, "炒菜受热均匀，好用。", None, 17),
    (12, 4, "透气好，跑步出汗也能干得快。", None, 3),
    (12, 1, "尺码标错了，XL 穿起来像 M。", None, 12),
    (13, 5, "插孔够用，线也不短。", None, 1),
    (13, 2, "有一个开关按下去弹不起来。", None, 14),
    (14, 4, "睡着很舒服，回弹慢。", None, 5),
    (14, 1, "拆开有股刺鼻味道，怀疑不合格。", None, 19),
    (15, 5, "静音效果真好，办公室用很合适。", None, 2),
    (15, 3, "偶发卡顿，换电池后好了。", None, 10),
    (16, 4, "容量大，通勤够用。", None, 8),
    (16, 2, "肩带缝线开了，用了不到一个月。", None, 21),
    (17, 5, "刷牙干净，震动力度合适。", None, 4),
    (17, 1, "充电座接触不良，经常充不进电。", None, 15),
    (18, 4, "亮度够，夜间看书写作业可以。", None, 6),
    (18, 2, "按钮松动，一碰就自己切换档位。", None, 13),
    (19, 3, "保暖可以，但袖子偏短。", None, 7),
    (19, 1, "充绒不均匀，一边厚一边薄。", None, 22),
    (0, 2, "最近这双鞋差评好像变多了，我也中招，鞋帮磨脚。", None, 1),
    (2, 1, "包装破损，耳机仓有明显划痕。", "package_scratch-demo.jpg", 2),
]


def _ensure_review_sample_images() -> None:
    """样图随仓库提供；缺失时明确报错，不复制无关头像作为图片证据。"""
    sample_dir = BACKEND_ROOT / "uploads" / "review_samples"
    names = {spec[3] for spec in REVIEW_SPECS if spec[3]}
    missing = [name for name in sorted(names) if not (sample_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"缺少教学晒图：{', '.join(missing)}；请从仓库恢复 uploads/review_samples"
        )


def _clear_ecommerce_tables(db: Session) -> None:
    """先清理引用商品的教学产物，再清理业务表；由 seed 统一提交事务。

    观测三张表（步骤 / 反馈 → 运行）也一并清空：运行记录里留着上一次演示的问答，
    会让首页概览与观测看板的成功率、耗时、路由分布在录课时显示成旧数据。
    用户表不动——演示账号由 sql/ecommerce.sql 提供，清掉就没法登录了。
    """
    db.query(AgentRunStep).delete()
    db.query(AgentFeedback).delete()
    db.query(AgentRun).delete()
    db.query(AlertNotification).delete()
    db.query(DiagnosisReport).delete()
    db.query(Review).delete()
    db.query(Order).delete()
    db.query(Product).delete()


def seed(db: Session) -> None:
    """教学数据重置：清理和写入处于同一事务，失败时保留原数据。"""
    Base.metadata.create_all(bind=engine)
    _ensure_review_sample_images()
    try:
        _clear_ecommerce_tables(db)
        _insert_ecommerce_data(db)
        db.commit()
    except Exception:
        db.rollback()
        raise


def _insert_ecommerce_data(db: Session) -> None:
    """组装教学商品、订单和评价，由 seed 负责提交。"""

    now = datetime.now()
    products: list[Product] = []
    for item in PRODUCTS:
        product = Product(
            name=item["name"],
            category=item["category"],
            description=item["description"],
            price=item["price"],
            stock=item["stock"],
            shelf_status="on_sale",
            review_status="normal",
            create_time=now - timedelta(days=60),
            update_time=now - timedelta(days=30),
        )
        products.append(product)
    db.add_all(products)
    db.flush()  # 拿到自增 id

    orders: list[Order] = []
    reviews: list[Review] = []

    for idx, spec in enumerate(REVIEW_SPECS):
        product_idx, rating, content, image_name, days_ago = spec
        product = products[product_idx]
        created_at = now - timedelta(days=days_ago)

        order = Order(
            order_no=f"EO{20260000 + idx:08d}",
            product_id=product.id,
            buyer_name=BUYERS[idx % len(BUYERS)],
            quantity=1,
            amount=product.price,
            status="completed",
            create_time=created_at - timedelta(days=2),
            update_time=created_at - timedelta(days=1),
        )
        orders.append(order)
        db.add(order)
        db.flush()

        # 晒图的相对路径；没有图片的评价存 None
        img = f"/uploads/review_samples/{image_name}" if image_name else None
        review = Review(
            product_id=product.id,
            order_id=order.id,
            rating=rating,
            content=content,
            img=img,
            create_time=created_at,
            update_time=created_at,
        )
        reviews.append(review)

    db.add_all(reviews)
    db.flush()

    # 额外补几笔非「已完成」的订单，让订单状态字段在演示里能看到不同取值。
    # 它们不挂评价：已支付/已发货/已取消的订单本来就不该有买家评价。
    extra_orders = _insert_status_demo_orders(db, products, start_no=len(orders))
    orders.extend(extra_orders)

    with_image = sum(1 for r in reviews if r.img)
    print(
        f"种子数据写入完成：商品 {len(products)}，"
        f"订单 {len(orders)}（含状态演示 {len(extra_orders)} 笔），"
        f"评价 {len(reviews)}（含图 {with_image}）"
    )
    print("已清空：诊断报告、预警通知、运行记录 / 步骤 / 反馈（用户账号保留）")


# 除「已完成」之外的订单状态，各补一笔用于演示（索引, 状态, 几天前下单）
STATUS_DEMO_ORDERS = [
    (4, "paid", 3),
    (11, "shipped", 5),
    (16, "cancelled", 8),
]


def _insert_status_demo_orders(db: Session, products: list[Product], start_no: int) -> list[Order]:
    """插入几笔不同状态的订单（不带评价），让状态字段有数据可看。"""
    now = datetime.now()
    created: list[Order] = []
    for offset, (product_idx, status, days_ago) in enumerate(STATUS_DEMO_ORDERS):
        product = products[product_idx]
        order = Order(
            order_no=f"EO{20260000 + start_no + offset:08d}",
            product_id=product.id,
            buyer_name=BUYERS[(start_no + offset) % len(BUYERS)],
            quantity=1,
            amount=product.price,
            status=status,
            create_time=now - timedelta(days=days_ago),
            update_time=now - timedelta(days=days_ago),
        )
        created.append(order)
        db.add(order)
    db.flush()
    return created


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
