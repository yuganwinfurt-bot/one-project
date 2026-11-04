// 诊断只读取任务状态；不领取、重试、取消任务或发送消息。
function queueDiagnosticText(value, limit = 160) {
  return String(value ?? '').replace(/https?:\/\/\S+/gi, '[url]')
    .replace(/sk-[A-Za-z0-9_-]{12,}/g, '[已隐藏密钥]').slice(0, limit);
}

function deliveryTaskWriteRejection(active, id, tabId, claimedAt, execution) {
  let failureType = ''; let reason = '';
  if (!active || active.id !== id) {
    failureType = 'task-mismatch'; reason = '任务已结束或队首已切换';
  } else if (tabId && active.claimedTabId && Number(active.claimedTabId) !== Number(tabId)) {
    failureType = 'writer-tab-mismatch'; reason = '回传标签页不是领取任务的标签页，后台拒绝写入';
  } else if ((claimedAt && Number(active.claimedAt) !== Number(claimedAt))
    || (execution?.queueLeaseAt && Number(active.claimedAt) !== Number(execution.queueLeaseAt))) {
    failureType = 'lease-mismatch'; reason = '回传的领取时间与当前任务不一致，后台拒绝写入';
  }
  return failureType ? {
    failureType, reason, taskId: queueDiagnosticText(id),
    expectedTabId: Number(active?.claimedTabId || 0), senderTabId: Number(tabId || 0),
    chatTabId: Number(active?.execution?.chatTabId || execution?.chatTabId || 0),
    expectedLeaseAt: Number(active?.claimedAt || 0), leaseAt: Number(claimedAt || execution?.queueLeaseAt || 0),
    requestedStage: queueDiagnosticText(execution?.stage),
  } : null;
}

function buildDeliveryQueueDiagnostic(queue, tabs, records, logs, now = Date.now()) {
  const active = queue?.active || null;
  const pending = Array.isArray(queue?.pending) ? queue.pending : [];
  const execution = active?.execution || null;
  const jobs = Array.isArray(execution?.jobs) ? execution.jobs : Array.isArray(active?.jobs) ? active.jobs : [];
  const index = Math.max(0, Number(execution?.index) || 0);
  const aliveTabs = new Map((Array.isArray(tabs) ? tabs : []).map(tab => [Number(tab.id), tab]));
  const age = stamp => Number(stamp) > 0 ? Math.max(0, now - Number(stamp)) : null;
  const describeJob = job => job ? {
    id: queueDiagnosticText(job.id), title: queueDiagnosticText(job.title, 80), company: queueDiagnosticText(job.company, 60),
  } : null;
  const stageAgeMs = age(execution?.stageUpdatedAt || active?.claimedAt || active?.startedAt || active?.createdAt);
  const diagnostics = [];
  if (!active && pending.length) diagnostics.push('队列有待处理任务，但没有队首执行者。');
  if (active && !active.claimedTabId) diagnostics.push('队首尚未被任何岗位列表页领取。');
  if (active?.claimedTabId && !aliveTabs.has(Number(active.claimedTabId))) diagnostics.push('领取任务的列表页已关闭，正在等待队列恢复。');
  if (active?.claimedTabId && !execution && stageAgeMs > 30000) diagnostics.push('任务已领取超过 30 秒，执行状态仍未创建。');
  if (execution?.waitingForChat) diagnostics.push(`队首正在等待详情/聊天页回传结果，阶段已约 ${Math.floor((stageAgeMs || 0) / 1000)} 秒未更新；后续任务暂不能开始。`);
  if (execution?.chatTabId && !aliveTabs.has(Number(execution.chatTabId))) diagnostics.push('任务登记的详情/聊天标签页已关闭，尚未完成队列收尾。');
  if (execution && stageAgeMs > 180000) diagnostics.push('执行状态已超过 3 分钟没有更新，将触发现有队列超时处理。');
  const rejection = [...(Array.isArray(logs) ? logs : [])].reverse().find(event => active && event.taskId === active.id && event.status === 'rejected' && Date.parse(event.time) >= Number(active.claimedAt || active.createdAt || 0) && ['writer-tab-mismatch', 'lease-mismatch', 'task-mismatch'].includes(event.failureType));
  if (rejection) diagnostics.push(`该任务曾有回传被拒：${queueDiagnosticText(rejection.reason || rejection.stage)}（发送页 ${Number(rejection.senderTabId || rejection.tabId || 0)}，领取页 ${Number(rejection.expectedTabId || 0)}）。请结合下方事件时间查看。`);
  const queuedIds = new Set([...(active?.jobs || []), ...pending.flatMap(task => task.jobs || [])].map(job => String(job?.id || '')).filter(Boolean));
  const queuedRecords = (Array.isArray(records) ? records : []).filter(record => record?.deliveryStatus === '排队中');
  const orphaned = queuedRecords.filter(record => !queuedIds.has(String(record.id || '')));
  if (orphaned.length) diagnostics.push(`有 ${orphaned.length} 条记录显示排队中，但当前实际队列中没有对应任务。`);
  if (!diagnostics.length) diagnostics.push(active ? '队首已有执行者，暂未从当前快照发现明确阻塞；请刷新并查看阶段是否前进。' : '当前实际投递队列为空。');
  return {
    capturedAt: new Date(now).toISOString(), pendingTaskCount: pending.length,
    pendingJobCount: pending.reduce((sum, task) => sum + (Array.isArray(task.jobs) ? task.jobs.length : 0), 0),
    active: active ? {
      taskId: queueDiagnosticText(active.id), stage: queueDiagnosticText(execution?.stage || (active.claimedTabId ? '已领取，等待创建执行状态' : '等待领取')),
      claimedTabId: Number(active.claimedTabId || 0), chatTabId: Number(execution?.chatTabId || 0),
      controllerAlive: aliveTabs.has(Number(active.claimedTabId)), chatAlive: execution?.chatTabId ? aliveTabs.has(Number(execution.chatTabId)) : null,
      waitingForChat: Boolean(execution?.waitingForChat), executionPresent: Boolean(execution),
      index, jobCount: jobs.length, currentJob: describeJob(jobs[index]), stageAgeMs,
      queueAgeMs: age(active.createdAt), claimAgeMs: age(active.claimedAt),
    } : null,
    queuedRecordCount: queuedRecords.length, orphanQueuedCount: orphaned.length,
    orphanQueuedPreview: orphaned.slice(0, 8).map(describeJob),
    pendingPreview: pending.slice(0, 8).map(task => ({ taskId: queueDiagnosticText(task.id), queueAgeMs: age(task.createdAt), jobCount: task.jobs?.length || 0, firstJob: describeJob(task.jobs?.[0]) })),
    tabs: (Array.isArray(tabs) ? tabs : []).map(tab => {
      let route = ''; let worker = false;
      try { const url = new URL(tab.url); route = url.pathname; worker = url.hash === '#bqa-delivery-worker'; } catch { /* 不导出原始 URL */ }
      return { tabId: Number(tab.id), route, worker, status: queueDiagnosticText(tab.status, 30), active: Boolean(tab.active), discarded: Boolean(tab.discarded) };
    }),
    diagnoses: diagnostics,
  };
}
