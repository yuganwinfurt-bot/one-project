const localHost = ["127.0.0.1", "localhost", "[::1]"].includes(window.location.hostname);
const publicBasePath = /^\/rag(?:\/|$)/.test(window.location.pathname) ? "/rag" : "";
const defaultApiBase = localHost ? "http://127.0.0.1:8000" : `${window.location.origin}${publicBasePath}`;
const API = (import.meta.env.VITE_API_URL || defaultApiBase).replace(/\/+$/, "");

export async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, { credentials: "include", ...options });
  if (!response.ok) {
    let detail = `请求失败（${response.status}）`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch { /* keep the status message */ }
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export { API };
