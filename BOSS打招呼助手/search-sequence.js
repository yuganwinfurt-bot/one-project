// 多城市搜索只推进已确认的步骤；所有入口共用同一份持久化状态。
let searchSequenceMutation = Promise.resolve();

function mutateSearchSequence(mutator) {
  const task = searchSequenceMutation.then(async () => {
    const result = await mutator(await getAutoSearchBatch());
    if (result && Object.prototype.hasOwnProperty.call(result, 'batch')) {
      if (result.batch) await setAutoSearchBatch(result.batch);
      else await clearAutoSearchBatch();
    }
    return result?.value;
  });
  searchSequenceMutation = task.catch(() => {});
  return task;
}

function searchConditionKey(value) {
  try {
    const url = new URL(value);
    if (url.origin !== 'https://www.zhipin.com' || url.pathname !== '/web/geek/jobs') return '';
    return JSON.stringify([
      (url.searchParams.get('query') || url.searchParams.get('keyword') || '').trim(),
      url.searchParams.get('city') || '', url.searchParams.get('jobType') || '0',
      url.searchParams.get('salary') || '0', url.searchParams.get('position') || '',
    ]);
  } catch { return ''; }
}

function attachSearchSequence(url, tabId) {
  return mutateSearchSequence(async batch => {
    const key = searchConditionKey(url);
    if (!key || !tabId) return { value: { ok: false, error: '无法确认当前岗位搜索页' } };
    if (batch?.id && (batch.currentTabId || batch.launching || batch.index < batch.conditions.length)) {
      const current = batch.conditions[Math.max(0, batch.index - 1)];
      if (Number(batch.currentTabId) === Number(tabId) && searchConditionKey(current?.url) === key) {
        // 兼容升级前没有步骤编号的活动批次。
        batch.currentStepToken ||= `${batch.id}:${batch.index}`;
        return { batch, value: { ok: true, batchId: batch.id, stepToken: batch.currentStepToken } };
      }
      return { value: { ok: false, error: '已有顺序搜索正在运行，请先停止该任务' } };
    }
    const data = await chrome.storage.local.get(SETTINGS_KEY);
    const conditions = (data[SETTINGS_KEY]?.autoSearch?.conditions || []).filter(item => item?.enabled && searchConditionKey(item.url));
    const index = conditions.findIndex(item => searchConditionKey(item.url) === key);
    if (index < 0) return { value: { ok: true, batchId: '', stepToken: '' } };
    // 从用户当前搜索项接入，按原配置顺序继续其余项目，不重新导航或重扫当前项。
    const ordered = [...conditions.slice(index), ...conditions.slice(0, index)];
    const id = `search-batch-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const next = { id, conditions: ordered, index: 1, currentTabId: tabId, searchTabId: tabId, lastCompletedTabId: 0, currentConditionId: ordered[0].id || '', currentStepToken: `${id}:1`, launching: false, startedAt: Date.now() };
    return { batch: next, value: { ok: true, batchId: id, stepToken: next.currentStepToken } };
  });
}

function scheduleSearchSequence(batchId) {
  setTimeout(() => { void runNextAutoSearchBatch(batchId).catch(error => recordSearchSequenceError(error, batchId)); }, 300);
}

function recordSearchSequenceError(error, batchId) {
  return recordDeliveryDiagnostic({ phase: 'search-sequence', action: 'handoff', status: 'failed', stage: '顺序搜索交接失败', taskId: batchId, reason: safeDiagnosticValue(error?.message) });
}

async function runSearchSequenceStep(batchId) {
  const launch = await mutateSearchSequence(async batch => {
    if (!batch || batch.id !== batchId || batch.currentTabId || batch.launching) return;
    const data = await chrome.storage.local.get(DELIVERY_TASK_QUEUE_KEY);
    const queue = data[DELIVERY_TASK_QUEUE_KEY] || {};
    if (queue.active || queue.pending?.length) {
      batch.waitingForDelivery = true;
      return { batch, value: null };
    }
    if (batch.index >= batch.conditions.length) return { batch: null, value: null };
    const config = batch.conditions[batch.index];
    batch.index += 1;
    batch.launching = true;
    batch.waitingForDelivery = false;
    batch.launchStartedAt = Date.now();
    batch.currentConditionId = config.id || '';
    batch.currentStepToken = `${batch.id}:${batch.index}`;
    return { batch, value: { config, token: batch.currentStepToken, tabId: batch.searchTabId || batch.lastCompletedTabId } };
  });
  if (!launch) return;
  void recordDeliveryDiagnostic({ phase: 'search-sequence', action: 'next', status: 'launching', stage: `正在切换下一搜索项：${launch.config.city || ''} · ${launch.config.keyword || ''}`, taskId: batchId });
  const result = await new Promise(resolve => openAutoSearch(launch.config, resolve, batchId, launch.tabId, launch.token));
  const accepted = await mutateSearchSequence(batch => {
    if (!batch || batch.id !== batchId || batch.currentStepToken !== launch.token || !batch.launching) return;
    batch.launching = false;
    if (result?.ok) {
      batch.currentTabId = result.tabId;
      batch.searchTabId = result.tabId;
    }
    return { batch, value: true };
  });
  if (accepted && !result?.ok) {
    void recordSearchSequenceError(new Error(result?.error || '未能导航到下一搜索项'), batchId);
    scheduleSearchSequence(batchId);
  }
}

async function completeSearchSequenceStep(batchId, tabId, stepToken) {
  const result = await mutateSearchSequence(batch => {
    if (!batch || batch.id !== batchId) return { value: { ok: true, stale: true } };
    if (stepToken && batch.lastCompletedStepToken === stepToken) return { value: { ok: true, duplicate: true } };
    if (!batch.currentTabId || Number(batch.currentTabId) !== Number(tabId)
      || (batch.currentStepToken && batch.currentStepToken !== stepToken)) return { value: { ok: false, stale: true, error: '完成通知与当前搜索步骤不一致' } };
    batch.currentTabId = 0;
    batch.lastCompletedTabId = Number(tabId);
    batch.lastCompletedStepToken = stepToken || '';
    batch.waitingForDelivery = true;
    return { batch, value: { ok: true, accepted: true } };
  });
  if (result?.accepted) {
    void recordDeliveryDiagnostic({ phase: 'search-sequence', action: 'complete', status: 'accepted', stage: '本搜索项已完成，等待投递队列清空后切换下一项', taskId: batchId, tabId });
    scheduleSearchSequence(batchId);
  }
  return result;
}

async function recoverSearchSequence() {
  const [batch, data] = await Promise.all([getAutoSearchBatch(), chrome.storage.local.get('bqa-search-run-status')]);
  if (!batch?.id) return;
  const run = data['bqa-search-run-status'];
  if (run?.batchId === batch.id && run.stepToken === batch.currentStepToken && Number(run.tabId) === Number(batch.currentTabId)) {
    if (['stopped', 'daily-limit'].includes(run.status)) return abortAutoSearchBatch(batch.id);
    if (['completed', 'partial', 'failed', 'interrupted'].includes(run.status)) {
      await completeSearchSequenceStep(batch.id, run.tabId, run.stepToken);
      return;
    }
  }
  if (batch.launching && Date.now() - Number(batch.launchStartedAt || 0) > 30000) {
    const data = await chrome.storage.local.get(AUTO_SEARCH_PENDING_KEY);
    const pending = Object.values(pendingAutoSearchByTab(data[AUTO_SEARCH_PENDING_KEY])).find(item => item.batchId === batch.id && item.stepToken === batch.currentStepToken);
    await mutateSearchSequence(latest => {
      if (!latest || latest.id !== batch.id || latest.currentStepToken !== batch.currentStepToken || !latest.launching) return;
      latest.launching = false;
      if (run?.batchId === latest.id && run.stepToken === latest.currentStepToken && run.status === 'running' && Number(run.tabId) === Number(latest.searchTabId)) {
        latest.currentTabId = Number(run.tabId);
      } else if (pending?.tabId) {
        latest.currentTabId = Number(pending.tabId);
        latest.searchTabId = Number(pending.tabId);
      } else latest.index = Math.max(0, latest.index - 1);
      return { batch: latest };
    });
  }
  const latest = await getAutoSearchBatch();
  if (latest?.id && !latest.currentTabId && !latest.launching) await runNextAutoSearchBatch(latest.id);
}
