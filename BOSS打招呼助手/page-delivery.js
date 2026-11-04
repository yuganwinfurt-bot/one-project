// 页面只报告结果；后台校验任务身份、保存记录并推进队列，避免跨标签页覆盖状态。
const PAGE_DELIVERY_TAB_KEY = 'bqa-page-delivery-tab';
const PAGE_DELIVERY_CHILD_TABS_KEY = 'bqa-page-delivery-child-tabs';
let pageDeliveryTabMutation = Promise.resolve();
let pageDeliveryResultMutation = Promise.resolve();
let idleDeliveryTabTimer = 0;

function scheduleIdleDeliveryTabCleanup() {
  clearTimeout(idleDeliveryTabTimer);
  // 先让结果回执返回；紧接着到来的任务可继续复用执行页。
  idleDeliveryTabTimer = setTimeout(() => {
    idleDeliveryTabTimer = 0;
    void closeIdleDeliveryTabs().catch(error => recordDeliveryDiagnostic({ phase: 'tab-lifecycle', action: 'cleanup', status: 'failed', stage: '临时投递页回收失败', reason: safeDiagnosticValue(error?.message) }));
  }, 1000);
}

function trackDeliveryChildTab(tab) {
  if (!tab?.id || !tab.openerTabId) return Promise.resolve(false);
  const task = pageDeliveryTabMutation.then(async () => {
    const data = await chrome.storage.local.get([PAGE_DELIVERY_TAB_KEY, PAGE_DELIVERY_CHILD_TABS_KEY, DELIVERY_TASK_QUEUE_KEY]);
    const execution = data[DELIVERY_TASK_QUEUE_KEY]?.active?.execution;
    const helperId = Number(data[PAGE_DELIVERY_TAB_KEY]);
    // 只记录本次投递执行页产生的子页，用户从搜索页手动打开的岗位不受影响。
    if (Number(tab.openerTabId) !== helperId || Number(execution?.chatTabId) !== helperId || !execution.waitingForChat) return false;
    const children = Array.isArray(data[PAGE_DELIVERY_CHILD_TABS_KEY]) ? data[PAGE_DELIVERY_CHILD_TABS_KEY] : [];
    await chrome.storage.local.set({ [PAGE_DELIVERY_CHILD_TABS_KEY]: [...children.filter(item => item.id !== tab.id), { id: tab.id, openerTabId: helperId }].slice(-50) });
    return true;
  });
  pageDeliveryTabMutation = task.catch(() => {});
  return task;
}

function closeIdleDeliveryTabs() {
  const task = pageDeliveryTabMutation.then(async () => {
    const data = await chrome.storage.local.get([PAGE_DELIVERY_TAB_KEY, PAGE_DELIVERY_CHILD_TABS_KEY, DELIVERY_TASK_QUEUE_KEY]);
    const queue = data[DELIVERY_TASK_QUEUE_KEY] || {};
    if (queue.active || queue.pending?.length) return false;
    const helperId = Number(data[PAGE_DELIVERY_TAB_KEY]);
    const children = Array.isArray(data[PAGE_DELIVERY_CHILD_TABS_KEY]) ? data[PAGE_DELIVERY_CHILD_TABS_KEY] : [];
    const ids = [...new Set([...children.map(item => Number(item.id)), helperId].filter(Boolean))];
    const kept = new Set();
    for (const id of ids) {
      let tab;
      try { tab = await chrome.tabs.get(id); } catch { continue; }
      // 用户把临时页改为其他网站时，交还给用户，不自动关闭。
      let ownedRoute = tab.url === 'about:blank';
      try { ownedRoute ||= new URL(tab.url).origin === 'https://www.zhipin.com'; } catch { /* 等待后续清理 */ }
      if (!ownedRoute) continue;
      try {
        await chrome.tabs.remove(id);
        void recordDeliveryDiagnostic({ phase: 'tab-lifecycle', action: 'cleanup', status: 'closed', stage: '队列已清空，已关闭临时投递页', tabId: id });
      } catch { kept.add(id); }
    }
    await chrome.storage.local.set({ [PAGE_DELIVERY_TAB_KEY]: kept.has(helperId) ? helperId : null, [PAGE_DELIVERY_CHILD_TABS_KEY]: children.filter(item => kept.has(Number(item.id))) });
    return true;
  });
  pageDeliveryTabMutation = task.catch(() => {});
  return task;
}

