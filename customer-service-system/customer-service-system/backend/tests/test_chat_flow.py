"""实际跑图验证确认与失败恢复；业务执行、数据库和模型均隔离。"""
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from types import SimpleNamespace

import pytest
from langgraph.checkpoint.memory import MemorySaver

from app.agent import graph as graph_module, nodes
from app.common.exceptions import BusinessException
from app.services import chat_service, confirmation_service

REAL_EXECUTE_ACTIONS = nodes.node_execute_actions


@pytest.fixture()
def flow(monkeypatch):
    monkeypatch.setattr(graph_module, "_compiled_graph", None)
    monkeypatch.setattr(graph_module, "_checkpointer", MemorySaver())
    rows = [{"review_id": i, "product_id": 1, "rating": 1, "content": f"bad{i}"} for i in range(3)]
    monkeypatch.setattr(nodes, "query_mysql", lambda question: {"rows": rows, "row_count": 3})
    monkeypatch.setattr(nodes, "query_chroma", lambda *args, **kwargs: {"hits": []})
    monkeypatch.setattr(nodes, "query_logs", lambda **kwargs: {"runs": []})
    monkeypatch.setattr(chat_service, "_load_product_names", lambda: ["product"])
    monkeypatch.setattr(chat_service, "chat_stream", lambda *args: iter(["answer"]))
    monkeypatch.setattr(chat_service.obs_service, "create_run", lambda *args, **kwargs: SimpleNamespace(id=1))
    monkeypatch.setattr(chat_service, "_record_step", lambda *args, **kwargs: None)
    finished = []
    monkeypatch.setattr(chat_service, "_finish_run_safe", lambda *args, **kwargs: finished.append(kwargs))

    class NoopSession:
        def query(self, *args): return self
        def filter(self, *args): return self
        def order_by(self, *args): return self
        def first(self): return None
        def close(self): pass

    monkeypatch.setattr(chat_service, "SessionLocal", NoopSession)
    executions = []

    def execute(state):
        executions.append(state["question"])
        return {"actions_executed": [{"type": "write_report", "ok": True}], "status_message": "done"}

    monkeypatch.setattr(nodes, "node_execute_actions", execute)
    return SimpleNamespace(executions=executions, finished=finished)


def events():
    return [
        (block.splitlines()[0].removeprefix("event: "), json.loads(block.splitlines()[1].removeprefix("data: ")))
        for block in chat_service.stream_chat("product", user_id=1)
    ]


def pending_thread():
    return next(data["thread_id"] for name, data in events() if name == "action_pending")


def test_concurrent_confirmation_executes_once(flow, monkeypatch):
    thread_id = pending_thread()
    start = Barrier(3)
    entered = Event()
    release = Event()

    def execute(state):
        entered.set()
        assert release.wait(5)
        flow.executions.append(state["question"])
        return {"actions_executed": [{"type": "write_report", "ok": True}]}

    monkeypatch.setattr(nodes, "node_execute_actions", execute)

    def confirm():
        start.wait(timeout=5)
        try:
            return confirmation_service.resume_actions(thread_id, True, user_id=1)
        except BusinessException as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(confirm) for _ in range(2)]
        try:
            start.wait(timeout=5)
            assert entered.wait(5)
        finally:
            release.set()
        results = [future.result(timeout=5) for future in futures]
    assert len(flow.executions) == 1
    assert sum(isinstance(result, BusinessException) for result in results) == 1


def test_other_user_cannot_confirm(flow):
    thread_id = pending_thread()
    with pytest.raises(BusinessException) as exc:
        confirmation_service.resume_actions(thread_id, True, user_id=2)
    assert exc.value.code == 403
    assert not flow.executions


def test_cancel_skips_business_actions(flow, monkeypatch):
    from app.services import action_service

    # 用真实执行节点检查取消分支，避免替代执行器绕过批准判断。
    monkeypatch.setattr(nodes, "node_execute_actions", REAL_EXECUTE_ACTIONS)
    monkeypatch.setattr(action_service, "execute_actions", lambda *args: pytest.fail("取消后不应写库"))
    thread_id = pending_thread()
    result = confirmation_service.resume_actions(thread_id, False, user_id=1)
    assert result["human_approved"] is False
    assert result["actions_executed"] == []


@pytest.mark.parametrize("error", [BusinessException("总结超时"), RuntimeError("模型连接失败")])
def test_answer_failure_preserves_pending_confirmation(flow, monkeypatch, error):
    def fail_answer(*args):
        raise error

    monkeypatch.setattr(chat_service, "chat_stream", fail_answer)
    output = events()
    thread_id = next(data["thread_id"] for name, data in output if name == "action_pending")
    assert any(name == "error" and data["awaiting_confirmation"] for name, data in output)
    assert output[-1][0] == "done"
    assert flow.finished[-1]["status"] == "awaiting_confirm"
    assert confirmation_service.get_pending_confirmation(thread_id, user_id=1)["actions"]
    assert confirmation_service.get_pending_confirmation(thread_id, user_id=2) is None
    assert confirmation_service.resume_actions(thread_id, True, user_id=1)["human_approved"] is True


def test_pending_entry_disappears_after_completion(flow):
    thread_id = pending_thread()
    confirmation_service.resume_actions(thread_id, True, user_id=1)
    assert confirmation_service.get_pending_confirmation(thread_id, user_id=1) is None


def test_pending_entry_disappears_after_restart(flow, monkeypatch):
    thread_id = pending_thread()
    monkeypatch.setattr(graph_module, "_compiled_graph", None)
    monkeypatch.setattr(graph_module, "_checkpointer", MemorySaver())
    assert confirmation_service.get_pending_confirmation(thread_id, user_id=1) is None
