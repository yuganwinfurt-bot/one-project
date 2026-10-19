"""诊断报告与预警通知的出参模型（Agent 写操作的产物）。"""

from datetime import datetime
from typing import Any

from pydantic import field_serializer

from app.schemas.base import RowItem


class DiagnosisReportItem(RowItem):
    """诊断报告（Agent 写操作的产物，只读展示）。"""

    id: int
    question: str
    source_run_id: int | None = None
    summary: str
    route: str | None = None
    risk_level: str
    evidence_count: int
    product_id: int | None = None
    product_name: str | None = None
    create_time: datetime | None = None

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class DiagnosisReportDetail(DiagnosisReportItem):
    """诊断报告详情，包含生成时保存的证据明细。"""

    evidence: list[dict[str, Any]] | None = None


class AlertItem(RowItem):
    """站内预警通知（Agent 写操作的产物，只读展示）。"""

    id: int
    title: str
    content: str
    level: str
    product_id: int | None = None
    product_name: str | None = None
    report_id: int | None = None
    is_read: int = 0
    create_time: datetime | None = None


    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None
