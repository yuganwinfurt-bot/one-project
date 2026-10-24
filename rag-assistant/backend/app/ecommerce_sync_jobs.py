"""单进程后台同步任务；SQLite 只保存进度和结果，不保存业务快照。"""

import asyncio
import json
import logging

from fastapi import HTTPException

from .database import connect, new_id, now_iso

logger = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()


def recover_interrupted_jobs():
    with connect() as db:
        db.execute(
            "UPDATE ecommerce_sync_jobs SET status = 'interrupted', stage = 'interrupted', "
            "error = ?, updated_at = ? WHERE status IN ('queued', 'running')",
            ("RAG 服务已重启，上次同步中断，请重新同步。", now_iso()),
        )


def _serialize(row):
    if row is None:
        return None
    job = dict(row)
    job["result"] = json.loads(job["result"])
    return job


def get_job(job_id=None, *, source="ecommerce"):
    with connect() as db:
        if job_id is None:
            row = db.execute(
                "SELECT * FROM ecommerce_sync_jobs WHERE source = ? ORDER BY rowid DESC LIMIT 1", (source,)
            ).fetchone()
        else:
            row = db.execute("SELECT * FROM ecommerce_sync_jobs WHERE id = ? AND source = ?", (job_id, source)).fetchone()
    return _serialize(row)


def update_job(job_id, *, only_running=False, **values):
    allowed = {"status", "stage", "processed_chunks", "total_chunks", "result", "error", "reused_chunks", "embedded_chunks"}
    if not values or not set(values) <= allowed:
        raise ValueError("Invalid job update")
    if "result" in values:
        values["result"] = json.dumps(values["result"], ensure_ascii=False)
    values["updated_at"] = now_iso()
    columns = ", ".join(f"{column} = ?" for column in values)
    condition = " AND status = 'running'" if only_running else ""
    with connect() as db:
        db.execute(f"UPDATE ecommerce_sync_jobs SET {columns} WHERE id = ?{condition}", (*values.values(), job_id))


def start_job(record_count, runner, lock, *, source="ecommerce"):
    # BEGIN IMMEDIATE 防止两次点击同时创建全量任务。
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM ecommerce_sync_jobs WHERE source = ? AND status IN ('queued', 'running') "
            "ORDER BY rowid DESC LIMIT 1", (source,)
        ).fetchone()
        if row:
            return {**_serialize(row), "reused": True}
        job_id = new_id()
        stamp = now_iso()
        db.execute(
            "INSERT INTO ecommerce_sync_jobs "
            "(id, source, status, stage, record_count, created_at, updated_at) VALUES (?, ?, 'queued', 'queued', ?, ?, ?)",
            (job_id, source, record_count, stamp, stamp),
        )
    task = asyncio.create_task(_run(job_id, runner, lock), name=f"ecommerce-sync-{job_id}")
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return get_job(job_id, source=source)


async def _run(job_id, runner, lock):
    try:
        async with lock:
            update_job(job_id, status="running", stage="preparing")

            def progress(done, total, *, reused_chunks=0, embedded_chunks=0, stage="indexing"):
                update_job(job_id, only_running=True, stage=stage, processed_chunks=done, total_chunks=total,
                           reused_chunks=reused_chunks, embedded_chunks=embedded_chunks)

            result = await runner(progress)
            count = int(result.get("chunk_count") or 0)
            update_job(job_id, status="succeeded", stage="done", result=result,
                       processed_chunks=count, total_chunks=count,
                       reused_chunks=int(result.get("reused_chunks") or 0),
                       embedded_chunks=int(result.get("embedded_chunks") or 0))
    except asyncio.CancelledError:
        update_job(job_id, status="interrupted", stage="interrupted",
                   error="RAG 服务停止，上次同步中断，请重新同步。")
        raise
    except Exception as exc:
        logger.exception("电商后台同步任务失败：%s", job_id)
        detail = exc.detail if isinstance(exc, HTTPException) and isinstance(exc.detail, str) else "同步失败，请查看 RAG 服务日志后重试。"
        update_job(job_id, status="failed", stage="failed", error=detail)
