"""将已完成的分析保存为业务报告；保存行为不产生消息通知。"""

import json

from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.models.diagnosis_report import DiagnosisReport
from app.observability.models import AgentRun


def save_run_report(db: Session, run_id: int, user_id: int) -> dict:
    run = db.query(AgentRun).filter(AgentRun.id == run_id, AgentRun.user_id == user_id).with_for_update().first()
    if not run or not run.answer_text:
        raise BusinessException(message="这次运行尚无可保存的完整回答", code=400)
    report = db.query(DiagnosisReport).filter(DiagnosisReport.source_run_id == run_id).first()
    if report:
        return {"report_id": report.id, "reused": True}
    payload = next((item.get("content", "") for item in run.answer_context or [] if item.get("role") == "user"), "")
    try:
        context = json.loads(payload)
    except (ValueError, TypeError):
        context = {}
    evidence = context.get("证据") or []
    ids = {item.get("product_id") for item in evidence if item.get("product_id") is not None}
    report = DiagnosisReport(
        source_run_id=run.id, question=run.question, summary=run.answer_text,
        route=run.route, risk_level=context.get("诊断风险信号") or "low", evidence=evidence, evidence_count=len(evidence),
        product_id=next(iter(ids)) if len(ids) == 1 else None, created_by=user_id,
    )
    db.add(report)
    db.commit()
    return {"report_id": report.id, "reused": False}


def update_report_answer(db: Session, run_id: int, answer: str) -> None:
    """明确请求诊断时先保留证据；模型返回后将正文更新为实际结论。"""
    report = db.query(DiagnosisReport).filter(DiagnosisReport.source_run_id == run_id).first()
    if report and answer:
        report.summary = answer
