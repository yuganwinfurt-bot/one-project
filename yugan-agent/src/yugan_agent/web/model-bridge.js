(() => {
  const status = document.getElementById('status');
  const nonce = window.location.hash.slice(1);
  const agentBase = new URL('../', window.location.href);
  const agentApi = (path) => new URL(path, agentBase);
  const trustedOrigin = (origin) => {
    if (origin === window.location.origin) return true;
    try {
      const target = new URL(origin);
      if (['localhost', '127.0.0.1', '[::1]'].includes(target.hostname) && ['4173', '5173', '8030'].includes(target.port)) return true;
      return window.location.protocol === 'https:' && target.protocol === 'https:' && target.hostname === window.location.hostname && !target.port;
    } catch { return false; }
  };
  let handlingRequest = false;
  window.addEventListener('message', async (event) => {
    const requestType = event.data?.type;
    const trustedSender = event.source === window.opener || (window.parent !== window && event.source === window.parent);
    if (handlingRequest || !trustedSender || !trustedOrigin(event.origin)
      || !['yugan-request-active-model', 'yugan-request-model-profiles'].includes(requestType)
      || event.data?.nonce !== nonce) return;
    handlingRequest = true;
    try {
      const auth = await fetch(agentApi('api/auth/status'), { credentials: 'same-origin', cache: 'no-store' }).then((response) => response.json());
      const stored = JSON.parse(localStorage.getItem(`yugan-model-profiles:${auth.subject}`) || '{}');
      if (requestType === 'yugan-request-active-model') {
        const profile = (stored.models || []).find((item) => item.id === stored.active_id);
        if (!profile) throw new Error('Agent 尚未选择模型');
        event.source.postMessage({ type: 'yugan-active-model', nonce, profile }, event.origin);
      } else {
        const profiles = (Array.isArray(stored.models) ? stored.models : [])
          .filter((item) => item && item.id && item.model && item.endpoint)
          .map((item) => ({
            id: item.id, name: item.name, endpoint: item.endpoint, model: item.model,
            api_key: item.api_key || '', vendor: item.vendor || '兼容接口',
            provider: item.provider || 'compatible', mode: item.mode || 'api',
            effort_supported: Boolean(item.effort_supported),
          }));
        let serverModels = [];
        const serverApiToken = sessionStorage.getItem('yugan-api-token') || '';
        try {
          const response = await fetch(agentApi('api/models/server-ollama'), {
            credentials: 'same-origin', cache: 'no-store',
            headers: serverApiToken ? { Authorization: `Bearer ${serverApiToken}` } : {},
          });
          if (response.ok) {
            const result = await response.json();
            serverModels = Array.isArray(result.models) ? result.models.filter((name) => typeof name === 'string') : [];
          }
        } catch { /* Personal API profiles remain available if server Ollama is offline. */ }
        event.source.postMessage({ type: 'yugan-model-profiles', nonce, profiles, server_models: serverModels, server_api_token: serverApiToken }, event.origin);
      }
      status.textContent = 'Agent 模型已安全发送到打开此窗口的 RAG 页面。';
      if (window.parent === window && window.opener) window.setTimeout(() => window.close(), 350);
    } catch (error) {
      const message = error.message || '读取 Agent 模型失败';
      handlingRequest = false;
      status.textContent = message;
      const errorType = requestType === 'yugan-request-active-model' ? 'yugan-active-model-error' : 'yugan-model-profiles-error';
      try { event.source.postMessage({ type: errorType, nonce, message }, event.origin); } catch { /* opener may have closed */ }
      if (window.parent === window && window.opener) window.setTimeout(() => window.close(), 1500);
    }
  });
  if (!window.opener && window.parent === window) status.textContent = '请从 RAG 页面打开此窗口。';
})();