function pageDeliveryResultRejection(active, message, tabId) {
  const execution = active?.execution;
  if (!active || active.id !== message.taskId || !execution?.active) return '任务已结束或已切换';
  if (!tabId || Number(execution.chatTabId) !== Number(tabId)) return '回执不是来自本任务登记的详情/聊天页';
  if (Number(active.claimedAt) !== Number(message.claimedAt) || execution.sessionId !== message.sessionId) return '回执的任务会话或领取时间已失效';
  if (!canonicalDeliveryJobId(message.jobId) || !execution.waitingForChat || Number(execution.index) !== Number(message.index)
    || canonicalDeliveryJobId(execution.jobs?.[execution.index]?.id) !== canonicalDeliveryJobId(message.jobId)) return '回执对应的岗位已处理或已切换';
  return '';
}

function pageDeliveryStageAllowed(active, execution, tabId, claimedAt) {
  return !pageDeliveryResultRejection(active, {
    taskId: active?.id, claimedAt, sessionId: execution?.sessionId,
    index: execution?.index, jobId: execution?.jobs?.[execution?.index]?.id,
  }, tabId);
}

function finishPageDelivery(message, tabId) {
  const task = pageDeliveryResultMutation.then(async () => {
    const data = await chrome.storage.local.get(DELIVERY_TASK_QUEUE_KEY);
    const queue = data[DELIVERY_TASK_QUEUE_KEY] || {};
    const duplicate = (queue.completedPages || []).some(item => item.taskId === message.taskId
      && item.sessionId === message.sessionId && item.jobId === canonicalDeliveryJobId(message.jobId)
      && Number(item.index) === Number(message.index)
      && Number(item.tabId) === Number(tabId) && Number(item.claimedAt) === Number(message.claimedAt));
    if (duplicate) return { ok: true, alreadyCompleted: true };
    const rejection = pageDeliveryResultRejection(queue.active, message, tabId);
    if (rejection) {
      void recordDeliveryDiagnostic({ phase: 'page-result', action: 'finish', status: 'rejected', stage: rejection, taskId: message.taskId, jobId: message.jobId, senderTabId: tabId });
      return { ok: false, stale: true, error: rejection };
    }
    const batch = queue.active.execution;
    const job = batch.jobs[batch.index];
    const success = message.success === true;
    const evidence = String(message.evidence || '');
    const historical = message.alreadyContacted === true && evidence === 'existing-conversation';
    const allowed = batch.useBossNativeGreeting ? ['chat-page', 'chat-input', 'detail-button-changed'] : ['greeting-sent'];
    if (success && !allowed.includes(evidence)) return { ok: false, error: '缺少可确认的沟通结果，未记录成功' };
    const error = queueDiagnosticText(message.error || '页面沟通未能完成', 500);
    if (historical) {
      if (!(await readDeliveredJob(job))) await upsertDeliveryRecord({ ...job, deliveryStatus: '已沟通（历史）', historical: true, historyDetectedAt: Date.now(), sessionId: batch.sessionId, error: '' });
    } else if (success) {
      const committed = await confirmDeliveredAfterChat(job, batch.sessionId);
      if (!committed.synced) throw new Error(committed.error || '沟通结果尚未保存，请重试回执');
    } else {
      await upsertDeliveryRecord({ ...job, deliveryStatus: '投递失败', sessionId: batch.sessionId, error });
    }
    const advanced = await mutateDeliveryTaskQueue(current => {
      if (pageDeliveryResultRejection(current.active, message, tabId)) return false;
      const latest = current.active.execution;
      const nextExecution = {
        ...latest, index: latest.index + 1, waitingForChat: false,
        stage: historical ? '已确认历史沟通，跳过并继续下一岗位' : success ? '已确认沟通结果，准备下一岗位' : '本岗位未完成，准备下一岗位', stageUpdatedAt: Date.now(),
        skipped: success || historical ? latest.skipped || [] : [...(latest.skipped || []), { ...job, error }],
      };
      const completed = nextExecution.index >= nextExecution.jobs.length;
      if (completed) current.active = null;
      else current.active.execution = nextExecution;
      // 与推进队列同一次写入，重复回执也不会推进第二次。
      current.completedPages = [...(current.completedPages || []), {
        taskId: message.taskId, sessionId: message.sessionId, claimedAt: Number(message.claimedAt),
        jobId: canonicalDeliveryJobId(job.id), index: Number(message.index), tabId: Number(tabId), success, historical, completedAt: Date.now(),
      }].slice(-100);
      return { completed };
    });
    if (advanced?.completed) {
      const next = await dispatchNextDeliveryTask();
      if (next) await wakeDeliveryConsumer(next);
      else scheduleIdleDeliveryTabCleanup();
    }
    void recordDeliveryDiagnostic({ phase: 'page-result', action: 'finish', status: advanced ? 'accepted' : 'stale', stage: advanced ? '详情页回执已保存，队列已放行下一岗位' : '结果已保存，原任务已切换', taskId: message.taskId, sessionId: message.sessionId, jobId: job.id, senderTabId: tabId });
    return { ok: true, advanced: Boolean(advanced), completed: Boolean(advanced?.completed), success, historical };
  });
  pageDeliveryResultMutation = task.catch(() => {});
  return task;
}

