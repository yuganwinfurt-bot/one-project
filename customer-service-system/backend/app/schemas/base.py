"""出参模型的公共基类。"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict


class RowItem(BaseModel):
    """从数据库行构造的出参基类。

    列表查询常带 JOIN 出来的额外列（例如订单列表要显示商品名），这些列不在 ORM 实体上，
    需要校验之后再补进出参。统一走 `from_row`，避免每个 service 各写一遍
    `model_validate(...).model_copy(update=...)`。
    """

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_row(cls, row: Any, **extra: Any) -> Self:
        """把 ORM 行转成出参，并按字段名补上查询里的额外列。

        额外列名先对着模型字段校验一遍：`model_copy(update=...)` 本身不校验，
        写错字段名会被静默塞进对象里，这里让它直接报错。
        """
        unknown = set(extra) - set(cls.model_fields)
        if unknown:
            raise ValueError(f"{cls.__name__} 没有这些字段：{sorted(unknown)}")
        return cls.model_validate(row).model_copy(update=extra)
