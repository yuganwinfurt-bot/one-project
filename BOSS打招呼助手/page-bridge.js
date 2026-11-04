(() => {
  'use strict';

  const MAX_RESPONSE_BYTES = 2 * 1024 * 1024;
  const MAX_META_ENTRIES = 500;
  const jobMeta = new Map();

  function isJobDataUrl(value) {
    try {
      const url = new URL(String(value || ''), location.href);
      return url.origin === location.origin
        && /\/wapi\/zpgeek\//i.test(url.pathname)
        && /(job|search|position|recommend)/i.test(url.pathname);
    } catch { return false; }
  }

  function rememberMeta(value) {
    const encryptJobId = value.encryptJobId || value.encryptJobID;
    const securityId = value.securityId || value.securityID;
    if (!encryptJobId || !securityId) return;
    const meta = {
      encryptJobId: String(encryptJobId), securityId: String(securityId),
      encryptBossId: String(value.encryptBossId || ''),
      bossId: Number(value.bossId || 0), bossSource: Number(value.bossSource || 0),
      salary: String(value.salaryDesc || value.salaryText || value.salaryRange || value.salary || '')
    };
    const aliases = [encryptJobId, value.jobId, value.jobID, value.positionId, value.positionID]
      .filter(item => item !== undefined && item !== null && String(item));
    for (const alias of aliases) {
      const key = String(alias);
      jobMeta.delete(key);
      jobMeta.set(key, meta);
    }
    while (jobMeta.size > MAX_META_ENTRIES) jobMeta.delete(jobMeta.keys().next().value);
  }

  function collectJobMeta(root) {
    const stack = [{ value: root, depth: 0 }];
    let visited = 0;
    while (stack.length && visited < 12000) {
      const { value, depth } = stack.pop();
      visited += 1;
      if (!value || typeof value !== 'object' || depth > 10) continue;
      if (!Array.isArray(value)) rememberMeta(value);
      for (const key in value) {
        if (!Object.prototype.hasOwnProperty.call(value, key)) continue;
        stack.push({ value: value[key], depth: depth + 1 });
        if (stack.length + visited >= 12000) break;
      }
    }
  }

  function inspectResponseText(text) {
    if (!text || text.length > MAX_RESPONSE_BYTES
      || !text.includes('securityId') || !text.includes('encryptJobId')) return;
    try { collectJobMeta(JSON.parse(text)); } catch { /* 非 JSON 响应忽略 */ }
  }

  async function inspectFetchResponse(response) {
    const size = Number(response.headers?.get('content-length') || 0);
    if (size > MAX_RESPONSE_BYTES || !response.body) return;
    const reader = response.clone().body.getReader();
    const chunks = [];
    let total = 0;
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        total += value.byteLength;
        if (total > MAX_RESPONSE_BYTES) {
          await reader.cancel();
          return;
        }
        chunks.push(value);
      }
      const bytes = new Uint8Array(total);
      let offset = 0;
      for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
      inspectResponseText(new TextDecoder().decode(bytes));
    } catch { /* 页面请求继续正常使用，扩展只放弃这份元数据 */ }
  }

  const nativeFetch = window.fetch;
  window.fetch = function (input, ...args) {
    const inspect = isJobDataUrl(typeof input === 'string' ? input : input?.url);
    return nativeFetch.call(this, input, ...args).then(response => {
      if (inspect && response.ok) void inspectFetchResponse(response);
      return response;
    });
  };

  const nativeOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...args) {
    const inspect = isJobDataUrl(url);
    if (inspect) this.addEventListener('load', () => {
      try {
        const size = Number(this.getResponseHeader('Content-Length') || 0);
        if (size > MAX_RESPONSE_BYTES) return;
        if (this.responseType === 'json') {
          collectJobMeta(this.response);
          return;
        }
        if (this.responseType && this.responseType !== 'text') return;
        inspectResponseText(this.responseText);
      } catch { /* 非文本响应忽略 */ }
    });
    return nativeOpen.call(this, method, url, ...args);
  };

  // content script 运行在 isolated world，不能直接读取 BOSS 页面注入的 _PAGE。
  // 仅在扩展主动请求时返回当前页会话所需的 token 与 uid。
  window.addEventListener('BQA_PAGE_AUTH_REQUEST', () => {
    const page = window._PAGE || {};
    window.dispatchEvent(new CustomEvent('BQA_PAGE_AUTH_RESPONSE', {
      detail: {
        token: page.token || '',
        uid: Number(page.uid || page.userId || 0),
        encryptedUid: String(page.encryptUserId || ''),
        bst: window.Cookie?.get?.('bst') || ''
      }
    }));
  });

  window.addEventListener('BQA_JOB_META_REQUEST', event => {
    const jobId = String(event.detail?.jobId || '');
    window.dispatchEvent(new CustomEvent('BQA_JOB_META_RESPONSE', {
      detail: { requestId: event.detail?.requestId, job: jobMeta.get(jobId) || null }
    }));
  });

  function jobVue() {
    const element = document.querySelector('#wrap .page-job-wrapper,.job-recommend-main,.page-jobs-main');
    return element?.__vue__ || element?.__vueParentComponent?.proxy || null;
  }

  window.addEventListener('BQA_CHANGE_JOB_PAGE_REQUEST', event => {
    const requestId = event.detail?.requestId;
    const direction = event.detail?.direction;
    const vm = jobVue();
    const action = vm?.searchJobAction || vm?.onSearch || vm?.pageChangeAction;
    const currentPage = Number(vm?.pageVo?.page || 1);
    const targetPage = direction === 'prev' ? Math.max(1, currentPage - 1) : currentPage + 1;
    if (!vm || typeof action !== 'function' || (direction === 'prev' && currentPage <= 1)) {
      window.dispatchEvent(new CustomEvent('BQA_CHANGE_JOB_PAGE_RESPONSE', {
        detail: { requestId, ok: false }
      }));
      return;
    }
    Promise.resolve(action(targetPage)).then(() => {
      window.dispatchEvent(new CustomEvent('BQA_CHANGE_JOB_PAGE_RESPONSE', {
        detail: { requestId, ok: true, page: targetPage }
      }));
    }).catch(error => {
      window.dispatchEvent(new CustomEvent('BQA_CHANGE_JOB_PAGE_RESPONSE', {
        detail: { requestId, ok: false, error: String(error?.message || error) }
      }));
    });
  });
})();
