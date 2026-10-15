import asyncio

import pytest

from yugan_agent.approvals import ApprovalBroker


@pytest.mark.asyncio
async def test_approve_all_is_limited_to_one_active_run():
    broker = ApprovalBroker(timeout_seconds=2)
    first_scope, other_scope = "a" * 32, "b" * 32
    assert broker.begin(first_scope)
    assert broker.begin(other_scope)

    first = asyncio.create_task(broker.request("type_text", "输入文字", {}, scope=first_scope))
    other = asyncio.create_task(broker.request("type_text", "另一任务", {}, scope=other_scope))
    await asyncio.sleep(0)
    assert len(broker.list_pending(first_scope)) == 1
    assert len(broker.list_pending(other_scope)) == 1

    assert broker.approve_all(first_scope)
    assert await first is True
    assert not other.done()
    assert await broker.request("press_key", "快捷键", {}, scope=first_scope) is True

    broker.end(first_scope)
    assert broker.begin(first_scope)
    next_run = asyncio.create_task(broker.request("type_text", "新任务", {}, scope=first_scope))
    await asyncio.sleep(0)
    assert len(broker.list_pending(first_scope)) == 1
    assert not next_run.done()

    assert broker.decide(broker.list_pending(first_scope)[0]["id"], False)
    assert broker.decide(broker.list_pending(other_scope)[0]["id"], False)
    assert await next_run is False
    assert await other is False
    broker.end(first_scope)
    broker.end(other_scope)
