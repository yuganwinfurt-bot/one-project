(() => {
  const node = (tag, value = '', className = '') => {
    const element = document.createElement(tag);
    element.textContent = String(value);
    if (className) element.className = className;
    return element;
  };
  const short = (value, limit) => String(value || '').slice(0, limit);
  const seconds = (value) => `${(Math.max(0, Number(value) || 0) / 1000).toFixed(1)} 秒`;
  const isApproval = (entry) => entry.kind === 'run' && entry.name?.startsWith('审批 · ');
  const kindName = (entry) => isApproval(entry) ? '操作审批' : ({ model: '模型请求', tool: '工具调用', rag: '知识库检索', run: '任务状态' }[entry.kind] || '执行记录');
  const countTools = (entries) => entries.filter((entry) => entry.kind === 'tool' && entry.status !== 'skipped').length;
  const persistedEntry = (entry) => ({
    kind: entry.kind, step: Math.max(0, Math.min(100, Number(entry.step) || 0)),
    name: short(entry.name, 128), status: entry.status || 'info',
    duration_ms: Math.min(600000, Math.max(0, Math.round(Number(entry.duration_ms) || 0))),
    detail: short(entry.detail, 240),
  });

  function panel(messageRow, entries, { running = false, model = '', elapsedMs = null, derived = false, partialTime = false } = {}) {
    const viewport = messageRow.closest('.messages');
    const nearBottom = () => viewport && viewport.scrollHeight - viewport.clientHeight - viewport.scrollTop < 48;
    const followAtMount = nearBottom();
    let firstRender = true;
    const box = node('details', '', 'tool-flow');
    box.open = running;
    const heading = node('summary', '', 'tool-flow-heading');
    const dot = node('span', '', 'tool-flow-dot');
    const headingText = node('span');
    const current = node('span', '', 'tool-flow-current');
    const toggle = node('span', '', 'tool-flow-toggle');
    heading.append(dot, headingText, current, toggle);
    const content = node('div', '', 'tool-flow-content');
    const caption = node('p', model ? `当前模型：${model}。执行记录来自实际请求和工具返回。` : '执行记录来自已保存的工具调用和返回状态。', 'tool-flow-caption');
    const list = node('ol', '', 'tool-flow-list');
    list.setAttribute('aria-label', '工具执行步骤');
    const empty = node('p', '', 'tool-flow-note');
    content.append(caption, list, empty);
    box.append(heading, content);
    box.setAttribute('aria-label', '工具执行流程');
    messageRow.querySelector('.message-body')?.prepend(box);
    let timers = [];

    const renderHeading = () => {
      const failed = entries.some((entry) => entry.status === 'error');
      const active = entries.find((entry) => entry.uiState === 'waiting') || entries.find((entry) => entry.uiState === 'running');
      const label = running ? (active?.uiState === 'waiting' ? '等待确认' : '处理中') : failed ? '存在失败步骤' : '已处理';
      headingText.textContent = `${label} · ${entries.length} 步 · ${countTools(entries)} 次工具调用${elapsedMs != null ? ` · ${partialTime ? '累计记录 ' : ''}${seconds(elapsedMs)}` : ' · 耗时未记录'}`;
      current.textContent = running && active ? active.name || kindName(active) : '';
      toggle.textContent = box.open ? '收起 ⌃' : '展开 ›';
      box.classList.toggle('is-running', running);
      box.classList.toggle('has-error', failed);
      empty.hidden = running || countTools(entries) > 0;
      empty.textContent = derived ? '' : '本轮未调用工具。';
      if (derived) empty.hidden = true;
      for (const { element, entry } of timers) element.textContent = entry.uiState === 'running' || entry.uiState === 'waiting'
        ? seconds(performance.now() - entry.startedAt) : seconds(entry.duration_ms);
    };
    const render = () => {
      const followChat = firstRender ? followAtMount : nearBottom();
      firstRender = false;
      const bottom = list.scrollHeight - list.clientHeight - list.scrollTop < 32;
      const previousTop = list.scrollTop;
      const fragment = document.createDocumentFragment();
      timers = [];
      for (const entry of entries) {
        const state = entry.uiState || entry.status;
        const row = node('li', '', `tool-flow-step flow-${state}`);
        const stateLabel = { running: '执行中', waiting: '等待确认', ok: '成功', error: '失败', skipped: '跳过', info: '记录' }[state] || '记录';
        const icon = node('span', state === 'ok' ? '✓' : state === 'error' ? '×' : state === 'skipped' ? '—' : state === 'info' ? '•' : '', 'tool-flow-state');
        icon.setAttribute('aria-label', stateLabel);
        const body = node('div', '', 'tool-flow-step-body');
        const title = node('div', '', 'tool-flow-step-title');
        title.append(node('b', kindName(entry), `tool-flow-kind kind-${isApproval(entry) ? 'approval' : entry.kind}`));
        if (entry.name) title.append(node('code', isApproval(entry) ? entry.name.slice(5) : entry.name));
        if (entry.step) title.append(node('small', `第 ${entry.step} 轮`));
        title.append(node('span', stateLabel, 'tool-flow-step-status'));
        const time = node('time');
        if (entry.uiState || entry.duration_ms > 0) {
          timers.push({ element: time, entry }); title.append(time);
        }
        body.append(title);
        if (entry.detail) body.append(node('p', entry.detail));
        row.append(icon, body); fragment.append(row);
      }
      list.replaceChildren(fragment);
      renderHeading();
      requestAnimationFrame(() => {
        if (box.open) list.scrollTop = bottom ? list.scrollHeight : previousTop;
        if (followChat && viewport) viewport.scrollTop = viewport.scrollHeight;
      });
    };
    box.addEventListener('toggle', renderHeading);
    render();
    return { box, render, tick: (elapsed) => { elapsedMs = elapsed; renderHeading(); }, finish: (elapsed) => { running = false; elapsedMs = elapsed; render(); } };
  }

  function create(messageRow, model) {
    const entries = [];
    const started = performance.now();
    const id = crypto.randomUUID().replaceAll('-', '');
    const view = panel(messageRow, entries, { running: true, model, elapsedMs: 0 });
    const approvals = new Map();
    let closed = false;
    let finishedElapsed = null;
    let currentTool = null;
    const begin = (entry) => {
      const value = { ...entry, status: 'info', uiState: 'running', startedAt: performance.now(), duration_ms: 0 };
      entries.push(value);
      if (entry.kind === 'tool') currentTool = value;
      view.render(); return value;
    };
    const end = (entry, status = 'ok', detail = '') => {
      if (!entry) return;
      Object.assign(entry, { status, detail: short(detail, 240), duration_ms: Math.round(performance.now() - entry.startedAt) });
      delete entry.uiState;
      if (entry === currentTool) {
        for (const approval of approvals.values()) if (approval.uiState) {
          Object.assign(approval, { status: status === 'ok' ? 'ok' : 'error', detail: status === 'ok' ? '审批已完成。' : '工具请求已结束，确认未完成或已超时。', duration_ms: Math.round(performance.now() - approval.startedAt) });
          delete approval.uiState;
        }
        currentTool = null;
      }
      view.render();
    };
    const record = (entry) => { entries.push({ ...entry, duration_ms: entry.duration_ms || 0 }); view.render(); };
    const approvalPending = (item) => {
      if (closed || approvals.has(item.id)) return;
      const entry = begin({ kind: 'run', name: `审批 · ${item.name || '操作'}`, detail: '需要你确认后才能继续执行。' });
      entry.uiState = 'waiting'; approvals.set(item.id, entry);
      if (currentTool) currentTool.uiState = 'waiting';
      view.render();
    };
    const approvalDecision = (approvalId, approved, all = false) => {
      if (closed) return;
      for (const [key, entry] of approvals) if ((all || key === approvalId) && entry.uiState) {
        end(entry, approved ? 'ok' : 'skipped', approved ? (all ? '已批准本次任务的后续操作。' : '已允许这次操作。') : '你拒绝了这次操作，等待工具返回拒绝结果。');
      }
      if (currentTool) currentTool.uiState = 'running';
      view.render();
    };
    const timer = setInterval(() => view.tick(performance.now() - started), 500);
    return {
      entries, begin, end, record, approvalPending, approvalDecision,
      finish(error = false) {
        if (closed) return;
        for (const entry of entries) if (entry.uiState) end(entry, 'error', '本轮请求已中断，请检查模型或工具服务。');
        const tools = countTools(entries);
        record({ kind: 'run', name: '结束', status: error ? 'error' : 'ok', detail: error ? '本轮执行中断，已保留执行记录。' : tools ? `已生成最终回复，本轮发起 ${tools} 次工具调用。` : '本轮未调用工具，模型直接回复。' });
        closed = true; clearInterval(timer);
        finishedElapsed = Math.round(performance.now() - started);
        view.finish(finishedElapsed);
      },
      snapshot() { return { id, model, elapsed_ms: finishedElapsed ?? Math.round(performance.now() - started), entries: entries.slice(-100).map(persistedEntry) }; },
    };
  }

  function mergeTraces(local = [], server = []) {
    const byContent = new Map();
    for (const trace of [...local, ...server]) {
      if (!trace || !Array.isArray(trace.entries) || !Number.isInteger(trace.turn_index)) continue;
      const normalized = { ...trace, model: short(trace.model, 128), entries: trace.entries.map(persistedEntry) };
      const key = JSON.stringify([trace.turn_index, normalized.model, normalized.entries]);
      byContent.set(key, normalized);
    }
    return [...byContent.values()];
  }
  function renderTrace(row, traces) {
    if (!traces.length) return;
    const entries = traces.flatMap((trace) => trace.entries || []);
    const recordedElapsed = traces.reduce((sum, trace) => sum + (Number(trace.elapsed_ms) || 0), 0);
    const duration = recordedElapsed || entries.filter((entry) => ['model', 'rag', 'tool'].includes(entry.kind)).reduce((sum, entry) => sum + (Number(entry.duration_ms) || 0), 0);
    panel(row, entries, { model: traces.map((trace) => trace.model).filter(Boolean).join(' / '), elapsedMs: duration || null,
      derived: traces.every((trace) => trace.derived), partialTime: !recordedElapsed && duration > 0 });
  }
  function toolSummary(result) {
    if (!result?.ok) return '工具返回失败，结果已交回模型处理。';
    const data = result.data;
    const facts = [];
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      for (const [key, label] of [['exit_code', '退出码'], ['count', '条数'], ['total', '总数'], ['matched_count', '匹配数']]) {
        if (Number.isFinite(data[key])) facts.push(`${label} ${data[key]}`);
      }
      for (const [key, label] of [['files', '文件'], ['matches', '匹配项'], ['rows', '数据行'], ['items', '条目']]) {
        if (Array.isArray(data[key])) facts.push(`${label} ${data[key].length} 个`);
      }
    } else if (Array.isArray(data)) facts.push(`返回 ${data.length} 项`);
    return `工具执行完成${facts.length ? `：${facts.join('，')}` : ''}。结果已交回模型。`;
  }
  window.YuganToolFlow = { create, renderTrace, mergeTraces, toolSummary };
})();