function openReusableDeliveryTab(url, reuseTabId, callerTabId) {
  clearTimeout(idleDeliveryTabTimer);
  idleDeliveryTabTimer = 0;
  const task = pageDeliveryTabMutation.then(async () => {
    const target = new URL(url);
    if (target.origin !== 'https://www.zhipin.com' || !target.pathname.startsWith('/job_detail/')) throw new Error('不是有效的岗位详情链接');
    const saved = await chrome.storage.local.get(PAGE_DELIVERY_TAB_KEY);
    const candidateIds = [...new Set([Number(saved[PAGE_DELIVERY_TAB_KEY]), Number(reuseTabId)].filter(id => id && id !== Number(callerTabId)))];
    for (const id of candidateIds) {
      let existing;
      try { existing = await chrome.tabs.get(id); } catch { continue; }
      let canReuse = false;
      try {
        const previous = new URL(existing.url);
        canReuse = previous.origin === target.origin
          && (id === Number(saved[PAGE_DELIVERY_TAB_KEY]) || /\/(?:job_detail\/|web\/geek\/chat)/.test(previous.pathname));
      } catch { /* 页面不可复用 */ }
      if (!canReuse) continue;
      try {
        // 保留用户当前焦点；跨所有单岗位批次复用同一个详情页。
        const updated = await chrome.tabs.update(id, { url: target.href });
        await chrome.storage.local.set({ [PAGE_DELIVERY_TAB_KEY]: updated.id });
        return { ok: true, tabId: updated.id, reused: true };
      } catch (error) {
        // 标签仍存在时导航失败应明确报错，不能不断额外开页。
        try { await chrome.tabs.get(id); } catch { continue; }
        throw error;
      }
    }
    const created = await chrome.tabs.create({ url: target.href, active: false });
    await chrome.storage.local.set({ [PAGE_DELIVERY_TAB_KEY]: created.id });
    return { ok: true, tabId: created.id, reused: false };
  });
  pageDeliveryTabMutation = task.catch(() => {});
  return task;
}
